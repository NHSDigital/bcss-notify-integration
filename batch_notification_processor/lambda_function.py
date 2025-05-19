"""Lambda function to process and send batch notifications via NHS Notify service."""

import environment
import logging as pylogging
import os
import uuid
from batch_processor import BatchProcessor
from communication_management import CommunicationManagement

logging = pylogging.getLogger()
logging.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def generate_batch_id():
    return str(uuid.uuid4())


def lambda_handler(event: dict, _context: object) -> dict:
    """
    AWS Lambda handler to process and send batch notifications.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context
    """
    logging.info("Lambda function has started.")

    environment.seed()

    # Generate unique batch ID
    batch_id = event.get("batch_id")

    if not batch_id:
        batch_id = generate_batch_id()

    logging.info("Batch ID: %s", batch_id)

    # Initialize processors
    batch_processor = BatchProcessor(batch_id)

    routing_plan_id = batch_processor.get_routing_plan_id()

    recipients = batch_processor.get_recipients()
    logging.info("Processing %s recipients", len(recipients))

    response = CommunicationManagement().send_batch_message(
        batch_id, routing_plan_id, recipients
    )

    if response.status_code == 201:
        logging.info("Batch message sent successfully.")
        batch_processor.mark_batch_as_sent(recipients)
        return {
            "status": "success",
            "message": f"Batch {batch_id} sent successfully.",
        }

    logging.error(
        "Failed to send batch message. Status code: %s. Reason: %s",
        response.status_code,
        response.text
    )

    return {
        "status": "error",
        "message": f"Failed to send batch message. Status code: {response.status_code}",
    }
