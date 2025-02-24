import hashlib
import hmac
import pytest
from lambda_function import (
    generate_hmac_signature,
    validate_signature,
    process_callback,
)


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

    assert generate_hmac_signature("application_id.api_key", body) == signature


def test_validate_signature_valid(setup):
    """Test that a valid signature passes verification."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert validate_signature(signature, "application_id.api_key", body)


def test_validate_signature_invalid(setup):
    """Test that an invalid signature does not pass verification."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert not validate_signature(signature, "test", body)


# There is a lot of code in this handler, worth breaking down into smaller chunks?
# Came up in discussion to refactor the lambda_handler when connecting to comms management endpoint
# Will become a lot shorter


def test_lambda_handler(setup):
    """Test that the Lambda handler returns the correct response."""
    pass


def test_process_callback_valid(example_callback_response, example_message_reference):
    """Test that a callback is processed correctly."""
    response = process_callback(example_callback_response)

    assert response == example_message_reference


def test_process_callback_invalid_missing_message_reference_value(example_body_data):
    """Test that missing callback_id is handled correctly"""
    with pytest.raises(ValueError):
        example_body_data[0]["attributes"]["messageReference"] = ""
        process_callback(example_body_data)


def test_process_callback_invalid_missing_attribute_index(example_body_data):
    """Test that missing messageReference attribute is handled correctly"""
    with pytest.raises(KeyError):
        del example_body_data[0]["attributes"]["messageReference"]
        process_callback(example_body_data)
