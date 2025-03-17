import logging
import uuid
import oracledb
from oracle_database import OracleDatabase, DatabaseConnectionError, DatabaseFetchError

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


class BatchProcessor:
    def __init__(self, batch_id: str, db_config: dict):
        self.batch_id = batch_id
        self.db = OracleDatabase(db_config["dsn"], db_config["user"], db_config["password"])
        try:
            self.db.connect()
        except DatabaseConnectionError as e:
            logging.error("Error connecting to the database: %s", e)

    def get_routing_plan_id(self):
        routing_plan_id = self.db.get_routing_plan_id(self.batch_id)

        if not routing_plan_id:
            logging.error("Failed to fetch routing plan ID.")
            raise DatabaseFetchError("Failed to fetch routing plan ID.")

        return routing_plan_id

    def get_recipients(self):
        recipients = []

        try:
            recipients = self.db.get_recipients(self.batch_id)
            if not recipients:
                logging.error("Failed to fetch recipients.")
                raise DatabaseFetchError("Failed to fetch recipients.")
        except oracledb.Error as e:
            logging.error({"error": str(e)})

        for recipient in recipients:
            recipient.message_reference = self.generate_message_reference()
            recipient.message_status = "REQUESTED"
            self.db.update_recipient(recipient)

        return recipients

    def mark_batch_as_sent(self, recipients):
        for recipient in recipients:
            recipient.message_status = "SENT"
            self.db.update_recipient(recipient)

    @staticmethod
    def generate_message_reference():
        return str(uuid.uuid4())
