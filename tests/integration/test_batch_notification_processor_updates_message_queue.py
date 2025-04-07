import boto3
from contextlib import contextmanager
import dotenv
import json
import lambda_function
import oracledb
import os
import pytest
import requests_mock
from unittest.mock import Mock, patch


dotenv.load_dotenv(".env.test")


@pytest.fixture(autouse=True)
def reset_db():
    with cursor() as cur:
        cur.execute("TRUNCATE TABLE notify_message_queue")
        cur.execute("TRUNCATE TABLE notify_message_batch")
        cur.connection.commit()


@pytest.fixture
def batch_id():
    return "d3f31ae4-1532-46df-b121-3503db6b32d6"


@pytest.fixture
def recipient_data():
    return [
        ("9449304424", "51c33851-5ad6-499d-91f0-38618fb15fcd"),
        ("9449305552", "e6c4a2d8-780e-4d28-a5e5-ee89be535e22"),
        ("9449306621", "83452037-abe2-4b34-acf9-7ba2015cd84b"),
        ("9449306613", "e5fa43a0-37ba-45f6-a4dd-2d9d8b6f66b2"),
        ("9449306605", "360641b3-3258-4076-8d23-3582fcf9ba91"),
    ]


@contextmanager
def cursor():
    conn = oracledb.connect(
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"), 
        dsn=f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_SID')}"
    )
    try:
        yield conn.cursor()
    finally:
        conn.close()


def seed_message_queue(batch_id, recipient_data):
    with cursor() as cur:
        cur.execute("""
            INSERT INTO notify_message_batch (batch_id, message_definition_id, batch_status)
            VALUES (:batch_id, 1, 'new')
        """, batch_id=batch_id)
        for recipient in recipient_data:
            cur.execute(
                """
                INSERT INTO notify_message_queue (
                    nhs_number, message_id, event_status_id, message_definition_id, message_status,
                    subject_id, event_id, pio_id
                ) VALUES (:nhs_number, :message_reference, 11197, 1, 'new', 1, 1, 1)
                """,
                nhs_number=recipient[0],
                message_reference=recipient[1]
            )

        cur.connection.commit()

def test_batch_notification_processor_updates_message_queue(batch_id, recipient_data):
    lambda_function.generate_batch_id = Mock(return_value=batch_id)
    secrets_client = Mock()
    secret_string = json.dumps({
        "username": os.getenv("DATABASE_USER"),
        "password": os.getenv("DATABASE_PASSWORD")
    })
    secrets_client.get_secret_value.return_value = {"SecretString": secret_string}
    boto3.client = Mock(return_value=secrets_client)
    message_references = [r[1] for r in recipient_data]

    with patch("lambda_function.BatchProcessor.generate_message_reference", side_effect=message_references):

        seed_message_queue(batch_id, recipient_data)

        with requests_mock.Mocker() as rm:
            rm.post(
                f"{os.getenv('COMMGT_BASE_URL')}/api/message/batch",
                status_code=201,
                json={"data": {"id": "batch_id"}},
            )

            lambda_function.lambda_handler({}, {})

    with cursor() as cur:
        cur.execute(
            "SELECT nhs_number, message_id, message_status FROM v_notify_message_queue WHERE batch_id = :batch_id",
            batch_id=batch_id
        )
        results = cur.fetchall()

    assert len(results) == 5
    for idx, result in enumerate(results):
        recipient = recipient_data[idx]
        assert result == (recipient[0], recipient[1], "SENDING")


def test_batch_notification_processor_payload(batch_id, recipient_data):
    lambda_function.generate_batch_id = Mock(return_value=batch_id)
    secrets_client = Mock()
    secret_string = json.dumps({
        "username": os.getenv("DATABASE_USER"),
        "password": os.getenv("DATABASE_PASSWORD")
    })
    secrets_client.get_secret_value.return_value = {"SecretString": secret_string}
    boto3.client = Mock(return_value=secrets_client)
    message_references = [r[1] for r in recipient_data]

    with patch("lambda_function.BatchProcessor.generate_message_reference", side_effect=message_references):

        seed_message_queue(batch_id, recipient_data)

        with requests_mock.Mocker() as rm:
            adapter = rm.post(
                f"{os.getenv('COMMGT_BASE_URL')}/api/message/batch",
                status_code=201,
                json={"data": {"id": "batch_id"}},
            )

            lambda_function.lambda_handler({}, {})

        assert adapter.called
        assert adapter.call_count == 1
        response_json = adapter.last_request.json()

        assert response_json["data"]["attributes"]["messageBatchReference"] == batch_id
        assert response_json["data"]["attributes"]["routingPlanId"] == "c3f31ae4-1532-46df-b121-3503db6b32d6"

        for idx, msg in enumerate(response_json["data"]["attributes"]["messages"]):
            assert msg["recipient"]["nhsNumber"] == recipient_data[idx][0]
            assert msg["messageReference"] == recipient_data[idx][1]
