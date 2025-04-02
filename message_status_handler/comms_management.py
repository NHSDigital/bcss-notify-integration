import os
import requests
import logging

BASE_URL = "http://example.com"
APPLICATION_ID = os.getenv("application_id")
API_KEY = os.getenv("api_key")
SECRET = f"{APPLICATION_ID}.{API_KEY}"

def get_statuses(
    batch_reference: str,
    nhs_number: str
) -> requests.Response:

    headers = {
        "x-api-key": API_KEY,
        "api-host": APPLICATION_ID
    }

    params = {
        "batchReference": batch_reference,
        "nhsNumber": nhs_number
    }

    url = f"{BASE_URL}/statuses"

    response = requests.get(
        url,
        headers=headers,
        params= params,
        timeout=10
    )

    if response.status_code != 201:
        logging.error("Failed to get batch message: %s ", response.json())

    return response
