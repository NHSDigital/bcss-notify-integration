import boto3
import json
import hashlib
import hmac
import logging
import os
import requests
import bcss_notify_callback.sql as sql
import oracle_connection as db
from bcss_notify_callback.patients_to_update import patient_to_update
from typing import Dict, Any

REGION_NAME = os.getenv("region_name")
logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()


def generate_hmac_signature(secret: str, body: str) -> str:
    """Generate HMAC-SHA256 signature for request body."""
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


def validate_signature(received_signature: str, secret: str, body: str) -> bool:
    """Validate received HMAC-SHA256 signature."""
    expected_signature = generate_hmac_signature(secret, body)
    return hmac.compare_digest(received_signature, expected_signature)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda function to handle NHS Notify callbacks."""
    logger.info("Lambda function has started with event: %s", event)

    try:

        headers = event.get("headers", {})
        body = event.get("body", "")

        api_key = headers.get("x-api-key")
        received_signature = headers.get("x-hmac-sha256-signature")

        expected_api_key = os.getenv("NHS_NOTIFY_API_KEY")
        application_id = os.getenv("NHS_NOTIFY_APPLICATION_ID")
        if not api_key or api_key != expected_api_key:
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Unauthorized: Invalid API Key"}),
            }

        logger.info("API key present and is matching")

        secret = f"{application_id}.{expected_api_key}"
        if not received_signature or not validate_signature(
            received_signature, secret, body
        ):
            return {
                "statusCode": 403,
                "body": json.dumps({"message": "Forbidden: Invalid HMAC Signature"}),
            }

        logger.info("Secret is valid")

        try:
            body_data = json.loads(body)
            logger.debug("Body data: %s", body_data)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Invalid JSON"}),
            }

        idempotency_key = body_data["data"][0]["meta"]["idempotencyKey"]
        logger.debug("Idempotency key: %s", idempotency_key)
        if not idempotency_key:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Missing idempotencyKey"}),
            }

        logger.info("Idempotency key present")

        if is_duplicate_request(idempotency_key):
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Duplicate request: Already processed"}),
            }
        logger.info("Idempotency key not duplicate")

        # Refactor for Comm Management API Endpoint
        # payload = json.loads(event)
        # batch_id = payload["batch_id"]
        # connection = db.get_connection()

        # message_references = get_statuses_from_communication_management_api(batch_id)
        # recipients_to_update = get_recipients_to_update(connection, message_references)
        # response_codes = update_message_statuses(connection, recipients_to_update)
        # Refactor ^

        # Refactor for Notify API Endpoint
        connection = db.get_connection()
        logger.info("Connected to BCSS Database")
        message_id = get_statuses_from_notify_api(body_data)
        logger.info("Message ID: %s", message_id)
        queue_dict = sql.read_queue_table_to_dict(connection, logger)
        recipient_to_update = patient_to_update(connection, message_id, queue_dict)
        logger.debug("Recipient to update: %s", recipient_to_update)
        response_code = update_message_status(connection, recipient_to_update)

        # db.commit_changes(connection)

        db.close_cursor(connection.cursor())
        db.close_connection(connection.close())

        ## Comms Management API return
        # return {
        #     "statusCode": 200,
        #     "body": json.dumps(
        #         {
        #             "message": "Callback processed successfully",
        #             "data": payload,
        #             "message_reference": message_references,
        #             "bcss_response": response_codes,
        #         }
        #     ),
        # }

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Callback processed successfully",
                    "data": body_data,
                    "message_reference": message_id,
                    "bcss_response": (
                        response_code if response_code else "No updates made"
                    ),
                }
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Internal Server Error: {str(e)}"}),
        }


def is_duplicate_request(idempotency_key: str) -> bool:
    """Check if the request has already been processed based on the idempotency key."""
    return False


def process_callback(data: Dict[str, Any]) -> None:
    """Process the callback data."""
    try:

        callback_id = data[0]["attributes"]["messageReference"]

        if not callback_id:
            raise ValueError("Missing messageReference in callback data")

        return callback_id

    except (KeyError, ValueError) as e:
        logger.error(f"Error processing callback: {e}")
        raise


def get_message_references(response, message_references):
    try:
        # Depends on what the response from comms management API looks like
        for item in response:
            message_reference = item[0]["attributes"]["messageReference"]
            if not message_reference:
                raise ValueError("Missing messageReference in API data")
            message_references.append(message_reference)

        return message_references

    except (KeyError, ValueError) as e:
        logger.error(f"Error processing API response JSON: {e}")
        raise


def get_statuses_from_communication_management_api(batch_id):
    try:
        message_references = []
        response = requests.get(
            f"{os.getenv('communication_management_api_url')}/api/statuses/{batch_id}"
        )
        if response.status_code == 200:
            message_references = get_message_references(
                response.json(), message_references
            )
            return message_references
    except Exception as e:
        logger.error(
            f"Failed to get statuses from Communication Management API: {str(e)}"
        )


def get_statuses_from_notify_api(data):
    """Process the callback data."""
    try:

        callback_id = data[0]["attributes"]["messageReference"]

        if not callback_id:
            raise ValueError("Missing messageReference in callback data")

        return callback_id

    except (KeyError, ValueError) as e:
        logger.error(f"Error processing callback: {e}")
        raise


def get_recipients_to_update(connection, message_references):
    cursor = db.get_cursor(connection)

    existing_recipients = sql.read_queue_table_to_dict(cursor)

    db.close_cursor(cursor)

    recipients_to_update = []

    for message_reference in message_references:
        for recipient in existing_recipients:
            if message_reference == recipient["MESSAGE_ID"]:
                recipients_to_update.append(recipient)

    return recipients_to_update


def update_message_statuses(connection, recipients_to_update):
    cursor = db.get_cursor(connection)

    response_codes = []
    for recipient_to_update in recipients_to_update:
        logger.info("Record to update: %s", recipient_to_update)
        response_code = sql.call_update_message_status(cursor, recipient_to_update)
        message_id = recipient_to_update["MESSAGE_ID"]

        if response_code == 0:
            response_codes.append({"message_id": message_id, "status": "updated"})
        else:
            logger.error(
                f"Failed to update message status for message_id: {message_id}"
            )

    db.commit_changes(connection)
    db.close_cursor(cursor)
    db.close_connection(connection)

    return response_codes


def update_message_status(connection, recipient_to_update):
    cursor = db.get_cursor(connection)

    logger.info("Record to update: %s", recipient_to_update)
    response_code = sql.call_update_message_status(cursor, recipient_to_update)
    message_id = recipient_to_update["MESSAGE_ID"]

    if response_code == 0:
        logger.info("Message status updated successfully")
    else:
        logger.error(f"Failed to update message status for message_id: {message_id}")

    # db.commit_changes(connection)
    db.close_cursor(cursor)
    db.close_connection(connection)

    return response_code
