"""Lambda function to monitor Oracle tablespace utilisation and send alerts."""

import json
import logging
import os
import boto3
from ..oracle.oracle import (
    get_connection,
    get_cursor,
    query_tablespace_utilisation,
    close_cursor,
    close_connection,
)

# Constants for environment variables
HOST = os.getenv("host")  # Database host
PORT = os.getenv("port")  # Database port
SID = os.getenv("sid")  # Database SID
TABLESPACE_NAME = os.getenv("tablespace")  # Target tablespace
SECRET_NAME = os.getenv("secret_name")  # AWS secret name
REGION_NAME = os.getenv("region_name")  # AWS region
TS_THRESHOLD = int(os.getenv("ts_threshold", "85"))  # Tablespace threshold percentage

# Initialize AWS client
SECRETS_CLIENT = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


def lambda_handler(_event: dict, _context: object) -> dict:
    """
    AWS Lambda handler to check Oracle tablespace utilisation.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context

    Returns:
        dict: Response containing status code and execution results
    """
    cursor = None
    connection = None

    try:
        logging.info("Starting lambda execution")
        connection = get_connection()
        cursor = get_cursor(connection)
        logging.info("Connected to database: %s", SID)
        logging.info("Database Version: %s", connection.version)
        logging.info("Fetching Utilization of tablespace: %s", TABLESPACE_NAME)

        # Query tablespace utilisation
        response = query_tablespace_utilisation(cursor, TABLESPACE_NAME, TS_THRESHOLD)
        return response

    except Exception as err:
        logging.error("Error: %s", str(err))
        return {"statusCode": 500, "body": json.dumps({"error": str(err)})}

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)
