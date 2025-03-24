import database
import pytest
from unittest.mock import patch


@pytest.fixture
def mocked_env(monkeypatch):
    monkeypatch.setenv("bcss_host", "test_host")
    monkeypatch.setenv("port", "1521")
    monkeypatch.setenv("sid", "test_sid")
    monkeypatch.setenv("bcss_secret_name", "test_secret")
    monkeypatch.setenv("region_name", "uk-west-1")


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


def test_get_secret(mock_boto3_client):
    assert database.get_secret() == {"username": "test", "password": "test"}


def test_get_client(monkeypatch):
    monkeypatch.setenv("region_name", "uk-west-1")
    database.client = None

    assert database.get_client() is not None
