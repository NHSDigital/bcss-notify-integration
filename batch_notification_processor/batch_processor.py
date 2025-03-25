import logging
import uuid
import oracledb
from oracle.oracle import (
    DatabaseConnectionError,
    DatabaseFetchError,
    get_connection,
    get_routing_plan_id,
    get_recipients,
    update_recipient,
)


class BatchProcessor:
    SENDING_STATUS = "SENDING"

    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        try:
            self.db = get_connection()
        except DatabaseConnectionError as e:
            logging.error("Error connecting to the database: %s", e)

    def get_routing_plan_id(self):
        routing_plan_id = get_routing_plan_id(self.db, self.batch_id)

        if not routing_plan_id:
            logging.error("Failed to fetch routing plan ID.")
            raise DatabaseFetchError("Failed to fetch routing plan ID.")

        return routing_plan_id

    def get_recipients(self):
        recipients = []
        logging.info("Self.db: %s", self.db)
        logging.info("Self.batch_id: %s", self.batch_id)
        try:
            recipients = get_recipients(self.db, self.batch_id)
            logging.info("Recipients: %s", recipients)
            if not recipients:
                logging.error("Failed to fetch recipients.")
                raise DatabaseFetchError("Failed to fetch recipients.")
        except oracledb.Error as e:
            logging.error({"error": str(e)})

        for recipient in recipients:
            recipient.message_id = self.generate_message_reference()
            recipient.message_status = "REQUESTED"
            update_recipient(self.db, recipient)

        return recipients

    def mark_batch_as_sent(self, recipients):
        for recipient in recipients:
            recipient.message_status = "SENT"
            update_recipient(self.db, recipient)

    @staticmethod
    def generate_message_reference():
        return str(uuid.uuid4())
