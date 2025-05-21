import environment
import json
import os
import pytest
import requests
import requests_mock
from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def clean_env():
    """Fixture to clean up environment variables after each test."""
    yield

    for key in environment.KEYS:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_secrets_response():
    return json.dumps({
        "SecretString": json.dumps({
            "api_key": "test_api_key",
            "application_id": "test_application_id",
            "commgt_base_url": "test_commgt_base_url",
            "database_host": "test_database_host",
            "database_password": "test_database_password",
            "database_port": "test_database_port",
            "database_sid": "test_database_sid",
            "database_user": "test_database_user",
            "oauth_api_key": "test_oauth_api_key",
            "oauth_api_kid": "test_oauth_api_kid",
            "oauth_token_url": "test_oauth_token_url",
            "private_key": "test_private_key"
        })
    })


def test_seed(monkeypatch, mock_secrets_response):
    """Test the seed function to ensure it populates environment variables correctly."""
    monkeypatch.setenv("SECRET_ARN", "test_secret_arn")

    with requests_mock.Mocker() as m:
        m.get("http://localhost:2773/secretsmanager/get?secretId=test_secret_arn&versionStage=AWSCURRENT", text=mock_secrets_response)

        environment.seed()

    for key in environment.KEYS:
        assert os.environ[key] == f"test_{key.lower()}"


def test_seed_no_secret_arn(monkeypatch, mock_secrets_response):
    """Test the seed function when SECRET_ARN is not set."""
    monkeypatch.setenv("DATABASE_USER", "test_database_user")

    with requests_mock.Mocker() as m:
        m.get("http://localhost:2773/secretsmanager/get?secretId=test_secret_arn&versionStage=AWSCURRENT", text=mock_secrets_response)

        environment.seed()

    for key in environment.KEYS:
        if key == "DATABASE_USER":
            assert os.environ[key] == "test_database_user"
        else:
            assert key not in os.environ


def test_seed_already_seeded(monkeypatch, mock_secrets_response):
    """Test the seed function when environment is already seeded."""
    monkeypatch.setenv("SECRET_ARN", "test_secret_arn")
    monkeypatch.setenv("ENVIRONMENT_SEEDED", "true")

    with requests_mock.Mocker() as m:
        adapter = m.get("http://localhost:2773/secretsmanager/get?secretId=test_secret_arn&versionStage=AWSCURRENT", text=mock_secrets_response)

        environment.seed()

        assert adapter.call_count == 0
