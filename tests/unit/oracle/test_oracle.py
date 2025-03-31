import oracle as oc
import json
import logging
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def setup():
    oc.PORT = "1521"
    oc.SID = "mock_sid"
    oc.BCSS_SECRET_NAME = "mock_secret_name"
    oc.BCSS_HOST = "mock_host"
    oc.REGION_NAME = "mock_region_name"
    return oc.PORT, oc.SID, oc.BCSS_SECRET_NAME, oc.BCSS_HOST, oc.REGION_NAME


def test_oracle_connection_valid(
    setup, mock_boto3_client, mock_oracledb_connect, mock_oracledb_makedsn
):
    mock_connection = MagicMock()
    mock_oracledb_connect.return_value = mock_connection

    connection = oc.create_oracle_connection(mock_boto3_client)

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

    assert oc.create_oracle_connection(mock_boto3_client) == {
        "statusCode": 500,
        "body": "Error Connecting to Database: 'username'",
    }


def test_get_queue_table_records_valid(mock_connection, mock_cursor):
    logger = logging.getLogger()

    mock_cursor.description = [
        ("NHS_NUMBER",),
        ("MESSAGE_ID",),
        ("BATCH_ID",),
        ("MESSAGE_STATUS",),
    ]
    mock_cursor.fetchall.return_value = [
        ("1234567890", "123", "456", "sent"),
        ("0987654321", "789", "ABC", "sending"),
    ]

    expected = [
        {
            "NHS_NUMBER": "1234567890",
            "MESSAGE_ID": "123",
            "BATCH_ID": "456",
            "MESSAGE_STATUS": "sent",
        },
        {
            "NHS_NUMBER": "0987654321",
            "MESSAGE_ID": "789",
            "BATCH_ID": "ABC",
            "MESSAGE_STATUS": "sending",
        },
    ]

    response = oc.get_queue_table_records(mock_connection, logger)

    assert response == expected


def test_get_queue_table_records_invalid_empty_table(mock_connection, mock_cursor):
    with pytest.raises(TypeError):
        mock_cursor.fetchall.return_value = None
        logger = logging.getLogger()

        oc.get_queue_table_records(mock_connection, logger)


def test_call_update_message_status_valid(mock_connection, mock_cursor):
    mock_var = mock_cursor.var(int)
    mock_var.getvalue.return_value = 0

    data = {"in_val1": "456", "in_val2": "123", "in_val3": "read"}

    response = oc.call_update_message_status(mock_connection, data)

    mock_cursor.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )

    assert response == 0


def test_call_update_message_status_invalid_message_id(mock_connection, mock_cursor):
    mock_var = mock_cursor.var(int)
    mock_var.getvalue.return_value = 1

    data = {"in_val1": "456", "in_val2": "INVALIDMESSAGEID", "in_val3": "read"}

    response = oc.call_update_message_status(mock_connection, data)

    mock_cursor.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )

    assert response != 0


def test_call_update_message_status_invalid_data(mock_connection, mock_cursor):
    mock_var = mock_cursor.var(int)
    mock_var.getvalue.return_value = 1

    data = {"in_val1": "456", "in_val2": "123"}

    response = oc.call_update_message_status(mock_connection, data)

    mock_cursor.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )

    assert response != 0
