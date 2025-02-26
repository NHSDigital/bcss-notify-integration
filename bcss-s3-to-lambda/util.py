import uuid
import jwt
from datetime import datetime, timezone, timedelta

from NotifyMessageQueue import NotifyMeesageQueue


class Util:

    @staticmethod
    def generate_single_message_request_body(
        recipient: str, routing_config_id: str
    ) -> dict:
        body = {
            "data": {
                "type": "Message",
                "attributes": {"routingPlanId": routing_config_id},
            }
        }

        body["data"]["attributes"].update(Util.generate_message(recipient))

        return body

    @staticmethod
    def generate_batch_message_request_body(
        routing_config_id: str, message_batch_reference: str, recipients
    ) -> dict:
        return {
            "data": {
                "type": "MessageBatch",
                "attributes": {
                    "routingPlanId": routing_config_id,
                    "messageBatchReference": message_batch_reference,
                    "messages": list(map(Util.generate_message, recipients)),
                },
            }
        }

    @staticmethod
    def generate_message(recipient) -> dict:
        return {
            "messageReference": recipient[NotifyMeesageQueue.MESSAGE_ID.value],
            "recipient": {"nhsNumber": recipient[NotifyMeesageQueue.NHS_NUMBER.value]},
            "personalisation": {},
        }

    @staticmethod
    def generate_jwt(
        algorithm: str,
        private_key,
        headers: dict,
        payload: dict,
        expiry_minutes: int = None,
    ) -> str:
        if expiry_minutes:
            expiry_date = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            payload["exp"] = expiry_date

        return jwt.encode(payload, private_key, algorithm, headers)

    @staticmethod
    def get_private_key(private_key_path: str) -> str:
        with open(private_key_path, "r", encoding="utf-8") as f:
            private_key = f.read()
            return private_key