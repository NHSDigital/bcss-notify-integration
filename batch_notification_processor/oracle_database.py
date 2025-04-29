from contextlib import contextmanager
import logging
from typing import Optional
import oracledb
import os


from recipient import Recipient


class DatabaseConnectionError(Exception):
    """Exception raised when an error occurs connecting to the database."""


class DatabaseFetchError(Exception):
    """Exception raised when an error occurs fetching data from the database."""


class OracleDatabase:
    def __init__(self):
        self.connection: Optional[oracledb.Connection] = None
        self.db_config = self.connection_params()

    def connect(self):
        if not self.connection:
            try:
                self.connection = oracledb.connect(**self.db_config)
            except oracledb.Error as e:
                logging.error("Error connecting to Oracle database: %s", e)
                raise DatabaseConnectionError(f"Failed to connect to the database. {e}") from e
        return self.connection

    def disconnect(self):
        """Closes the connection to the database."""
        if self.connection:
            try:
                self.connection.close()
                logging.info("Connection to Oracle database closed successfully.")
            except oracledb.Error as e:
                logging.error("Error closing the connection: %s", e)
                raise
            finally:
                self.connection = None

    @contextmanager
    def cursor(self):
        if not self.connection:
            self.connect()

        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
        finally:
            if cursor:
                cursor.close()

    def get_routing_plan_id(self, batch_id: str):
        with self.cursor() as cursor:
            try:
                result = cursor.callfunc("PKG_NOTIFY_WRAP.f_get_next_batch", oracledb.STRING, [batch_id])
                self.connection.commit()
                return result
            except oracledb.Error as e:
                logging.error("Error calling PKG_NOTIFY_WRAP.f_get_next_batch: %s", e)
                raise

    def get_recipients(self, batch_id: str) -> list[Recipient]:
        recipient_data = []

        with self.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id",
                    {"batch_id": batch_id},
                )
                recipient_data = cursor.fetchall()
            except oracledb.Error as e:
                logging.error("Error executing query: %s", e)

        return [Recipient(rd) for rd in recipient_data]

    def update_recipient(self, recipient: Recipient, attr: str):
        attr = attr.lower()
        if attr not in ["message_id", "message_status"]:
            raise ValueError(f"Invalid attribute for Recipient update: {attr}")

        with self.cursor() as cursor:
            try:
                cursor.execute(
                    (
                        "UPDATE v_notify_message_queue "
                        f"SET {attr} = :{attr} "
                        "WHERE nhs_number = :nhs_number"
                    ),
                    {
                        attr: getattr(recipient, attr),
                        "nhs_number": recipient.nhs_number
                    },
                )
                self.connection.commit()
            except oracledb.Error as e:
                logging.error("Error updating recipient: %s", e)
                self.connection.rollback()
                raise

    def update_message_id(self, recipient: Recipient):
        self.update_recipient(recipient, "message_id")

    def update_message_status(self, recipient: Recipient):
        self.update_recipient(recipient, "message_status")

    @staticmethod
    def connection_params():
        username = os.getenv("DATABASE_USER")
        password = os.getenv("DATABASE_PASSWORD")

        return {
            "user": username,
            "password": password,
            "dsn": f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_SID')}",
        }
