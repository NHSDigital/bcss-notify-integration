import uuid
import logging
import oracledb
from oracle_database import OracleDatabase
from notify_message_queue import NotifyMeesageQueue

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


class BCSSNotifyBatchProcessor:
    """
    Class responsible for processing batches of participants to notify.
    """

    def __init__(self, database):
        self.db = database

    def get_participants(self, batch_id: str):
        """
        Retrieves a list of participants for notification.

        Args:
            batch_id (str): The batch id for the batch of message to be sent.
        """
        routing_plan_id = None
        participants = []

        try:
            self.db.connect()
            routing_plan_id = self.db.call_function(
                "PKG_NOTIFY_WRAP.f_get_next_batch",
                oracledb.NUMBER,
                [batch_id],
            )

            if routing_plan_id is None or routing_plan_id == "":
                return [], routing_plan_id


            if not batch_id:
                participants = self.db.execute_query(
                    "SELECT * FROM v_notify_message_queue WHERE batch_id IS NULL"
                )
            else:
                participants = self.db.execute_query(
                    "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id",
                    {"batch_id": batch_id},
                )
        except oracledb.Error as e:
            logging.error({"error": str(e)})
        finally:
            self.db.disconnect()

        if routing_plan_id is None or routing_plan_id == "":
            return [], routing_plan_id

        participants = []

        try:
            self.db.connect()
            participants = self.db.execute_query(
                "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id",
                {"batch_id": batch_id},
            )
        except oracledb.Error as e:
            logging.error({"error": str(e)})
        finally:
            self.db.disconnect()

        participants = self.generate_participants_message_reference(participants)

        return participants, routing_plan_id

    def generate_participants_message_reference(self, participants):
        """
        Generate and update the message references for participants.

        Args:
            participants (list[list[any]]): List of participants.
        """
        participants_list = []

        for participant in participants:
            participant_list = list(participant)

            nhs_number = participant_list[NotifyMeesageQueue.NHS_NUMBER.value]
            message_reference = str(uuid.uuid4())
            while self.check_message_reference_exists(message_reference):
                logging.warning(
                    "Clash detected for UUID %s. Generating a new one...",
                    message_reference,
                )
                message_reference = str(uuid.uuid4())
            participant_list[NotifyMeesageQueue.MESSAGE_ID.value] = message_reference
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
            self.db.connect()
            result = self.db.execute_query(query, params)
            count = result[0][0] if result else 0
            return count > 0
        except Exception as e:
            logging.error("Error checking MESSAGE_REF: %s", e)
            raise

    def update_participant_message_reference(
        self, nhs_number: str, message_referce: str
    ):
        """
        Update the MESSAGE_ID for the given participant.

        :param nhs_number: The NHS_NUMBER of the given participant
        :param message_referce: The MESSAGE_ID to update
        """
        try:
            self.db.connect()
            self.db.execute_non_query(
                "UPDATE v_notify_message_queue SET MESSAGE_ID = :message_referce WHERE NHS_NUMBER = :nhs_number",
                {"message_referce": message_referce, "nhs_number": nhs_number},
            )
        except oracledb.Error as e:
            logging.error({"error": str(e)})
        finally:
            self.db.disconnect()
