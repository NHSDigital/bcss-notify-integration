"""Lambda function to process and send batch notifications via NHS Notify service."""

import json
import logging
import os
import uuid
import boto3

from bcss_notify_batch_processor import BCSSNotifyBatchProcessor


def initialise_logger() -> logging.Logger:
    """Configure logging for the Lambda function."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def secrets_client():
    return boto3.client("secretsmanager", region_name=os.getenv("region_name"))


def get_secret(secret_name: str) -> dict:
    """
    Retrieve a secret value from AWS Secrets Manager.

    Args:
        secret_name: Name of the secret to retrieve

    Returns:
        dict: Parsed secret value
    """

    response = secrets_client().get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def db_config():
    db_secret = get_secret(os.getenv("secret_arn"))

    return {
        "user": db_secret["username"],
        "password": db_secret["password"],
        "dsn": f"{os.getenv('host')}:{os.getenv('port')}/{os.getenv('sid')}",
    }


def lambda_handler(_event: dict, _context: object) -> None:
    """
    AWS Lambda handler to process and send batch notifications.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context
    """
    logger = initialise_logger()
    logger.info("Lambda function has started.")

    # Initialize processors
    batch_processor = BCSSNotifyBatchProcessor(db_config())

    # Generate unique batch ID
    batch_id = str(uuid.uuid4())
    logger.debug("Generated batch ID: %s", batch_id)

    logger.info("Getting participants...")
    participants = batch_processor.get_participants(batch_id)
    logger.info("participants:\n%s", participants)
