import hashlib
import hmac
import pytest
from bcss_notify_callback.lambda_function import (
    generate_hmac_signature,
    validate_signature,
)


class TestLambdaFunction:
    # Env variables for tests
    def test_initialization(
        self,
    ):
        assert 1 == 0

    @pytest.fixture
    def setup(self, monkeypatch):
        monkeypatch.setenv("APPLICATION_ID", "application_id")
        monkeypatch.setenv("NOTIFY_API_KEY", "api_key")

    def test_generate_hmac_signature_valid(self):
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
