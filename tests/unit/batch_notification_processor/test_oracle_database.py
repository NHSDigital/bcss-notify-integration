import unittest
from unittest.mock import patch, Mock

import pytest
import oracledb
import uuid

from database import DatabaseConnectionError
from recipient import Recipient
import oracle_database

@pytest.fixture
def mock_db_credentials(monkeypatch):
    monkeypatch.setenv("DATABASE_USER", "user")
    monkeypatch.setenv("DATABASE_PASSWORD", "password")
    monkeypatch.setenv("DATABASE_HOST", "host")
    monkeypatch.setenv("DATABASE_PORT", "port")
    monkeypatch.setenv("DATABASE_SID", "sid")


@patch("oracle_database.database", autospec=True)
def test_get_routing_plan_id(mock_database):
    expected_routing_plan_id = str(uuid.uuid4())
    batch_id = '1234'
    mock_cursor = mock_database.cursor().__enter__()
    mock_cursor.callfunc = Mock(return_value=expected_routing_plan_id)

    routing_plan_id = oracle_database.get_routing_plan_id(batch_id)

    mock_cursor.callfunc.assert_called_with(
        "PKG_NOTIFY_WRAP.f_get_next_batch",
        oracledb.STRING,
        [batch_id]
    )
    assert routing_plan_id == expected_routing_plan_id


@patch("oracle_database.database", autospec=True)
def test_get_recipients(mock_database):
    raw_recipient_data = [
        ("1111111111", "message_reference_1"),
        ("2222222222", "message_reference_2"),
    ]

    mock_cursor = mock_database.cursor().__enter__()
    mock_cursor.fetchall = Mock(return_value=raw_recipient_data)

    batch_id = '1234'

    recipients = oracle_database.get_recipients(batch_id)

    mock_cursor.execute.assert_called_with(
        "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id", {'batch_id': batch_id})

    assert len(recipients) == 2
    assert isinstance(recipients[0], Recipient)
    assert recipients[0].nhs_number == "1111111111"
    assert recipients[0].message_id == "message_reference_1"
    assert isinstance(recipients[1], Recipient)
    assert recipients[1].nhs_number == "2222222222"
    assert recipients[1].message_id == "message_reference_2"


@patch("oracle_database.database", autospec=True)
def test_update_message_id(mock_database):
    recipient = Recipient(("1111111111", "message_reference_1"))

    mock_cursor = mock_database.cursor().__enter__()

    oracle_database.update_message_id(recipient)

    mock_cursor.execute.assert_called_with(
        "UPDATE v_notify_message_queue SET message_id = :message_id WHERE nhs_number = :nhs_number",
        {'message_id': recipient.message_id, 'nhs_number': recipient.nhs_number}
    )
    mock_cursor.connection.commit.assert_called_once()


@patch("oracle_database.database", autospec=True)
def test_update_message_status(mock_database):
    recipient = Recipient(("1111111111", "message_reference_1"))

    mock_cursor = mock_database.cursor().__enter__()

    oracle_database.update_message_status(recipient)

    mock_cursor.execute.assert_called_with(
        "UPDATE v_notify_message_queue SET message_status = :message_status WHERE nhs_number = :nhs_number",
        {'message_status': recipient.message_status, 'nhs_number': recipient.nhs_number}
    )
    mock_cursor.connection.commit.assert_called_once()
