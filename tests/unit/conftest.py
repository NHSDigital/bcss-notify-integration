import pytest
import os
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_environment():
    os.environ["PORT"] = "1521"
    os.environ["SID"] = "mock_sid"
    os.environ["BCSS_SECRET_NAME"] = "mock_secret_name"
    os.environ["BCSS_HOST"] = "mock_host"
    os.environ["REGION_NAME"] = "mock_region_name"


@pytest.fixture
def mock_connection(mock_cursor):
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection


@pytest.fixture
def mock_cursor():
    return MagicMock()


@pytest.fixture
def mock_boto3_client():
    mock_client = MagicMock()
    # Mock the get_secret_value response
    mock_client.get_secret_value.return_value = {
        "SecretString": '{\n  "username":"test_username",\n  "password":"test_password"\n}\n',
    }
    return mock_client


@pytest.fixture
def mock_oracledb_connect():
    """Fixture to mock oracledb.connect."""
    with patch("oracledb.connect") as mock_connect:
        yield mock_connect


@pytest.fixture
def mock_oracledb_makedsn():
    """Fixture to mock oracledb.makedsn."""
    with patch("oracledb.makedsn") as mock_makedsn:
        mock_makedsn.return_value = "mock_dsn"
        yield mock_makedsn


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_get_message_references():
    with patch(
        "bcss_notify_callback.lambda_function.get_message_references"
    ) as mock_get_message_references:
        yield mock_get_message_references


@pytest.fixture
def mock_read_queue_to_dict():
    with patch(
        "bcss_notify_callback.sql.read_queue_table_to_dict"
    ) as mock_read_queue_to_dict:
        yield mock_read_queue_to_dict


@pytest.fixture
def mock_call_update_message_status():
    with patch(
        "bcss_notify_callback.sql.call_update_message_status"
    ) as mock_call_update_message_status:
        yield mock_call_update_message_status


@pytest.fixture
def example_body_data(example_message_reference):
    """Fixture to return an example callback response."""
    data = [
        {
            "type": "ChannelStatus",
            "attributes": {
                "messageId": "example_message_id",
                "messageReference": f"{example_message_reference}",
                "cascadeType": "primary",
                "cascadeOrder": 1,
                "channel": "nhsapp",
                "channelStatus": "failed",
                "channelStatusDescription": "Unnotified",
                "supplierStatus": "read",
                "retryCount": 0,
                "timestamp": "2000-01-01T00:00:00.000Z",
            },
            "links": {"message": "www.example-api-link.com"},
            "meta": {"idempotencyKey": "test_idempotency_key"},
        }
    ]
    return data


@pytest.fixture
def example_message_reference():
    return "example_message_reference"


@pytest.fixture
def example_message_reference_2():
    return "example_message_reference_2"


@pytest.fixture
def example_message_references(example_message_reference, example_message_reference_2):
    message_references = [example_message_reference, f"{example_message_reference_2}"]
    return message_references


@pytest.fixture
def example_comms_management_response(
    example_message_reference, example_message_reference_2
):
    data = [
        [
            {
                "type": "ChannelStatus",
                "attributes": {
                    "messageId": "example_message_id",
                    "messageReference": f"{example_message_reference}",
                    "cascadeType": "primary",
                    "cascadeOrder": 1,
                    "channel": "nhsapp",
                    "channelStatus": "failed",
                    "channelStatusDescription": "Unnotified",
                    "supplierStatus": "read",
                    "retryCount": 0,
                    "timestamp": "2000-01-01T00:00:00.000Z",
                },
                "links": {"message": "www.example-api-link.com"},
                "meta": {"idempotencyKey": "test_idempotency_key"},
            }
        ],
        [
            {
                "type": "ChannelStatus",
                "attributes": {
                    "messageId": "example_message_id",
                    "messageReference": f"{example_message_reference_2}",
                    "cascadeType": "primary",
                    "cascadeOrder": 1,
                    "channel": "nhsapp",
                    "channelStatus": "failed",
                    "channelStatusDescription": "Unnotified",
                    "supplierStatus": "read",
                    "retryCount": 0,
                    "timestamp": "2000-01-01T00:00:00.000Z",
                },
                "links": {"message": "www.example-api-link.com"},
                "meta": {"idempotencyKey": "test_idempotency_key"},
            }
        ],
    ]
    return data


@pytest.fixture
def example_recipients_to_update(
    example_message_reference, example_message_reference_2
):
    return [
        {
            "NHS_NUMBER": "123456789",
            "MESSAGE_ID": example_message_reference,
            "BATCH_ID": "ABC",
        },
        {
            "NHS_NUMBER": "987654321",
            "MESSAGE_ID": f"{example_message_reference_2}",
            "BATCH_ID": "ABC",
        },
    ]


@pytest.fixture
def example_queue_table_data(example_message_reference, example_message_reference_2):
    return [
        {
            "NHS_NUMBER": "123456789",
            "MESSAGE_ID": example_message_reference,
            "BATCH_ID": "ABC",
        },
        {
            "NHS_NUMBER": "987654321",
            "MESSAGE_ID": f"{example_message_reference_2}",
            "BATCH_ID": "ABC",
        },
        {
            "NHS_NUMBER": "123987456",
            "MESSAGE_ID": "example_message_id",
            "BATCH_ID": "ABC",
        },
    ]


@pytest.fixture
def example_batch_id():
    return "example_batch_id"


@pytest.fixture
def example_comms_management_url():
    return "www.example_comms_management_url.com"
