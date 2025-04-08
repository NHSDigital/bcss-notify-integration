import json
import lambda_function
from unittest.mock import patch


def test_lambda_handler():
    with patch("comms_management.get_read_messages") as mock_get_read_messages:
        with patch("message_status_recorder.record_message_statuses") as mock_record_message_statuses:
            mock_get_read_messages.return_value = [{"message_id": "123", "status": "read"}]
            mock_record_message_statuses.return_value = {"status": "success"}

            response = lambda_function.lambda_handler({"batch_id": "12345"}, None)

            assert response["statusCode"] == 200
            assert json.loads(response["body"]) == {
                "message": "Message status updates successful",
                "data": [{"message_id": "123", "status": "read"}],
                "bcss_response": {"status": "success"},
            }


def test_lambda_handler_no_messages():
    with patch("comms_management.get_read_messages") as mock_get_read_messages:
        mock_get_read_messages.return_value = []

        response = lambda_function.lambda_handler({"batch_id": "12345"}, None)

        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == {"message": "No messages with read status found."}


def test_lambda_handler_exception():
    with patch("comms_management.get_read_messages") as mock_get_read_messages:
        mock_get_read_messages.side_effect = Exception("Test exception")

        response = lambda_function.lambda_handler({"batch_id": "12345"}, None)

        assert response["statusCode"] == 500
        assert json.loads(response["body"]) == {"message": "Internal Server Error: Test exception"}
