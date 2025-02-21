import pytest
from unittest.mock import MagicMock
from bcss_notify_callback.sql import (
    read_queue_table_to_dict,
    call_update_message_status,
)


@pytest.fixture
def setup():
    mock_cursor = MagicMock()

    mock_cursor.description = [
        ("NHS_NUMBER",),
        ("MESSAGE_ID",),
        ("BATCH_ID",),
        ("MESSAGE_STATUS",),
    ]
    return mock_cursor


def test_read_queue_table_to_dict_valid(setup):
    mock_cursor = setup

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

    response = read_queue_table_to_dict(mock_cursor)

    assert response == expected


def test_read_queue_table_to_dict_invalid_empty_table(setup):
    with pytest.raises(TypeError):
        mock_cursor = setup
        mock_cursor.fetchall.return_value = None

        read_queue_table_to_dict(mock_cursor)


def test_call_update_message_status_valid(setup):
    mock_cursor = setup
    mock_var = MagicMock()
    mock_var.getvalue.return_value = 0

    data = {"in_val1": "456", "in_val2": "123", "in_val3": "read"}

    response = call_update_message_status(mock_cursor, data, mock_var)

    mock_cursor.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )

    assert response == 0


def test_call_update_message_status_invalid_message_id(setup):
    mock_cursor = setup
    mock_var = MagicMock()
    mock_var.getvalue.return_value = 1

    data = {"in_val1": "456", "in_val2": "INVALIDMESSAGEID", "in_val3": "read"}

    response = call_update_message_status(mock_cursor, data, mock_var)

    mock_cursor.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )

    assert response != 0


def test_call_update_message_status_invalid_data(setup):
    mock_cursor = setup
    mock_var = MagicMock()
    mock_var.getvalue.return_value = 1

    data = {"in_val1": "456", "in_val2": "123"}

    response = call_update_message_status(mock_cursor, data, mock_var)

    mock_cursor.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )

    # The message_status column is not nullable so when a NULL value is passed into the procedure,
    # it should return an Oracle exception, ORA-01400 Cannot insert NULL value
    assert response != 0
