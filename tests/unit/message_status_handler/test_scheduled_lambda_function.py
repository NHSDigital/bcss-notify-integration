import json
import scheduled_lambda_function as lambda_function
from unittest.mock import patch


@patch("batch_fetcher.fetch_batch_ids")
@patch("comms_management.get_read_messages")
@patch("message_status_recorder.record_message_statuses")
def test_lambda_handler(mock_record_message_statuses, mock_get_read_messages, mock_fetch_batch_ids):
    mock_fetch_batch_ids.return_value = ["12345"]
    mock_get_read_messages.return_value = [{"message_id": "123", "status": "read"}]
    mock_record_message_statuses.return_value = {"status": "success"}

    response = lambda_function.lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "message": "Message status handler finished",
        "data": {
            "12345": {
                "notification_status": [{"message_id": "123", "status": "read"}],
                "bcss_response": {"status": "success"},
            }
        }
    }


@patch("batch_fetcher.fetch_batch_ids")
@patch("comms_management.get_read_messages")
def test_lambda_handler_no_messages(mock_get_read_messages, mock_fetch_batch_ids):
    mock_fetch_batch_ids.return_value = ["12345"]
    mock_get_read_messages.return_value = []

    response = lambda_function.lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "message": "Message status handler finished",
        "data": {
            "12345": {
                "notification_status": [],
            }
        }
    }


@patch("batch_fetcher.fetch_batch_ids")
@patch("comms_management.get_read_messages")
def test_lambda_handler_exception(mock_get_read_messages, mock_fetch_batch_ids):
    mock_fetch_batch_ids.return_value = ["12345"]
    mock_get_read_messages.side_effect = Exception("Test exception")

    response = lambda_function.lambda_handler({}, None)

    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal Server Error: Test exception"}


@patch("batch_fetcher.fetch_batch_ids")
@patch("comms_management.get_read_messages")
@patch("message_status_recorder.record_message_statuses")
def test_lambda_handler_with_bcss_error(mock_record_message_statuses, mock_get_read_messages, mock_fetch_batch_ids):
    mock_fetch_batch_ids.return_value = ["12345"]
    mock_get_read_messages.return_value = [{"message_id": "123", "status": "read"}]
    mock_record_message_statuses.side_effect = Exception("BCSS error")

    response = lambda_function.lambda_handler({}, None)

    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {
        "message": "Internal Server Error: BCSS error",
    }
