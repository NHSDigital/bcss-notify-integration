import unittest
from unittest.mock import patch, Mock

import boto3
import pytest
import oracledb
import uuid

from oracle_database import OracleDatabase, DatabaseConnectionError
from recipient import Recipient


@pytest.fixture
def mock_db_credentials(monkeypatch):
    monkeypatch.setenv("DATABASE_HOST", "host")
    monkeypatch.setenv("DATABASE_PORT", "port")
    monkeypatch.setenv("DATABASE_SID", "sid")
    secrets_client = Mock()
    secrets_client.get_secret_value.return_value = {"SecretString": '{"username": "user", "password": "pass"}'}
    boto3.client = Mock(return_value=secrets_client)


@patch("oracle_database.oracledb", autospec=True)
class TestOracleDatabase():
    def testSuccessfulConnectionToDb(self, mock_oracledb, mock_db_credentials):
        database = OracleDatabase()

        database.connect()

        assert database.connection is not None

    def testFailedConnectionToDb(self, mock_oracledb, mock_db_credentials):
        database = OracleDatabase()
        mock_oracledb.Error = oracledb.Error
        mock_oracledb.connect = Mock(side_effect=oracledb.Error("Something's not right"))

        with pytest.raises(DatabaseConnectionError) as exc_info:
            database.connect()

        assert str(exc_info.value) == "Failed to connect to the database. Something's not right"

    def test_get_routing_plan_id(self, mock_oracledb, mock_db_credentials):
        database = OracleDatabase()

        expected_routing_plan_id = str(uuid.uuid4())
        batch_id = '1234'
        mock_cursor = database.cursor().__enter__()
        mock_cursor.callfunc = Mock(return_value=expected_routing_plan_id)

        routing_plan_id = database.get_routing_plan_id(batch_id)

        mock_cursor.callfunc.assert_called_with(
            "PKG_NOTIFY_WRAP.f_get_next_batch",
            mock_oracledb.STRING,
            [batch_id]
        )
        assert routing_plan_id == expected_routing_plan_id

    def test_get_recipients(self, mock_oracledb, mock_db_credentials):
        database = OracleDatabase()
        raw_recipient_data = [
            ("1111111111", "message_reference_1"),
            ("2222222222", "message_reference_2"),
        ]

        mock_cursor = database.cursor().__enter__()
        mock_cursor.fetchall = Mock(return_value=raw_recipient_data)

        batch_id = '1234'

        recipients = database.get_recipients(batch_id)

        mock_cursor.execute.assert_called_with(
            "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id", {'batch_id': batch_id})

        assert len(recipients) == 2
        assert isinstance(recipients[0], Recipient)
        assert recipients[0].nhs_number == "1111111111"
        assert recipients[0].message_id == "message_reference_1"
        assert isinstance(recipients[1], Recipient)
        assert recipients[1].nhs_number == "2222222222"
        assert recipients[1].message_id == "message_reference_2"

    def test_update_message_id(self, mock_oracledb, mock_db_credentials):
        database = OracleDatabase()
        recipient = Recipient(("1111111111", "message_reference_1"))

        mock_cursor = database.cursor().__enter__()

        database.update_message_id(recipient)

        mock_cursor.execute.assert_called_with(
            "UPDATE v_notify_message_queue SET message_id = :message_id WHERE nhs_number = :nhs_number",
            {'message_id': recipient.message_id, 'nhs_number': recipient.nhs_number}
        )
        database.connection.commit.assert_called_once()

    def test_update_message_status(self, mock_oracledb, mock_db_credentials):
        database = OracleDatabase()
        recipient = Recipient(("1111111111", "message_reference_1"))

        mock_cursor = database.cursor().__enter__()

        database.update_message_status(recipient)

        mock_cursor.execute.assert_called_with(
            "UPDATE v_notify_message_queue SET message_status = :message_status WHERE nhs_number = :nhs_number",
            {'message_status': recipient.message_status, 'nhs_number': recipient.nhs_number}
        )
        database.connection.commit.assert_called_once()
