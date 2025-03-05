import json
import hashlib
import hmac
import logging
import os
from typing import Dict, Any
import requests
import sql
import oracle_connection as db
from patients_to_update import patient_to_update


logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


def generate_hmac_signature(secret: str, body: str) -> str:
    """Generate HMAC-SHA256 signature for request body."""
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


def validate_signature(received_signature: str, secret: str, body: str) -> bool:
    """Validate received HMAC-SHA256 signature."""
    expected_signature = generate_hmac_signature(secret, body)
    return hmac.compare_digest(received_signature, expected_signature)


def lambda_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    """AWS Lambda function to handle NHS Notify callbacks."""
    logging.info("Lambda function has started with event: %s", event)

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

        logging.info("API key present and is matching")

        secret = f"{application_id}.{expected_api_key}"
        if not received_signature or not validate_signature(
            received_signature, secret, body
        ):
            return {
                "statusCode": 403,
                "body": json.dumps({"message": "Forbidden: Invalid HMAC Signature"}),
            }

        logging.info("Secret is valid")

        try:
            body_data = json.loads(body)
            logging.debug("Body data: %s", body_data)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Invalid JSON"}),
            }

        idempotency_key = body_data["data"][0]["meta"]["idempotencyKey"]
        logging.debug("Idempotency key: %s", idempotency_key)
        if not idempotency_key:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Missing idempotencyKey"}),
            }

        logging.info("Idempotency key present")

        if is_duplicate_request(idempotency_key):
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Duplicate request: Already processed"}),
            }
        logging.info("Idempotency key not duplicate")

        connection = db.get_connection()
        logging.info("Connected to BCSS Database")
        message_id = get_status_from_notify_api(body_data)
        logging.info("Message ID: %s", message_id)
        queue_dict = sql.read_queue_table_to_dict(connection, logging)
        recipient_to_update = patient_to_update(connection, message_id, queue_dict)
        logging.debug("Recipient to update: %s", recipient_to_update)
        response_code = update_message_status(connection, recipient_to_update)

        db.close_cursor(connection.cursor())
        db.close_connection(connection.close())

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


def is_duplicate_request(_idempotency_key: str) -> bool:
    """Check if the request has already been processed based on the idempotency key."""
    return False


def get_status_from_notify_api(data: Dict[str, Any]):
    """Process the callback data."""
    try:

        message_id = data[0]["attributes"]["messageReference"]

        if not message_id:
            raise ValueError("Missing messageReference in callback data")

        return message_id

    except (KeyError, ValueError) as e:
        logging.error("Error processing callback: %s", e)
        raise


def update_message_status(connection, recipient_to_update):
    cursor = db.get_cursor(connection)

    logging.info("Record to update: %s", recipient_to_update)
    response_code = sql.call_update_message_status(cursor, recipient_to_update)
    message_id = recipient_to_update["MESSAGE_ID"]

    if response_code == 0:
        logging.info("Message status updated successfully")
    else:
        logging.error("Failed to update message status for message_id: %s", message_id)

    # db.commit_changes(connection)
    db.close_cursor(cursor)
    db.close_connection(connection)

    return response_code


def get_message_references(response, message_references):
    try:
        for item in response:
            message_reference = item[0]["attributes"]["messageReference"]

            if not message_reference:
                raise ValueError("Missing Value: 'messageReference' in API data")

            message_references.append(message_reference)

        return message_references

    except KeyError as e:
        logging.error(
            "Error processing API response JSON: Missing Key: %s in API data", e
        )
        raise
    except ValueError as e:
        logging.error("Error processing API response JSON: %s", e)
        raise


def get_statuses_from_communication_management_api(batch_id):
    try:
        message_references = []
        response = requests.get(
            f"{os.getenv('communication_management_api_url')}/api/statuses/{batch_id}"
        )
        response.raise_for_status()
        if response.status_code == 200:
            message_references = get_message_references(
                response.json(), message_references
            )
            return message_references

    except requests.exceptions.HTTPError as e:
        logging.error(
            "Failed to get statuses from Communication Management API: %s", str(e)
        )
        raise
    except Exception as e:
        logging.error(
            "Error processing Communication Management API response: %s", str(e)
        )
        raise


def get_recipients_to_update(connection, message_references):

    existing_recipients = sql.read_queue_table_to_dict(connection, logging)

    recipients_to_update = []

    for message_reference in message_references:
        for recipient in existing_recipients:
            if message_reference == recipient["MESSAGE_ID"]:
                recipients_to_update.append(recipient)

    return recipients_to_update


def update_message_statuses(connection, recipients_to_update):

    response_codes = []
    for recipient_to_update in recipients_to_update:
        logging.info("Record to update: %s", recipient_to_update)
        response_code = sql.call_update_message_status(connection, recipient_to_update)
        message_id = recipient_to_update["MESSAGE_ID"]

        if response_code == 0:
            response_codes.append({"message_id": message_id, "status": "updated"})
        else:
            logging.error(
                "Failed to update message status for message_id: %s", message_id
            )

    db.commit_changes(connection)
    db.close_connection(connection)

    return response_codes
