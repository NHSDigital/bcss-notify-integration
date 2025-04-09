from batch_processor import BatchProcessor
import dotenv
import lambda_function
import os
import requests_mock
from unittest.mock import Mock


dotenv.load_dotenv(".env.test")


def test_batch_notification_processor_updates_message_queue(batch_id, recipient_data, helpers):
    lambda_function.generate_batch_id = Mock(return_value=batch_id)
    message_references = [r[1] for r in recipient_data]
    helpers.seed_message_queue(batch_id, recipient_data)
    BatchProcessor.generate_message_reference = Mock(side_effect=message_references)

    with requests_mock.Mocker() as rm:
        rm.post(
            f"{os.getenv('COMMGT_BASE_URL')}/api/message/batch",
            status_code=201,
            json={"data": {"id": "batch_id"}},
        )

        lambda_function.lambda_handler({}, {})

    with helpers.cursor() as cur:
        cur.execute(
            "SELECT nhs_number, message_id, message_status FROM v_notify_message_queue WHERE batch_id = :batch_id",
            batch_id=batch_id
        )
        results = cur.fetchall()

    assert len(results) == 5
    for idx, result in enumerate(results):
        recipient = recipient_data[idx]
        assert result == (recipient[0], recipient[1], "SENDING")


def test_batch_notification_processor_payload(batch_id, recipient_data, helpers):
    lambda_function.generate_batch_id = Mock(return_value=batch_id)
    message_references = [r[1] for r in recipient_data]
    helpers.seed_message_queue(batch_id, recipient_data)
    BatchProcessor.generate_message_reference = Mock(side_effect=message_references)

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
