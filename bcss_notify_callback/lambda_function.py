import hashlib
import hmac
import os
import boto3
import json
import bcss_notify_callback.sql as sql
from bcss_notify_callback.oracle_connection import oracle_connection
from bcss_notify_callback.patients_to_update import patient_to_update
from typing import Dict, Any

REGION_NAME = os.getenv("region_name")


def generate_hmac_signature(secret: str, body: str) -> str:
    """Generate HMAC-SHA256 signature for request body."""
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


def validate_signature(received_signature: str, secret: str, body: str) -> bool:
    """Validate received HMAC-SHA256 signature."""
    expected_signature = generate_hmac_signature(secret, body)
    return hmac.compare_digest(received_signature, expected_signature)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda function to handle NHS Notify callbacks."""

    print("Event: ", event)

    try:
        # Extract headers and body
        headers = event.get("headers", {})
        body = event.get("body", "")

        # # Extract headers
        api_key = headers.get("x-api-key")
        received_signature = headers.get("x-hmac-sha256-signature")

        # Validate API key
        expected_api_key = os.getenv(
            "NHS_NOTIFY_API_KEY"
        )  # Set this in your Lambda environment variables
        application_id = os.getenv(
            "NHS_NOTIFY_APPLICATION_ID"
        )  # Set this in your Lambda environment variables
        if not api_key or api_key != expected_api_key:
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Unauthorized: Invalid API Key"}),
            }

        print("API key present and is matching")

        # Validate HMAC signature
        secret = f"{application_id}.{expected_api_key}"
        if not received_signature or not validate_signature(
            received_signature, secret, body
        ):
            return {
                "statusCode": 403,
                "body": json.dumps({"message": "Forbidden: Invalid HMAC Signature"}),
            }

        print("Secret is valid")

        # Parse body
        try:
            body_data = json.loads(body)
            print("body data: ", body_data)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Invalid JSON"}),
            }

        # Handle idempotency
        idempotency_key = body_data["data"][0]["meta"]["idempotencyKey"]
        print("idempotency_key: ", idempotency_key)
        if not idempotency_key:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Bad Request: Missing idempotencyKey"}),
            }

        print("Idempotency key present")

        # Use an external system (e.g., DynamoDB or Redis) to ensure idempotency
        if is_duplicate_request(idempotency_key):
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Duplicate request: Already processed"}),
            }

        print("Idempotency key not duplicate")

        # Connect to BCSS Database
        client = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)
        connection = oracle_connection(client)
        cursor = connection.cursor()
        print("Connected to BCSS Database")

        # SQL Table read queue table to dict
        queue_dict = sql.read_queue_table_to_dict(cursor)

        # Process the callback data, extract all the message_reference IDs
        message_id = process_callback(body_data)
        print("Message_id: ", message_id)

        # Work out which messages need updating, cross reference the message references from the callback with the queue table dict
        var = cursor.var(int)
        record_to_update = patient_to_update(message_id, queue_dict, var)
        print("Record to update:", record_to_update)

        # Update the record with the matching message_id
        response_code = sql.call_update_message_status(cursor, record_to_update, var)

        # Commit the changes
        # connection.commit()

        cursor.close()
        connection.close()

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
    # Placeholder logic: Implement a proper check using DynamoDB, Redis, or another data store.
    # For example:
    #   - Query DynamoDB with idempotency_key
    #   - If exists, return True; otherwise, store and return False
    return False


def process_callback(data: Dict[str, Any]) -> None:
    """Process the callback data."""
    # Placeholder for processing the callback payload.
    # Implement the required business logic here.
    callback_id = data[0]["attributes"]["messageReference"]
    # Find a way to extract the message references from the body of the message (data.)
    print(callback_id)
    return callback_id
