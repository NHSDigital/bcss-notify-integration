import json
import os
import logging
import boto3
import oracledb

PORT = os.getenv("port")
SID = os.getenv("sid")
BCSS_SECRET_NAME = os.getenv("bcss_secret_name")
BCSS_HOST = os.getenv("bcss_host")
REGION_NAME = os.getenv("region_name")


class DatabaseConnectionError(Exception):
    """Exception raised when an error occurs connecting to the database."""


class DatabaseFetchError(Exception):
    """Exception raised when an error occurs fetching data from the database."""


def create_oracle_connection(client):
    try:
        get_secret_value_response = client.get_secret_value(SecretId=BCSS_SECRET_NAME)

        secret = json.loads(get_secret_value_response["SecretString"])
        try:
            db_user = secret["username"]
            db_password = secret["password"]
        except KeyError as e:
            logging.error("Error Connecting to Database: %s", e)
            return {"statusCode": 500, "body": f"Error Connecting to Database: {e}"}

        dsn_tns = oracledb.makedsn(BCSS_HOST, PORT, SID)
        connection = oracledb.connect(user=db_user, password=db_password, dsn=dsn_tns)

        return connection
    except oracledb.Error as e:
        logging.error("Error connecting to Oracle database: %s", e)
        raise DatabaseConnectionError(f"Failed to connect to the database. {e}") from e


def get_connection():
    session = boto3.Session()
    client = session.client(service_name="secretsmanager", region_name=REGION_NAME)
    connection = create_oracle_connection(client)
    return connection


def get_cursor(connection):
    return connection.cursor()


def get_queue_table_records(connection, logger):
    cursor = connection.cursor()
    cursor = get_cursor(connection)
    try:
        cursor.execute(
            cursor,
            "select NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS from V_NOTIFY_MESSAGE_QUEUE",
        )

        columns = [col[0] for col in cursor.description]
        queue_data = cursor.fetchall()

        if not queue_data:
            raise TypeError("No data found in queue table")

        queue_dict = [dict(zip(columns, row)) for row in queue_data]
        close_cursor(cursor)
        return queue_dict
    except Exception as e:
        logger.error(f"Error reading queue table to dict: {e}")
        raise


def call_update_message_status(connection, data):
    cursor = get_cursor(connection)
    response_code = 1
    var = cursor.var(int)
    cursor.execute(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )
    response_code = var.getvalue()
    close_cursor(cursor)

    return response_code


def rollback_changes(connection):
    connection.rollback()


def commit_changes(connection):
    connection.commit()


def close_connection(connection):
    connection.close()


def close_cursor(cursor):
    cursor.close()
