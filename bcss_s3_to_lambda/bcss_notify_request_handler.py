from auth_manager import AuthManager
from nhs_notify import NHSNotify


class BCSSNotifyRequestHandler:
    """
    Class responsible for handling individual notification requests.
    """

    def __init__(self, token_url, private_key, nhs_notify_base_url, database):
        self.auth_manager = AuthManager(token_url, private_key)
        self.nhs_notify = NHSNotify(nhs_notify_base_url)
        self.db = database

    def send_message(self, batch_id, routing_config_id, participants):
        """
        Send a message to a list of participants.

        Args:
            batch_id (str): The batch id for the batch of message to be sent.
            routing_config_id (str): The routing config/plan id determin the info, type, template, channels of the message.
            participants (list[str]): The list of the participant string NHS numbers.
        """
        if len(participants) == 0:
            return None

        access_token = self.auth_manager.get_access_token()

        batch_message_response = self.nhs_notify.send_batch_message(
            access_token, batch_id, routing_config_id, participants
        )

        return batch_message_response
