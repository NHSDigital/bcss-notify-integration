from BaseAPIClient import BaseAPIClient
from Util import Util

import uuid


class NHSNotify:

    def __init__(self, base_url: str) -> None:
        self.api_client = BaseAPIClient(base_url)

    def send_single_message(
        self,
        access_token: str,
        routing_config_id: str,
        recipient: str,
        message_reference: str,
    ) -> dict:
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        requestBody: dict = Util.generate_single_message_request_body(
            recipient, routing_config_id, message_reference
        )

        response: dict = self.api_client.make_request(
            method="POST", endpoint="/v1/messages", json=requestBody, headers=headers
        )
        return response

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

        requestBody: dict = Util.generate_batch_message_request_body(
            routing_config_id, batch_id, recipients
        )

        response: dict = self.api_client.make_request(
            method="POST",
            endpoint="/v1/message-batches",
            json=requestBody,
            headers=headers,
        )
        return response

    def get_message_status(self, access_token: str, message_id: str) -> dict:
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        response: dict = self.api_client.make_request(
            method="GET", endpoint=f"/v1/messages/{message_id}", headers=headers
        )

        return response

    def get_NHS_acccount_details(
        self, access_token: str, ods_code: str, page_number: str
    ):
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "authorization": "Bearer " + access_token,
        }

        params: dict = {"ods-organisation-code": ods_code, "page": page_number}

        response: dict = self.api_client.make_request(
            method="GET",
            endpoint="/channels/nhsapp/accounts",
            headers=headers,
            params=params,
        )

        return response
