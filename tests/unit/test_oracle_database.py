import unittest
from unittest.mock import MagicMock, patch, Mock

from parameterized import parameterized
import pytest
import oracledb

from oracle_database import OracleDatabase
from requests.exceptions import ConnectionError

class MyTestCase(unittest.TestCase):
    @parameterized.expand([
        ["user", "password", None,],
        ["user", None, "dsn"],
        [None, 'password', "dsn"],
        [None, None, None],
        ["", "", ""]
    ])
    def testConnectionToDbWithNullValues(self, user, password, dsn):
        db_config = {
            'user': user,
            'password': password,
            'dsn': dsn
        }
        database = OracleDatabase(**db_config)

        with pytest.raises(ConnectionError) as exc_info:
            database.connect()

        assert str(exc_info.value) == "Missing connection parameters."

    def testSuccessfulConnectionToDb(self):
        db_config = {
            'user': "user",
            'password': "password",
            'dsn': "dsn"
        }
        database = OracleDatabase(**db_config)

        with patch('oracledb.connect', return_value='Successful Connection'):
            assert(database.connect() == True)

    def testFailedConnectionToDb(self):
        db_config = {
            'user': "user",
            'password': "INCORRECT_PASSWORD",
            'dsn': "dsn"
        }
        database = OracleDatabase(**db_config)

        with patch('oracledb.connect') as mock_oracle_connect:
            mock_oracle_connect.side_effect = (oracledb.Error, "Error connecting to Oracle database")

            with pytest.raises(ConnectionError) as exc_info:
                database.connect()

                assert str(exc_info.value) == "Failed to connect to the database."

    def test_get_next_batch(self):
        db_config = {
            'user': "user",
            'password': "INCORRECT_PASSWORD",
            'dsn': "dsn"
        }
        database = OracleDatabase(**db_config)

        with patch('oracle_database.OracleDatabase.call_function', return_value='5678'):
            assert(database.get_next_batch('1234') == '5678')

    def test_get_set_of_participants(self):
        db_config = {
            'user': "user",
            'password': "password",
            'dsn': "dsn"
        }
        database = OracleDatabase(**db_config)

        database.execute_query = Mock(return_value='Successful Query')

        batch_id = '1234'

        assert(database.get_set_of_participants(batch_id) == 'Successful Query')
        database.execute_query.assert_called_with("SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id", {'batch_id': batch_id})

    def test_get_set_of_participants_null_batch_id(self):
        db_config = {
            'user': "user",
            'password': "password",
            'dsn': "dsn"
        }
        database = OracleDatabase(**db_config)

        database.execute_query = Mock(return_value='Successful Query')

        assert(database.get_set_of_participants(None) == 'Successful Query')
        database.execute_query.assert_called_with("SELECT * FROM v_notify_message_queue WHERE batch_id IS NULL")

    def test_get_participants_no_db_connection(self):
        db_config = {
            'user': "user",
            'password': "password",
            'dsn': "dsn"
        }
        database = OracleDatabase(**db_config)


        with pytest.raises(ConnectionError) as exc_info:
            database.get_set_of_participants('1234')

            assert str(exc_info.value) == "Database is not connected."


if __name__ == '__main__':
    unittest.main()
