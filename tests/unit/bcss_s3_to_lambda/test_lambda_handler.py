from unittest.mock import MagicMock, patch
from lambda_function import (
        lambda_handler, initialise_logger, secrets_client, 
        get_secret, db_config, generate_batch_id
)
import boto3
import logging


@patch("lambda_function.generate_batch_id", return_value="b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3")
@patch("lambda_function.BCSSNotifyBatchProcessor", autospec=True)
def test_lambda_handler(mock_bcss_notify_batch_processor, generate_batch_id, monkeypatch):
    monkeypatch.setenv("host", "host")
    monkeypatch.setenv("port", "port")
    monkeypatch.setenv("sid", "sid")
    secrets_client = MagicMock()
    secrets_client.get_secret_value.return_value = {"SecretString": '{"username": "user", "password": "pass"}'}
    boto3.client = MagicMock(return_value=secrets_client)
    mock_bcss_notify_batch_processor.get_participants.return_value = [{"nhs_number": "1234567890"}]

    lambda_handler({}, {})

    mock_bcss_notify_batch_processor.assert_called_once_with(
        "b3b3b3b3-b3b3-b3b3b3b3-b3b3b3b3b3b3",
        {"dsn": "host:port/sid", "user": "user", "password": "pass"}
    )
    mock_bcss_notify_batch_processor.return_value.get_participants.assert_called_once()


def test_initialise_logger():
    mock_logger = MagicMock()
    mock_stream_handler = MagicMock()
    logging.getLogger = MagicMock(return_value=mock_logger)
    logging.StreamHandler = MagicMock(return_value=mock_stream_handler)

    logger = initialise_logger()
    assert logger == mock_logger

    mock_logger.setLevel.assert_called_once_with(logging.INFO)
    mock_logger.addHandler.assert_any_call(mock_stream_handler)


def test_secrets_client(monkeypatch):
    boto3.client = MagicMock()
    monkeypatch.setenv("region_name", "us-east-1")

    assert secrets_client() == boto3.client("secretsmanager", region_name="us-east-1")


def test_get_secret():
    secrets_client = MagicMock()
    secrets_client.get_secret_value.return_value = {"SecretString": '{"username": "user", "password": "pass"}'}
    boto3.client = MagicMock(return_value=secrets_client)

    assert get_secret("test") == {"username": "user", "password": "pass"}


def test_db_config(monkeypatch):
    monkeypatch.setenv("username", "user")
    monkeypatch.setenv("password", "pass")
    monkeypatch.setenv("host", "host")
    monkeypatch.setenv("port", "port")
    monkeypatch.setenv("sid", "sid")
    config = db_config()
    assert config == {"user": "user", "password": "pass", "dsn": "host:port/sid"}
