import pytest
from unittest.mock import MagicMock, patch


# Mocking the boto3 client
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
