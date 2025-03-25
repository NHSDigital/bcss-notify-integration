import hashlib
import hmac
import json
import os
import uuid
import logging
from recipient import Recipient
import requests


class CommunicationManagement:
    def __init__(self) -> None:
        self.base_url = os.getenv("base_url")
        self.application_id = os.getenv("application_id")
        self.api_key = os.getenv("api_key")
        self.secret = f"{self.application_id}.{self.api_key}"

    def send_batch_message(
        self,
        batch_id: str,
        routing_config_id: str,
        recipients: list[Recipient],
    ) -> requests.Response:
        request_body: dict = self.generate_batch_message_request_body(
            routing_config_id, batch_id, recipients
        )

        hmac_signature = self.generate_hmac_signature(request_body)
        logging.info("HMAC signature: %s", hmac_signature)
        headers = {
            "content-type": "application/vnd.api+json",
            "accept": "application/vnd.api+json",
            "x-correlation-id": str(uuid.uuid4()),
            "x-api-key": self.api_key,
            "x-hmac-sha256-signature": hmac_signature,
        }

        url = f"{self.base_url}/api/message/batch"

        response = requests.post(url, headers=headers, json=request_body, timeout=10)

        return response

    def generate_batch_message_request_body(
        self,
        routing_config_id: str,
        message_batch_reference: str,
        recipients: list[Recipient],
    ) -> dict:
        return {
            "data": {
                "type": "MessageBatch",
                "attributes": {
                    "routingPlanId": routing_config_id,
                    "messageBatchReference": message_batch_reference,
                    "messages": [self.generate_message(r) for r in recipients],
                },
            }
        }

    def generate_message(self, recipient) -> dict:
        return {
            "messageReference": recipient.message_id,  # pylint: disable=no-member
            "recipient": {
                "nhsNumber": recipient.nhs_number
            },  # pylint: disable=no-member
            "personalisation": {},
        }

    def generate_hmac_signature(self, request_body: dict) -> str:
        logging.info("Request body: %s", request_body)
        return hmac.new(
            bytes(self.secret, "ASCII"),
            msg=bytes(json.dumps(request_body), "ASCII"),
            digestmod=hashlib.sha256,
        ).hexdigest()
