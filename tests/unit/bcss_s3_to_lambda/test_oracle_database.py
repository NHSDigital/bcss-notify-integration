import unittest
from unittest.mock import patch, Mock

import pytest
import oracledb
import uuid

from oracle_database import OracleDatabase, DatabaseConnectionError
from recipient import Recipient


def db_config():
    return {
        'dsn': "dsn",
        'user': "user",
        'password': "password"
    }


@patch("oracle_database.oracledb", autospec=True)
class TestOracleDatabase(unittest.TestCase):
    def testSuccessfulConnectionToDb(self, mock_oracledb):
        database = OracleDatabase(**db_config())

        database.connect()

        assert database.connection is not None

    def testFailedConnectionToDb(self, mock_oracledb):
        database = OracleDatabase(**db_config())
        mock_oracledb.Error = oracledb.Error
        mock_oracledb.connect = Mock(side_effect=oracledb.Error("Something's not right"))

        with pytest.raises(DatabaseConnectionError) as exc_info:
            database.connect()

        assert str(exc_info.value) == "Failed to connect to the database. Something's not right"

    def test_get_next_batch(self, mock_oracledb):
        database = OracleDatabase(**db_config())

        routing_plan_id = str(uuid.uuid4())
        batch_id = '1234'
        mock_cursor = database.cursor().__enter__()
        mock_cursor.callfunc = Mock(return_value=routing_plan_id)

        next_batch = database.get_next_batch(batch_id)

        mock_cursor.callfunc.assert_called_with(
            "PKG_NOTIFY_WRAP.f_get_next_batch",
            mock_oracledb.STRING,
            [batch_id]
        )
        assert next_batch == routing_plan_id


    def test_get_recipients(self, mock_oracledb):
        database = OracleDatabase(**db_config())
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
