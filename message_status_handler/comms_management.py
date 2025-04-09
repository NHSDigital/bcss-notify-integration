import os
import requests
import logging


def get_read_messages(batch_reference: str) -> dict:
    response = requests.get(
        f"{os.getenv('COMMGT_BASE_URL')}/api/statuses",
        headers={"x-api-key": os.getenv("API_KEY")},
        params={"batchReference": batch_reference, "status": "read"},
        timeout=10
    )

    if response.status_code != 201:
        logging.error("Failed to fetch messages that have been read: %s ", response.json())

    return response.json()
