import comms_management
import json
import logging
import message_status_recorder
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    logging.info("Message status handler started. Event: %s", event)
    try:
        batch_id = event.get("batch_id")
        messages_with_read_status = comms_management.get_read_messages(batch_id)

        logging.info("Messages with read status: %s", messages_with_read_status)

        if len(messages_with_read_status) == 0:
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"message": "No messages with read status found."}
                ),
            }

        bcss_response_codes = message_status_recorder.record_message_statuses(batch_id, messages_with_read_status)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Message status updates successful",
                    "data": messages_with_read_status,
                    "bcss_response": bcss_response_codes,
                }
            ),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Internal Server Error: {str(e)}"}),
        }
