import oracle as oc
import json
import logging
import pytest
import uuid
import oracledb
from bcss_s3_to_lambda.recipient import Recipient
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


def test_get_routing_plan_id(mock_connection, mock_cursor):
    expected_routing_plan_id = str(uuid.uuid4())
    batch_id = "1234"
    mock_cursor.callfunc = MagicMock(return_value=expected_routing_plan_id)

    routing_plan_id = oc.get_routing_plan_id(mock_connection, batch_id)

    mock_cursor.callfunc.assert_called_with(
        "PKG_NOTIFY_WRAP.f_get_next_batch", oracledb.STRING, [batch_id]
    )
    assert routing_plan_id == expected_routing_plan_id


def test_get_recipients(mock_connection, mock_cursor):
    raw_recipient_data = [
        ("1111111111", "message_reference_1"),
        ("2222222222", "message_reference_2"),
    ]

    mock_cursor.fetchall = MagicMock(return_value=raw_recipient_data)

    batch_id = "1234"

    recipients = oc.get_recipients(mock_connection, batch_id)

    mock_cursor.execute.assert_called_with(
        "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id",
        {"batch_id": batch_id},
    )

    assert len(recipients) == 2
    assert isinstance(recipients[0], Recipient)
    assert recipients[0].nhs_number == "1111111111"
    assert recipients[0].message_id == "message_reference_1"
    assert isinstance(recipients[1], Recipient)
    assert recipients[1].nhs_number == "2222222222"
    assert recipients[1].message_id == "message_reference_2"
