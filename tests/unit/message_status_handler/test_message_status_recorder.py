from unittest.mock import Mock, patch

import message_status_recorder

import database

@patch("message_status_recorder.update_message_status", return_value=12)
@patch("database.cursor")
def test_record_message_statuses(mock_cursor, mock_update_message_status):
    batch_id = "batch_id"
    json_data = {
        "data": [
            {"message_reference": "message_reference_1"},
            {"message_reference": "message_reference_2"},
        ]
    }
    message_status_recorder.record_message_statuses(batch_id, json_data)

    assert mock_update_message_status.call_count == 2
    mock_update_message_status.assert_any_call(mock_cursor().__enter__(), batch_id, "message_reference_1")
    mock_update_message_status.assert_any_call(mock_cursor().__enter__(), batch_id, "message_reference_2")


@patch("database.cursor")
def test_update_message_status(mock_cursor):
    mock_cursor_contextmanager = mock_cursor().__enter__()
    mock_var = Mock(getvalue=Mock(return_value=12))
    mock_cursor_contextmanager.var.return_value = mock_var

    response_code = message_status_recorder.update_message_status(mock_cursor_contextmanager, "batch_id", "message_reference_1")

    assert mock_cursor_contextmanager.execute.call_count == 1
    assert response_code == 12
    mock_cursor_contextmanager.execute.assert_called_once_with(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        {
            "in_val1": "batch_id",
            "in_val2": "message_reference_1",
            "in_val3": "read",
            "out_val": mock_var,
        },
    )
