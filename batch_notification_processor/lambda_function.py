"""Lambda function to process and send batch notifications via NHS Notify service."""

import logging
import uuid
from batch_processor import BatchProcessor
from communication_management import CommunicationManagement
from scheduler import Scheduler


def generate_batch_id():
    return str(uuid.uuid4())


def lambda_handler(event: dict, _context: object) -> None:
    """
    AWS Lambda handler to process and send batch notifications.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context
    """
    logging.info("Lambda function has started.")

    # Generate unique batch ID
    batch_id = event.get("batch_id") 

    if not batch_id:
        batch_id = generate_batch_id()

    logging.debug("Batch ID: %s", batch_id)

    # Initialize processors
    batch_processor = BatchProcessor(batch_id)

    routing_plan_id = batch_processor.get_routing_plan_id()

    recipients = batch_processor.get_recipients()
    logging.info("recipients:\n%s", recipients)

    response = CommunicationManagement().send_batch_message(
        batch_id, routing_plan_id, recipients
    )

    if response.status_code == 201:
        logging.info("Batch message sent successfully.")
        batch_processor.mark_batch_as_sent(recipients)
        Scheduler(batch_id).schedule_status_check(os.getenv("SCHEDULE_STATUS_CHECK_MINUTES", 720))
    else:
        logging.error("Failed to send batch message. Status code: %s", response.status_code)
