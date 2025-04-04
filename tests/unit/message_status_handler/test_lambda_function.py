import hashlib
import hmac
import logging
import pytest
import requests
import lambda_function as lf
from unittest.mock import MagicMock


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("APPLICATION_ID", "application_id")
    monkeypatch.setenv("NOTIFY_API_KEY", "api_key")


def test_generate_hmac_signature_valid(setup):
    """Test that an HMAC SHA-256 signature is generated correctly."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert lf.generate_hmac_signature("application_id.api_key", body) == signature


def test_validate_signature_valid(setup):
    """Test that a valid signature passes verification."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert lf.validate_signature(signature, "application_id.api_key", body)


def test_validate_signature_invalid(setup):
    """Test that an invalid signature does not pass verification."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert not lf.validate_signature(signature, "test", body)


def test_lambda_handler(setup):
    """Test that the Lambda handler returns the correct response."""
    pass


def test_get_status_from_notify_api(example_body_data, example_message_reference):
    """Test that a callback is processed correctly."""
    response = lf.get_status_from_notify_api(example_body_data)

    assert response == example_message_reference


def test_get_status_from_notify_api_invalid_missing_message_reference_value(
    example_body_data,
):
    """Test that missing callback_id is handled correctly"""
    with pytest.raises(ValueError):
        example_body_data[0]["attributes"]["messageReference"] = ""
        lf.get_status_from_notify_api(example_body_data)


def test_get_status_from_notify_api_invalid_missing_attribute_index(example_body_data):
    """Test that missing messageReference attribute is handled correctly"""
    with pytest.raises(KeyError):
        del example_body_data[0]["attributes"]["messageReference"]
        lf.get_status_from_notify_api(example_body_data)


def test_get_message_references_valid(
    example_comms_management_response, example_message_references
):
    message_references = lf.get_message_references(
        example_comms_management_response, []
    )
    assert message_references == example_message_references


def test_get_message_references_invalid_missing_message_reference_value(
    example_comms_management_response, caplog
):
    with pytest.raises(ValueError):
        example_comms_management_response[0][0]["attributes"]["messageReference"] = ""
        example_comms_management_response[1][0]["attributes"]["messageReference"] = ""
        lf.get_message_references(example_comms_management_response, [])
    assert caplog.records[0].levelname == "ERROR"
    assert (
        caplog.records[0].message
        == "Error processing API response JSON: Missing Value: 'messageReference' in API data"
    )


def test_get_message_references_invalid_missing_message_reference_key(
    example_comms_management_response, caplog
):
    with pytest.raises(KeyError):
        caplog.set_level(logging.ERROR)
        del example_comms_management_response[0][0]["attributes"]["messageReference"]
        del example_comms_management_response[1][0]["attributes"]["messageReference"]
        lf.get_message_references(example_comms_management_response, [])
    assert caplog.records[0].levelname == "ERROR"
    assert (
        caplog.records[0].message
        == "Error processing API response JSON: Missing Key: 'messageReference' in API data"
    )


def test_get_statuses_from_communication_management_api_valid(
    mock_requests_get,
    example_batch_id,
    example_comms_management_response,
    example_message_references,
):
    mock_comms_management_response = MagicMock()
    mock_comms_management_response.status_code = 200
    mock_comms_management_response.json.return_value = example_comms_management_response
    mock_requests_get.return_value = mock_comms_management_response

    mock_get_message_references = MagicMock(return_value=example_message_references)
    lf.get_message_references = mock_get_message_references

    response = lf.get_statuses_from_communication_management_api(example_batch_id)
    mock_requests_get.assert_called_once_with(
        f"{lf.os.getenv('communication_management_api_url')}/api/statuses/{example_batch_id}",
        timeout=30,
    )
    assert response == example_message_references


def test_get_statuses_from_communication_management_api_invalid_non_200_response(
    mock_requests_get, example_comms_management_response, example_batch_id, caplog
):
    with pytest.raises(requests.exceptions.HTTPError) as e:
        caplog.set_level(logging.ERROR)
        mock_comms_management_response = MagicMock()
        mock_comms_management_response.status_code = 500
        mock_comms_management_response.json.return_value = (
            example_comms_management_response
        )
        mock_comms_management_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("500 Server Error")
        )
        mock_requests_get.return_value = mock_comms_management_response

        lf.get_statuses_from_communication_management_api(example_batch_id)
        mock_requests_get.assert_called_once_with(
            f"{lf.os.getenv('communication_management_api_url')}/api/statuses/{example_batch_id}",
            timeout=30,
        )
    assert str(e.value) == "500 Server Error"
    assert caplog.records[0].levelname == "ERROR"
    assert (
        caplog.records[0].message
        == "Failed to get statuses from Communication Management API: 500 Server Error"
    )


def test_get_recipients_to_update(
    mock_connection,
    example_queue_table_data,
    example_message_references,
    caplog,
):
    caplog.set_level(logging.INFO)

    recipients_to_update = lf.get_recipients_to_update(
        mock_connection, example_message_references
    )

    assert len(recipients_to_update) == 2
    assert recipients_to_update[0] == example_queue_table_data[0]
    assert recipients_to_update[1] == example_queue_table_data[1]
    assert example_queue_table_data[2] not in recipients_to_update


def test_get_recipients_to_update_no_matches(
    mock_connection,
    mock_cursor,
    example_message_references,
    caplog,
):
    caplog.set_level(logging.INFO)
    mock_cursor.fetchall.return_value = [
        ("123456789", "false_message_id", "ABC"),
        ("987654321", "false_message_id", "ABC"),
        ("123987456", "example_message_id", "ABC"),
    ]
    mock_cursor.description = [
        ("NHS_NUMBER",),
        ("MESSAGE_ID",),
        ("BATCH_ID",),
    ]

    recipients_to_update = lf.get_recipients_to_update(
        mock_connection, example_message_references
    )

    assert len(recipients_to_update) == 0


def test_patient_to_update_valid_match(
    example_patient_to_update_dict, mock_connection, mock_cursor
):
    """Test that a valid patient is returned."""
    message_id, queue_dict = example_patient_to_update_dict
    data = lf.patient_to_update(mock_connection, message_id, queue_dict)

    mock_var = mock_cursor.var(int)
    mock_var.getvalue.return_value = 0

    assert data["in_val1"] == "456"
    assert data["in_val2"] == "123"
    assert data["in_val3"] == "read"
    assert data["out_val"] == mock_var


def test_patient_to_update_valid_no_match(
    example_patient_to_update_dict, mock_connection
):
    """Test that False is returned if no match is found."""
    message_id, queue_dict = example_patient_to_update_dict
    message_id = "XYZ"
    data = lf.patient_to_update(mock_connection, message_id, queue_dict)

    assert not data


def test_update_message_status_valid(
    mock_connection, example_recipient_to_update, caplog
):
    caplog.set_level(logging.INFO)

    response_code = lf.update_message_status(
        mock_connection, example_recipient_to_update
    )

    assert caplog.records[0].levelname == "INFO"
    assert (
        caplog.records[0].message == f"Record to update: {example_recipient_to_update}"
    )

    assert response_code == 0
    assert caplog.records[1].levelname == "INFO"
    assert caplog.records[1].message == "Message status updated successfully"


def test_update_message_status_invalid(
    mock_connection, mock_var, example_recipient_to_update, caplog
):
    caplog.set_level(logging.INFO)

    example_recipient_to_update["MESSAGE_ID"] = "false_message_id"
    mock_var.getvalue.return_value = 1

    response_code = lf.update_message_status(
        mock_connection, example_recipient_to_update
    )

    assert caplog.records[0].levelname == "INFO"
    assert (
        caplog.records[0].message == f"Record to update: {example_recipient_to_update}"
    )

    assert response_code == 1
    assert caplog.records[1].levelname == "ERROR"
    assert (
        caplog.records[1].message
        == f'Failed to update message status for message_id: {example_recipient_to_update["MESSAGE_ID"]}'
    )


def test_update_message_statuses_valid(
    mock_connection,
    example_recipients_to_update,
    caplog,
):
    caplog.set_level(logging.INFO)

    response_codes = lf.update_message_statuses(
        mock_connection, example_recipients_to_update
    )

    assert caplog.records[0].levelname == "INFO"
    assert (
        caplog.records[0].message
        == f"Record to update: {example_recipients_to_update[0]}"
    )
    assert (
        caplog.records[1].message
        == f"Record to update: {example_recipients_to_update[1]}"
    )

    assert response_codes == [
        {
            "message_id": example_recipients_to_update[0]["MESSAGE_ID"],
            "status": "updated",
        },
        {
            "message_id": example_recipients_to_update[1]["MESSAGE_ID"],
            "status": "updated",
        },
    ]


def test_update_message_statuses_invalid(
    mock_connection,
    mock_cursor,
    example_recipients_to_update,
    caplog,
):
    caplog.set_level(logging.ERROR)
    mock_cursor.var.return_value.getvalue.return_value = 1

    response_codes = lf.update_message_statuses(
        mock_connection, example_recipients_to_update
    )

    assert caplog.records[0].levelname == "ERROR"
    assert (
        caplog.records[0].message
        == f"Failed to update message status for message_id: {example_recipients_to_update[0]['MESSAGE_ID']}"
    )
    assert (
        caplog.records[1].message
        == f"Failed to update message status for message_id: {example_recipients_to_update[1]['MESSAGE_ID']}"
    )

    assert response_codes == []
