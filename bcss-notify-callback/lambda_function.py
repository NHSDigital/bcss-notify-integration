import boto3
import json
import logging
import os
import requests
import sql as sql
from oracle_connection import oracle_connection
from typing import Dict, Any

REGION_NAME = os.getenv("region_name")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda function to update BCSS message statuses."""

    logging.info("Event: ", event)

    try:
        # Event payload looks like: { "batch_id": "1234" }
        payload = json.loads(event)
        batch_id = payload["batch_id"]
        connection = get_connection()

        # TODO: Make connection the responsibility of the oracle/sql module
        if connection is None:
            raise Exception("Failed to connect to BCSS Database")

        message_references = get_statuses_from_communication_management_api(batch_id)

        recipients_to_update = get_recipients_to_update(connection, message_references)

        response_codes = update_message_statuses(connection, recipients_to_update, message_references)

        connection.close()

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Callback processed successfully",
                    "data": payload,
                    "message_references": message_references,
                    "bcss_responses": response_codes,
                }
            )
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Internal Server Error: {str(e)}"})
        }


# TODO: The oracle/sql module should be responsible for making a db connection
def get_connection():
    client = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)
    connection = oracle_connection(client)
    logging.info("Connected to BCSS Database")

    return connection


def get_statuses_from_communication_management_api(batch_id):
    message_references = []
    try:
        response = requests.get(f"{os.getenv('communication_management_api_url')}/api/statuses/{batch_id}")
        if response.status_code == 200:
            # TODO: Implement get_message_references
            message_references = get_message_references(response.json())
    except Exception as e:
        logging.error(f"Failed to get statuses from Communication Management API: {str(e)}")

    return message_references


# TODO: The oracle/sql module should be responsible for getting a connection
# assigning a cursor from the connection and closing the cursor and connection
def get_recipients_to_update(connection, message_references):
    cursor = connection.cursor()

    existing_recipients = sql.read_queue_table_to_dict(cursor)

    cursor.close()

    recipients_to_update = []

    for message_reference in message_references:
        for recipient in existing_recipients:
            if message_reference == recipient["MESSAGE_ID"]:
                recipients_to_update.append(recipient)

    return recipients_to_update


# TODO: The oracle/sql module should be responsible for making a db connection
# assigning a cursor from the connection and closing the cursor and connection
def update_message_statuses(connection, recipients_to_update):
    cursor = connection.cursor()

    response_codes = []
    for recipient_to_update in recipients_to_update:
        logging.info('Record to update:', recipient_to_update)
        response_code = sql.call_update_message_status(cursor, recipient_to_update)
        message_id = recipient_to_update["MESSAGE_ID"]

        if response_code == 0:
            response_codes.append({"message_id": message_id, "status": "updated"})
        else:
            logging.error(f"Failed to update message status for message_id: {message_id}")

    # Commit the changes
    # connection.commit()

    cursor.close()
    connection.close()

    return response_codes
