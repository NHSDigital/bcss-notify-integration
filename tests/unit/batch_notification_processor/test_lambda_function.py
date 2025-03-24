from unittest.mock import Mock, patch
from lambda_function import lambda_handler, secrets_client, get_secret, db_config
from recipient import Recipient
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
@patch(
    "batch_notification_processor.communication_management.CommunicationManagement.send_batch_message",
    return_value=201,
)
@patch("batch_notification_processor.batch_processor.BatchProcessor", autospec=True)
def test_lambda_handler(
    mock_batch_processor,
    send_batch_message,
    mock_communication_management,
    mock_scheduler,
    generate_batch_id,
    mock_get_connection,
    mock_connection,
    mock_cursor,
    mock_boto3_client,
    mock_get_recipients,
    monkeypatch,
    caplog,
):
    caplog.set_level(logging.INFO)
    monkeypatch.setenv("host", "host")
    monkeypatch.setenv("port", "port")
    monkeypatch.setenv("sid", "sid")
    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": '{"username": "user", "password": "pass"}'
    }
    boto3.client = Mock(return_value=secrets_client)

    recipient = Recipient(("1234567890", "message_reference_0", "REQUESTED"))
    routing_plan_id = "c2c2c2c2-c2c2-c2c2c2c2-c2c2c2c2c2c2"

    mock_get_connection.return_value = mock_connection
    mock_cursor.execute.return_value = [recipient]

    mock_batch_processor.return_value.get_routing_plan_id = Mock(
        return_value=routing_plan_id
    )

    mock_batch_processor.return_value.get_recipients = Mock(return_value=[recipient])

    mock_response = Mock()
    mock_response.status_code = 201
    mock_communication_management.return_value.send_batch_message = Mock(
        return_value=mock_response
    )

    lambda_handler({}, {})

    mock_batch_processor.assert_called_once_with(
        "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3",
        {"dsn": "host:port/sid", "user": "user", "password": "pass"},
    )
    mock_batch_processor.return_value.get_routing_plan_id.assert_called_once()
    mock_batch_processor.return_value.get_recipients.assert_called_once()

    mock_communication_management.assert_called_once()
    mock_communication_management.return_value.send_batch_message.assert_called_once_with(
        "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3", routing_plan_id, [recipient]
    )
    mock_batch_processor.return_value.mark_batch_as_sent.assert_called_once_with(
        [recipient]
    )
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
