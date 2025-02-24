import oracle_connection as oc
import json
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def setup():
    oc.PORT = "1521"
    oc.SID = "mock_sid"
    oc.BCSS_SECRET_NAME = "mock_secret_name"
    oc.BCSS_HOST = "mock_host"
    return oc.PORT, oc.SID, oc.BCSS_SECRET_NAME, oc.BCSS_HOST


def test_oracle_connection_valid(
    setup, mock_boto3_client, mock_oracledb_connect, mock_oracledb_makedsn
):
    mock_connection = MagicMock()
    mock_oracledb_connect.return_value = mock_connection

    connection = oc.oracle_connection(mock_boto3_client)

    mock_boto3_client.get_secret_value.assert_called_once_with(
        SecretId="mock_secret_name"
    )
    mock_oracledb_connect.assert_called_once_with(
        user="test_username", password="test_password", dsn="mock_dsn"
    )
    assert connection == mock_connection


def test_oracle_connection_missing_secret(setup, mock_boto3_client):
    missing_secret = {"password": "test_password"}
    mock_boto3_client.get_secret_value.return_value = {
        "SecretString": json.dumps(missing_secret)
    }

    with pytest.raises(KeyError):
        oc.oracle_connection(mock_boto3_client)
