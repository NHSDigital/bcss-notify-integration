from contextlib import contextmanager
from typing import Optional
import logging
import oracledb

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
        self.dsn = dsn
        self.user = user
        self.password = password
        self.connection: Optional[oracledb.Connection] = None

    def connect(self):
        """Establishes a connection to the database."""
        if self.connection:
            logging.info("Already connected to the database.")
            return

        if (not self.user) or (not self.password) or (not self.dsn):
            logging.error("Missing connection parameters.")
            raise DatabaseConnectionError("Missing connection parameters.")

        try:
            self.connection = oracledb.connect(
                user=self.user, password=self.password, dsn=self.dsn
            )
            logging.info("Connection to Oracle database established successfully.")
            return True
        except oracledb.Error as e:
            logging.error("Error connecting to Oracle database: %s", e)
            raise DatabaseConnectionError("Failed to connect to the database.") from e

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
        """
        Provides a context-managed database cursor.

        :yield: Cursor object for executing SQL queries.
        """
        if not self.connection:
            raise DatabaseConnectionError("Database is not connected.")

        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
        except oracledb.Error as e:
            logging.error("Error while executing query: %s", e)
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query: str, params: Optional[dict] = None):
        """
        Executes a query and returns the results.

        :param query: SQL query to execute
        :param params: Parameters for the SQL query
        :return: Query results as a list of tuples
        """
        with self.cursor() as cursor:
            try:
                cursor.execute(query, params or {})
                results = cursor.fetchall()
                return results
            except oracledb.Error as e:
                logging.error("Error executing query: %s", e)
                raise

    def execute_non_query(self, query: str, params: Optional[dict] = None):
        """
        Executes a non-query SQL statement (INSERT, UPDATE, DELETE).

        :param query: SQL query to execute
        :param params: Parameters for the SQL query
        """
        with self.cursor() as cursor:
            try:
                cursor.execute(query, params or {})
                self.connection.commit()
                logging.info("Non-query executed and changes committed.")
            except oracledb.Error as e:
                logging.error("Error executing non-query: %s", e)
                self.connection.rollback()
                raise

    def call_function(self, function_name: str, return_type: any, params: list):
        """
        Invokes a PL/SQL function directly.

        :param function_name: The name of the function to call
        :param return_type: The return type of the function (e.g., oracledb.NUMBER)
        :param params: List of parameters to pass to the function
        :return: The function's return value
        """
        with self.cursor() as cursor:
            try:
                result = cursor.callfunc(function_name, return_type, params)
                self.connection.commit()
                return result
            except oracledb.Error as e:
                logging.error("Error invoking function %s': %s", function_name, e)
                raise


    def get_next_batch(self, batch_id: str):
        """
        Calls a stored procedure to get the next batch ID.

        :return: The next batch ID
        """
        return self.call_function("PKG_NOTIFY_WRAP.f_get_next_batch", oracledb.NUMBER, [batch_id])


    def get_set_of_participants(self, batch_id: str):
        """
        Calls a stored procedure to get the set of participants for a given batch ID.

        :return: A set of participants
        """
        if not batch_id:
            logging.info("No batch ID provided.")
            return self.execute_query(
                "SELECT * FROM v_notify_message_queue WHERE batch_id IS NULL"
            )

        return self.execute_query(
            "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id",
            {"batch_id": batch_id},
        )
