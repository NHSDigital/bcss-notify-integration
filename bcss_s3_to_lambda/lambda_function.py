"""Lambda function to process and send batch notifications via NHS Notify service."""

import json
import logging
import os
import uuid
import boto3

from batch_processor import BatchProcessor
from communication_management import CommunicationManagement


def initialise_logger() -> logging.Logger:
    """Configure logging for the Lambda function."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
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


def generate_batch_id():
    return str(uuid.uuid4())


def lambda_handler(_event: dict, _context: object) -> None:
    """
    AWS Lambda handler to process and send batch notifications.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context
    """
    logger = initialise_logger()
    logger.info("Lambda function has started.")

    # Generate unique batch ID
    batch_id = generate_batch_id()
    logger.debug("Generated batch ID: %s", batch_id)

    # Initialize processors
    batch_processor = BatchProcessor(batch_id)

    routing_plan_id = batch_processor.get_routing_plan_id()

    recipients = batch_processor.get_recipients()
    logger.info("recipients:\n%s", recipients)

    response = CommunicationManagement().send_batch_message(
        batch_id, routing_plan_id, recipients
    )

    if response.status_code == 201:
        logger.info("Batch message sent successfully.")
        batch_processor.mark_batch_as_sent(recipients)
    else:
        logger.error(
            "Failed to send batch message. Status code: %s", response.status_code
        )
