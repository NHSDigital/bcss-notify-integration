import database
import pytest
from unittest.mock import patch


@pytest.fixture
def mocked_env(monkeypatch):
    monkeypatch.setenv("DATABASE_HOST", "test_host")
    monkeypatch.setenv("DATABASE_PORT", "1521")
    monkeypatch.setenv("DATABASE_SID", "test_sid")
    monkeypatch.setenv("SECRET_ARN", "test_secret")
    monkeypatch.setenv("REGION_NAME", "uk-west-1")


@pytest.fixture
def mock_boto3_client(mocked_env):
    with patch("boto3.client") as mock_boto3_client:
        mock_boto3_client.return_value.get_secret_value.return_value={"SecretString": '{"username": "test", "password": "test"}'}

        yield mock_boto3_client


@patch("oracledb.connect")
def test_connection(mock_oracledb_connect, mock_boto3_client):
    with database.connection() as conn:
        assert conn is not None

    assert conn.closed


@patch("oracledb.connect")
def test_cursor(mock_oracledb_connect, mock_boto3_client):
    with database.cursor() as cursor:
        assert cursor is not None

    assert cursor.closed


def test_connection_params(mock_boto3_client):
    assert database.connection_params() == {"user": "test", "password": "test", "dsn": "test_host:1521/test_sid"}
