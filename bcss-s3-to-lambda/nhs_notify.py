from util import Util

import uuid
import requests


class NHSNotify:

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def send_single_message(
        self,
        access_token: str,
        routing_config_id: str,
        recipient: str,
    ) -> dict:
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        request_body: dict = Util.generate_single_message_request_body(
            recipient, routing_config_id
        )

        url = f"{self.base_url}/v1/messages"

        return requests.request(
            'POST', url,
            headers=headers,
            json=request_body,
            timeout=10
        )

    def send_batch_message(
        self,
        access_token: str,
        batch_id: str,
        routing_config_id: str,
        recipients: list[list[any]],
    ) -> dict:
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        request_body: dict = Util.generate_batch_message_request_body(
            routing_config_id, batch_id, recipients
        )

        url = f"{self.base_url}/v1/message-batches"

        response: dict = requests.request(
            'POST', url,
            headers=headers,
            json=request_body,
            timeout=10
        ).json()

        return response

    def get_message_status(self, access_token: str, message_id: str) -> dict:
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        url = f"{self.base_url}/v1/messages/{message_id}"

        response = requests.request(
            'GET',
            url,
            headers=headers,
            timeout=10
        )

        return response.json()

    def get_nhs_account_details(
        self, access_token: str, ods_code: str, page_number: str
    ):
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        params: dict = {"ods-organisation-code": ods_code, "page": page_number}

        url = f"{self.base_url}/channels/nhsapp/accounts"

        response = requests.request(
            'GET',
            url,
            headers=headers,
            params=params,
            timeout=10
        )

        return response.json()
