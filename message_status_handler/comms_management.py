import os
import requests
import logging


def get_read_messages(batch_reference: str) -> dict:
    response = requests.get(
        f"{os.getenv('COMMGT_BASE_URL')}/api/statuses",
        headers={"x-api-key": os.getenv("API_KEY")},
        params={"batchReference": batch_reference, "channel": "nhsapp", "supplierStatus": "read"},
        timeout=10
    )

    if response.status_code == 201:
        return response.json()

    logging.error("Failed to fetch messages that have been read: %s ", response.text)
    return {
        "status": "error", 
        "message": f"Failed to fetch messages that have been read: {response.text}",
        "data": [],
    }
