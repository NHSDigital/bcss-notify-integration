from unittest.mock import Mock, patch
from lambda_function import lambda_handler, secrets_client, get_secret, db_config
from recipient import Recipient
from batch_notification_processor.batch_processor import BatchProcessor
from batch_notification_processor import get_recipients
import boto3
import logging


@patch(
    "batch_notification_processor.lambda_function.generate_batch_id",
    return_value="b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3",
)
@patch("batch_notification_processor.lambda_function.Scheduler", autospec=True)
@patch(
    "batch_notification_processor.lambda_function.CommunicationManagement",
    autospec=True,
)
@patch("batch_notification_processor.lambda_function.BatchProcessor", autospec=True)
def test_lambda_handler(
    mock_batch_processor,
    mock_communication_management,
    mock_scheduler,
    generate_batch_id,
    mock_get_recipients,
    mock_get_connection,
    mock_boto3_client,
    monkeypatch,
):
    monkeypatch.setenv("host", "host")
    monkeypatch.setenv("port", "port")
    monkeypatch.setenv("sid", "sid")

    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": '{"username": "user", "password": "pass"}'
    }
    boto3.client = Mock(return_value=secrets_client)

    recipient = Mock()
    recipient.message_id = "message_reference_0"
    recipient.message_status = "REQUESTED"
    recipient.phone_number = "1234567890"

    routing_plan_id = "c2c2c2c2-c2c2-c2c2c2c2-c2c2c2c2c2c2"
    mock_batch_processor.return_value.get_routing_plan_id = Mock(
        return_value=routing_plan_id
    )
    mock_batch_processor.return_value.get_recipients = Mock(return_value=[recipient])
    mock_batch_processor.return_value.mark_batch_as_sent = Mock()

    mock_response = Mock()
    mock_response.status_code = 201
    mock_communication_management.return_value.send_batch_message = Mock(
        return_value=mock_response
    )

    lambda_handler({}, {})

    mock_batch_processor.assert_called_once_with("b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3")

    mock_batch_processor.return_value.get_routing_plan_id.assert_called_once()
    mock_batch_processor.return_value.get_recipients.assert_called_once()

    mock_communication_management.assert_called_once()
    mock_communication_management.return_value.send_batch_message.assert_called_once_with(
        "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3", routing_plan_id, [recipient]
    )

    # Ensure the batch is marked as sent
    mock_batch_processor.return_value.mark_batch_as_sent.assert_called_once_with(
        [recipient]
    )

    # Ensure the status check was scheduled
    mock_scheduler.return_value.schedule_status_check.assert_called_once()


def test_secrets_client(monkeypatch):
    boto3.client = Mock()
    monkeypatch.setenv("region_name", "us-east-1")

    assert secrets_client() == boto3.client("secretsmanager", region_name="us-east-1")


def test_get_secret():
    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": '{"username": "user", "password": "pass"}'
    }
    boto3.client = Mock(return_value=secrets_client)

    assert get_secret("test") == {"username": "user", "password": "pass"}


def test_db_config(monkeypatch):
    monkeypatch.setenv("username", "user")
    monkeypatch.setenv("password", "pass")
    monkeypatch.setenv("host", "host")
    monkeypatch.setenv("port", "port")
    monkeypatch.setenv("sid", "sid")
    config = db_config()
    assert config == {"user": "user", "password": "pass", "dsn": "host:port/sid"}
