import pytest
from unittest.mock import Mock, patch
import database
import oracledb

@pytest.fixture(autouse=True)
def mocked_env(monkeypatch):
    monkeypatch.setenv("DATABASE_USER", "test")
    monkeypatch.setenv("DATABASE_PASSWORD", "test")
    monkeypatch.setenv("DATABASE_HOST", "test_host")
    monkeypatch.setenv("DATABASE_PORT", "1521")
    monkeypatch.setenv("DATABASE_SID", "test_sid")
    monkeypatch.setenv("SECRET_ARN", "test_secret")
    monkeypatch.setenv("REGION_NAME", "uk-west-1")


@patch("oracledb.connect")
def test_connection(mock_oracledb_connect):
    with database.connection() as conn:
        assert conn is not None

    assert conn.closed

@pytest.mark.skip
def test_failed_connection_to_db():
    with patch("database.oracledb") as mock_oracledb:
        mock_oracledb.Error = oracledb.Error
        mock_oracledb.connect = Mock(side_effect=oracledb.Error("Something's not right"))

        with pytest.raises(database.DatabaseConnectionError) as exc_info:
            database.connection()

        assert str(exc_info.value) == "Failed to connect to the database. Something's not right"

@patch("oracledb.connect")
def test_cursor(mock_oracledb_connect):
    with database.cursor() as cursor:
        assert cursor is not None

    assert cursor.closed


def test_connection_params():
    assert database.connection_params() == {"user": "test", "password": "test", "dsn": "test_host:1521/test_sid"}
