from contextlib import contextmanager
from typing import Optional
import oracledb


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
            print("Already connected to the database.")
            return

        try:
            self.connection = oracledb.connect(
                user=self.user, password=self.password, dsn=self.dsn
            )
            print("Connection to Oracle database established successfully.")
        except oracledb.Error as e:
            print(f"Error connecting to Oracle database: {e}")
            raise

    def disconnect(self):
        """Closes the connection to the database."""
        if self.connection:
            try:
                self.connection.close()
                print("Connection to Oracle database closed successfully.")
            except oracledb.Error as e:
                print(f"Error closing the connection: {e}")
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
            raise ConnectionError("Database is not connected.")

        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
        except oracledb.Error as e:
            print(f"Error while executing query: {e}")
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
                print(f"Error executing query: {e}")
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
                print("Non-query executed and changes committed.")
            except oracledb.Error as e:
                print(f"Error executing non-query: {e}")
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
                print(f"Error invoking function '{function_name}': {e}")
                raise
