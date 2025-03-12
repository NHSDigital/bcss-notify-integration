import uuid
import logging
import oracledb
from notify_message_queue import NotifyMessageQueue
from oracle_database import DatabaseConnectionError, DatabaseFetchError

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


class BCSSNotifyBatchProcessor:
    """
    Class responsible for processing batches of participants to notify.
    """

    def __init__(self, database):
        self.db = database
        try:
            self.db.connect()
        except DatabaseConnectionError as e:
            logging.error("Error connecting to the database: %s", e)

    def get_routing_plan_id(self):
        """
        Retrieves the next batch ID from the database.
        """
        routing_plan_id = self.db.get_next_batch()

        if not routing_plan_id:
            logging.error("Failed to fetch routing plan ID.")
            raise DatabaseFetchError("Failed to fetch routing plan ID.")

        return routing_plan_id

    def get_participants(self, batch_id: str):
        """
        Retrieves a list of participants for notification.

        Args:
            batch_id (str): The batch id for the batch of message to be sent.
        """
        participants = []

        try:
            participants = self.db.get_set_of_participants(batch_id)
            if not participants:
                logging.error("Failed to fetch participants.")
                raise DatabaseFetchError("Failed to fetch participants.")
        except oracledb.Error as e:
            logging.error({"error": str(e)})
        finally:
            self.db.disconnect()

        return participants


    def generate_participants_message_reference(self, participants):
        """
        Generate and update the message references for participants.

        Args:
            participants (list[list[any]]): List of participants.
        """
        participants_list = []

        for participant in participants:
            participant_list = list(participant)

            nhs_number = participant_list[NotifyMessageQueue.NHS_NUMBER.value]
            message_reference = str(uuid.uuid4())
            while self.check_message_reference_exists(message_reference):
                logging.info(
                    "Clash detected for UUID %s . Generating a new one...", {message_reference}
                )
                message_reference = str(uuid.uuid4())
            participant_list[NotifyMessageQueue.MESSAGE_ID.value] = message_reference
            self.update_participant_message_reference(nhs_number, message_reference)
            participants_list.append(participant_list)

        return participants_list

    def check_message_reference_exists(self, message_reference: str) -> bool:
        """
        Checks if the given MESSAGE_ID exists.

        :param message_reference: The MESSAGE_ID value to check
        :return: True if the MESSAGE_ID exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM v_notify_message_queue WHERE MESSAGE_ID = :message_reference"
        params = {"message_reference": message_reference}

        try:
            result = self.db.execute_query(query, params)
            count = result[0][0] if result else 0
            return count > 0
        except Exception as e:
            logging.error("Error checking MESSAGE_REF: %s", e)
            raise

    def update_participant_message_reference(
        self, nhs_number: str, message_reference: str
    ):
        """
        Update the MESSAGE_ID for the given participant.

        :param nhs_number: The NHS_NUMBER of the given participant
        :param message_reference: The MESSAGE_ID to update
        """
        try:
            self.db.execute_non_query(
                "UPDATE v_notify_message_queue SET MESSAGE_ID = :message_reference \
                WHERE NHS_NUMBER = :nhs_number",
                {"message_reference": message_reference, "nhs_number": nhs_number},
            )
        except oracledb.Error as e:
            logging.error({"error": str(e)})
        finally:
            self.db.disconnect()
