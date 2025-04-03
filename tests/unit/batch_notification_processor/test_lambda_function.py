from unittest.mock import Mock, patch
import lambda_function
from recipient import Recipient

import boto3


def test_lambda_handler(monkeypatch):
    mock_batch_processor = Mock()
    lambda_function.BatchProcessor = mock_batch_processor
    mock_communication_management = Mock()
    lambda_function.CommunicationManagement = mock_communication_management
    mock_scheduler = Mock()
    lambda_function.Scheduler = mock_scheduler
    lambda_function.generate_batch_id = Mock(
        return_value="b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3"
    )
    monkeypatch.setenv("DATABASE_HOST", "host")
    monkeypatch.setenv("DATABASE_PORT", "port")
    monkeypatch.setenv("DATABASE_SID", "sid")
    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": '{"username": "user", "password": "pass"}'
    }
    boto3.client = Mock(return_value=secrets_client)

    recipient = Recipient(("1234567890", "message_reference_0", "REQUESTED"))
    routing_plan_id = "c2c2c2c2-c2c2-c2c2c2c2-c2c2c2c2c2c2"

    mock_batch_processor.return_value.get_routing_plan_id = Mock(
        return_value=routing_plan_id
    )
    mock_batch_processor.return_value.get_recipients = Mock(return_value=[recipient])

    mock_response = Mock()
    mock_response.status_code = 201
    mock_communication_management.return_value.send_batch_message = Mock(
        return_value=mock_response
    )

    lambda_function.lambda_handler({}, {})

    mock_batch_processor.assert_called_once_with("b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3")
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

    assert lambda_function.secrets_client() == boto3.client(
        "secretsmanager", region_name="us-east-1"
    )


def test_get_secret():
    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": '{"username": "user", "password": "pass"}'
    }
    boto3.client = Mock(return_value=secrets_client)

    assert lambda_function.get_secret("test") == {
        "username": "user",
        "password": "pass",
    }


def test_db_config(monkeypatch):
    monkeypatch.setenv("username", "user")
    monkeypatch.setenv("password", "pass")
    monkeypatch.setenv("DATABASE_HOST", "host")
    monkeypatch.setenv("DATABASE_PORT", "port")
    monkeypatch.setenv("DATABASE_SID", "sid")
    config = lambda_function.db_config()
    assert config == {"user": "user", "password": "pass", "dsn": "host:port/sid"}
