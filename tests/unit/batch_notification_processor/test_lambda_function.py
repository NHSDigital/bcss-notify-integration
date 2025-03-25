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
@patch("batch_notification_processor.lambda_function.BatchProcessor", autospec=True)
@patch("batch_notification_processor.communication_management.json.dumps", return_value='{"mocked":"json"}')
def test_lambda_handler(
    mock_json_dumps,
    mock_batch_processor,
    mock_communication_management_class,
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
    monkeypatch.setenv("base_url", "http://example.com")
    monkeypatch.setenv("application_id", "test_app")
    monkeypatch.setenv("api_key", "test_key")
    
    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {
        "SecretString": '{"username": "user", "password": "pass"}'
    }
    boto3.client = Mock(return_value=secrets_client)

    recipient = Recipient(("1234567890", "message_reference_0", "REQUESTED"))
    routing_plan_id = "c2c2c2c2-c2c2-c2c2c2c2-c2c2c2c2c2c2"

    mock_get_connection.return_value = mock_connection
    mock_cursor.execute.return_value = [{"nhs_number": "1234567890", "message_id": "message_reference_0", "status": "REQUESTED"}]

    mock_batch_processor.return_value.get_routing_plan_id = Mock(
        return_value=routing_plan_id
    )

    mock_batch_processor.return_value.get_recipients = Mock(return_value=[recipient])

    # Set up the mock response for CommunicationManagement
    mock_response = Mock()
    mock_response.status_code = 201

    # Create a mock instance with all required methods
    mock_communication_management = Mock()
    mock_communication_management.send_batch_message.return_value = mock_response
    mock_communication_management.generate_batch_message_request_body.return_value = {
        "data": {
            "type": "messages",
            "attributes": {
                "routingPlanId": routing_plan_id,
                "messageBatchReference": "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3",
                "messages": [
                    {
                        "messageReference": "message_reference_0",
                        "recipient": {"nhsNumber": "1234567890"},
                        "personalisation": {},
                    }
                ],
            },
        }
    }
    mock_communication_management.generate_hmac_signature.return_value = "test_signature"
    
    # Set the mock instance as the return value for the class
    mock_communication_management_class.return_value = mock_communication_management

    lambda_handler({}, {})

    # Verify the interactions
    mock_batch_processor.assert_called_once_with(
        "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3",
        {"dsn": "host:port/sid", "user": "user", "password": "pass"},
    )
    mock_batch_processor.return_value.get_routing_plan_id.assert_called_once()
    mock_communication_management.send_batch_message.assert_called_once_with(
        "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3",
        routing_plan_id,
        [recipient]
    )


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
