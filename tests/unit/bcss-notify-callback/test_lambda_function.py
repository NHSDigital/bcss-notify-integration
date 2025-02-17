import hashlib
import hmac
import pytest
from bcss_notify_callback.lambda_function import (
    generate_hmac_signature,
    validate_signature,
)


@pytest.fixture
def setup(self, monkeypatch):
    monkeypatch.setenv("APPLICATION_ID", "application_id")
    monkeypatch.setenv("NOTIFY_API_KEY", "api_key")


def test_generate_hmac_signature_valid(self):
    """Test that an HMAC SHA-256 signature is generated correctly."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert generate_hmac_signature("application_id.api_key", body) == signature


def test_validate_signature_valid(self):
    """Test that a valid signature passes verification."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert validate_signature(signature, "application_id.api_key", body)


def test_validate_signature_invalid(self):
    """Test that an invalid signature does not pass verification."""
    body = "body"
    signature = hmac.new(
        "application_id.api_key".encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    assert not validate_signature(signature, "test", body)


# There is a lot of code in this handler, worth breaking down into smaller chunks?


def test_lambda_handler(self):
    """Test that the Lambda handler returns the correct response."""
    pass


def test_is_duplicate_request_valid(self):
    """Test that a duplicate request is identified correctly."""
    pass


def test_process_callback_valid(self):
    """Test that a callback is processed correctly."""
    pass


def test_process_callback_invalid(self):
    """Test that missing callback_id is handled correctly"""
    pass
