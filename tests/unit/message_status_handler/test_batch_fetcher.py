from unittest.mock import Mock, patch

import batch_fetcher
import oracledb


@patch("database.cursor")
def test_fetch_batch_ids(mock_cursor):
    mock_cursor.return_value.__enter__.return_value.fetchall.return_value = [
        ("batch_id_1",),
        ("batch_id_2",)
    ]
    batch_ids = batch_fetcher.fetch_batch_ids()

    assert batch_ids == ["batch_id_1", "batch_id_2"]

    mock_cursor().__enter__().execute.assert_called_once_with(
        "SELECT DISTINCT batch_id FROM v_notify_message_queue WHERE message_status = :status",
        {"status": "sending"}
    )


@patch("database.cursor")
def test_fetch_batch_ids_error(mock_cursor):
    error = oracledb.Error("Database error")
    mock_cursor.return_value.__enter__.return_value.fetchall.side_effect = error

    with patch("logging.error") as mock_logging:
        batch_ids = batch_fetcher.fetch_batch_ids()

    assert batch_ids == []
    mock_logging.assert_called_once_with("Error fetching batch IDs: %s", error)
