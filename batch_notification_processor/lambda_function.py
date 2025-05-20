"""Lambda function to process and send batch notifications via NHS Notify service."""

import batch_processor
import environment
import logging as pylogging
import os
from communication_management import CommunicationManagement

logging = pylogging.getLogger()
logging.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def lambda_handler(_event: dict, _context: object) -> dict:
    """
    AWS Lambda handler to process and send batch notifications.
    """
    logging.info("Lambda function has started.")

    environment.seed()

    batch_id, routing_plan_id, recipients = batch_processor.next_batch()
    batches = [batch_id]

    while routing_plan_id and recipients:
        logging.info("Batch ID: %s, Routing plan ID: %s, Recipients: %s", batch_id, routing_plan_id, recipients)

        response = CommunicationManagement().send_batch_message(
            batch_id, routing_plan_id, recipients
        )

        if response.status_code == 201:
            batch_processor.mark_batch_as_sent(batch_id)
            batches.append(batch_id)
            logging.info("Batch %s sent successfully to %s recipients.", batch_id, len(recipients))
        else:
            logging.error("Batch %s failed to send. Status code: %s. Response: %s", batch_id, response.status_code, response.text)

        batch_id, routing_plan_id, recipients = batch_processor.next_batch()

    logging.info("Lambda function has completed processing. Batches sent: %s", batches)

    return {
        "status": "complete",
        "message": f"Processed batches: {batches}",
    }
