import boto3
from contextlib import contextmanager
import dotenv
import json
from lambda_function import lambda_handler
import oracledb
import os
import pytest
from recipient import Recipient
import requests_mock
from unittest.mock import Mock, patch


dotenv.load_dotenv(".env.test")


@pytest.fixture(autouse=True)
def reset_db():
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE notify_message_queue")
        cursor.execute("TRUNCATE TABLE notify_message_batch")
        conn.commit()
        cursor.close()


def batch_id():
    return "d3f31ae4-1532-46df-b121-3503db6b32d6"

@pytest.fixture
def recipients():
    return [
        Recipient(("9449304424", "51c33851-5ad6-499d-91f0-38618fb15fcd")),
        Recipient(("9449305552", "e6c4a2d8-780e-4d28-a5e5-ee89be535e22")),
        Recipient(("9449306621", "83452037-abe2-4b34-acf9-7ba2015cd84b")),
        Recipient(("9449306613", "e5fa43a0-37ba-45f6-a4dd-2d9d8b6f66b2")),
        Recipient(("9449306605", "360641b3-3258-4076-8d23-3582fcf9ba91")),
    ]

@contextmanager
def connection():
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    dsn = f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_SID')}"
    conn = oracledb.connect(user=user, password=password, dsn=dsn)
    yield conn


def seed_message_queue(recipients):
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notify_message_batch (batch_id, message_definition_id, batch_status)
            VALUES (:batch_id, 1, 'new')
        """, batch_id=batch_id())
        for recipient in recipients:
            cursor.execute(
                """
                INSERT INTO notify_message_queue (
                    nhs_number, message_id, event_status_id, message_definition_id, message_status,
                    subject_id, event_id, pio_id
                ) VALUES (:nhs_number, :message_reference, 11197, 1, 'new', 1, 1, 1)
                """,
                nhs_number=recipient.nhs_number,
                message_reference=recipient.message_id
            )

        conn.commit()
        cursor.close()

@patch("lambda_function.generate_batch_id", return_value=batch_id())
def test_batch_notification_processor_updates_message_queue(mock_generate_batch_id, recipients):
    secrets_client = Mock()
    secret_string = json.dumps({
        "username": os.getenv("DATABASE_USER"),
        "password": os.getenv("DATABASE_PASSWORD")
    })
    secrets_client.get_secret_value.return_value = {"SecretString": secret_string}
    boto3.client = Mock(return_value=secrets_client)
    with patch("lambda_function.BatchProcessor.generate_message_reference", 
               side_effect=[r.message_id for r in recipients]):

        seed_message_queue(recipients)

        with requests_mock.Mocker() as rm:
            rm.post(
                f"{os.getenv('COMMGT_BASE_URL')}/api/message/batch",
                status_code=201,
                json={"data": {"id": "batch_id"}},
            )

            lambda_handler({}, {})

    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nhs_number, message_id, message_status FROM v_notify_message_queue WHERE batch_id = :batch_id",
            batch_id=batch_id()
        )
        results = cursor.fetchall()
        cursor.close()

    assert len(results) == 5
    for idx, result in enumerate(results):
        recipient = recipients[idx]
        assert result == (recipient.nhs_number, recipient.message_id, "SENDING")
