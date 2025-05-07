import logging
import hashlib
import time
import uuid
import oracledb
import oracle_database


class RecipientsNotFoundError(Exception):
    """Raised when no recipients are found for the batch"""


class BatchProcessor:
    SENDING_STATUS = "sending"

    def __init__(self, batch_id: str):
        self.batch_id = batch_id

    def get_routing_plan_id(self):
        routing_plan_id = oracle_database.get_routing_plan_id(self.batch_id)

        if not routing_plan_id:
            logging.error("Failed to fetch routing plan ID.")
            raise Exception("Failed to fetch routing plan ID.")

        return routing_plan_id

    def get_recipients(self):
        recipients = []

        try:
            recipients = oracle_database.get_recipients(self.batch_id)
            if not recipients:
                logging.error("Failed to fetch recipients.")
                raise RecipientsNotFoundError("Failed to fetch recipients.")
        except oracledb.Error as e:
            logging.error({"error": str(e)})

        for recipient in recipients:
            recipient.message_id = self.generate_message_reference()
            oracle_database.update_message_id(recipient)

        return recipients

    def mark_batch_as_sent(self, recipients):
        for recipient in recipients:
            recipient.message_status = self.SENDING_STATUS
            oracle_database.update_message_status(recipient)

    @staticmethod
    def generate_message_reference():
        str_val = str(time.time())
        return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))
