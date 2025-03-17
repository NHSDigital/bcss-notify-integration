from contextlib import contextmanager
from typing import Optional
import logging
import oracledb

from recipient import Recipient

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


class DatabaseConnectionError(Exception):
    """Exception raised when an error occurs connecting to the database."""


class DatabaseFetchError(Exception):
    """Exception raised when an error occurs fetching data from the database."""


class OracleDatabase:
    """
    A class to manage connections to an Oracle database using python-oracledb.
    Follows good practices for resource management and error handling.
    """

    def __init__(self, dsn: str, user: str, password: str):
        """
        Initializes the OracleDatabase instance.

        :param dsn: The Data Source Name (TNS string or hostname/service name)
        :param user: Database username
        :param password: Database password
        """
        self.dsn: str = dsn
        self.user: str = user
        self.password: str = password
        self.connection: Optional[oracledb.Connection] = None

    def connect(self):
        if self.connection:
            return

        try:
            self.connection = oracledb.connect(
                user=self.user, password=self.password, dsn=self.dsn
            )
        except oracledb.Error as e:
            logging.error("Error connecting to Oracle database: %s", e)
            raise DatabaseConnectionError(f"Failed to connect to the database. {e}") from e

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

    def update_recipient(self, recipient: Recipient):
        with self.cursor() as cursor:
            try:
                cursor.execute(
                    (
                        "UPDATE v_notify_message_queue "
                        "SET MESSAGE_ID = :message_reference, "
                        "MESSAGE_STATUS = :message_status "
                        "WHERE NHS_NUMBER = :nhs_number"
                    ),
                    {
                        "message_reference": recipient.message_reference,
                        "message_status": recipient.message_status,
                        "nhs_number": recipient.nhs_number
                    },
                )
                self.connection.commit()
            except oracledb.Error as e:
                logging.error("Error updating recipient: %s", e)
                self.connection.rollback()
                raise
