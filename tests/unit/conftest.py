import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_connection(mock_cursor):
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection


@pytest.fixture
def mock_cursor(mock_var, example_message_reference, example_message_reference_2):
    mock_cursor = MagicMock()
    mock_cursor.cursor.return_value = mock_cursor
    mock_cursor.var.return_value = mock_var
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = [
        ("123456789", example_message_reference, "ABC"),
        ("987654321", example_message_reference_2, "ABC"),
        ("123987456", "example_message_id", "ABC"),
    ]
    mock_cursor.description = [
        ("NHS_NUMBER",),
        ("MESSAGE_ID",),
        ("BATCH_ID",),
    ]
    return mock_cursor


@pytest.fixture
def mock_var():
    mock_var = MagicMock()
    mock_var.getvalue.return_value = 0
    return mock_var


@pytest.fixture
def mock_boto3_client():
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": '{\n  "username":"test_username",\n  "password":"test_password"\n}\n',
    }
    return mock_client


@pytest.fixture
def mock_generate_batch_id():
    mock_generate_batch_id = MagicMock()
    mock_generate_batch_id.return_value = "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3"
    return mock_generate_batch_id


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
def mock_get_recipients():
    with patch("oracle.oracle.get_recipients") as mock_get_recipients:
        yield mock_get_recipients


@pytest.fixture
def mock_batch_processor():
    with patch(
        "batch_notification_processor.lambda_function.BatchProcessor"
    ) as mock_batch_processor:
        yield mock_batch_processor


@pytest.fixture
def mock_scheduler():
    with patch(
        "batch_notification_processor.lambda_function.Scheduler"
    ) as mock_scheduler:
        yield mock_scheduler


@pytest.fixture
def mock_communication_management():
    with patch(
        "batch_notification_processor.communication_management.CommunicationManagement"
    ) as mock_communication_management:
        yield mock_communication_management


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get


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
def example_recipient_to_update(example_message_reference):
    return {
        "NHS_NUMBER": "123456789",
        "MESSAGE_ID": example_message_reference,
        "BATCH_ID": "ABC",
    }


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
def example_patient_to_update_dict():
    message_id = "123"
    queue_dict = [
        {"MESSAGE_ID": "123", "BATCH_ID": "456"},
        {"MESSAGE_ID": "789", "BATCH_ID": "ABC"},
    ]

    return message_id, queue_dict


@pytest.fixture
def example_batch_id():
    return "example_batch_id"
