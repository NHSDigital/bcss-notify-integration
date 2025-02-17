import pytest
from bcss_notify_callback.patients_to_update import patient_to_update
from unittest.mock import MagicMock


@pytest.fixture
def setup():
    message_id = "123"
    queue_dict = [
        {"MESSAGE_ID": "123", "BATCH_ID": "456"},
        {"MESSAGE_ID": "789", "BATCH_ID": "ABC"},
    ]
    mock_connection = MagicMock()
    cursor = mock_connection.return_value
    var = cursor.var(int)
    return message_id, queue_dict, var


def test_patient_to_update_valid_match(setup):
    """Test that a valid patient is returned."""
    message_id, queue_dict, var = setup
    data = patient_to_update(message_id, queue_dict, var)

    assert data["in_val1"] == "456"
    assert data["in_val2"] == "123"
    assert data["in_val3"] == "read"
    assert data["out_val"] == var


def test_patient_to_update_valid_no_match(setup):
    """Test that False is returned if no match is found."""
    message_id, queue_dict, var = setup
    message_id = "XYZ"
    data = patient_to_update(message_id, queue_dict, var)

    assert not data


# Test for missing queue_patient["BATCH_ID"]?
# What would we want the outcome to be if either of these are missing?
# def test_patient_to_update_invalid_missing_batch_id(setup):
#     message_id, queue_dict, var = setup
#     pass
