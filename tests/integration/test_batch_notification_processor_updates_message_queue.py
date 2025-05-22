import batch_processor
import dotenv
import os
import pytest
import requests_mock
import lambda_function
from jsonschema import ValidationError, validate
from unittest.mock import Mock
import uuid

dotenv.load_dotenv(".env.test")


def test_batch_notification_processor_updates_message_queue(recipient_data, helpers):
    """Test that the batch notification processor updates the BCSS message queue correctly."""
    batch_id_1 = str(uuid.uuid4())
    batch_id_2 = str(uuid.uuid4())

    message_references = [r[1] for r in recipient_data]
    batch_processor.generate_message_reference = Mock(side_effect=message_references)
    batch_processor.generate_batch_id = Mock(side_effect=[batch_id_1, batch_id_2, str(uuid.uuid4())])

    helpers.seed_message_queue(batch_id_1, recipient_data[:3], 1)
    helpers.seed_message_queue(batch_id_2, recipient_data[3:], 2)

    with requests_mock.Mocker() as rm:
        rm.post(
            f"{os.getenv('COMMGT_BASE_URL')}/message/batch",
            status_code=201,
            json={"data": {"id": "batch_id"}},
        )

        lambda_function.lambda_handler({}, {})

    with helpers.cursor() as cur:
        cur.execute(
            """
            SELECT batch_id, nhs_number, message_id, message_status
            FROM v_notify_message_queue
            WHERE batch_id = :batch_id
            ORDER BY batch_id
            """,
            batch_id=batch_id_1
        )
        results = cur.fetchall()

        assert len(results) == 3

        for idx, result in enumerate(results):
            recipient = recipient_data[idx]
            assert result == (batch_id_1, recipient[0], recipient[1], "sending")

        cur.execute(
            """
            SELECT batch_id, nhs_number, message_id, message_status
            FROM v_notify_message_queue
            WHERE batch_id = :batch_id
            ORDER BY batch_id
            """,
            batch_id=batch_id_2
        )
        results = cur.fetchall()

        assert len(results) == 2
        assert results[0] == (batch_id_2, recipient_data[3][0], recipient_data[3][1], "sending")
        assert results[1] == (batch_id_2, recipient_data[4][0], recipient_data[4][1], "sending")


def test_batch_notification_processor_payload(recipient_data, nhs_notify_message_batch_schema, helpers):
    """Test that the batch notification processor sends the correct payload to the CMAPI."""
    batch_id = str(uuid.uuid4())
    message_references = [r[1] for r in recipient_data]
    helpers.seed_message_queue(batch_id, recipient_data)
    batch_processor.generate_message_reference = Mock(side_effect=message_references)
    batch_processor.generate_batch_id = Mock(side_effect=[batch_id, str(uuid.uuid4())])

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            f"{os.getenv('COMMGT_BASE_URL')}/message/batch",
            status_code=201,
            json={"data": {"id": "batch_id"}},
        )

        lambda_function.lambda_handler({}, {})

    assert adapter.called
    assert adapter.call_count == 1

    try:
        validate(instance=adapter.last_request.json(), schema=nhs_notify_message_batch_schema)
    except ValidationError as e:
        pytest.fail(f"Validation failed: {e}")
    except KeyError as e:
        pytest.fail(f"Invalid key for body: {e}")

    response_json = adapter.last_request.json()

    assert response_json["data"]["attributes"]["messageBatchReference"] == batch_id
    assert (
        response_json["data"]["attributes"]["routingPlanId"]
        == "e43a7d31-a287-485e-b1c2-f53cebbefba3"
    )

    for idx, msg in enumerate(response_json["data"]["attributes"]["messages"]):
        assert msg["recipient"]["nhsNumber"] == recipient_data[idx][0]
        assert msg["messageReference"] == recipient_data[idx][1]
