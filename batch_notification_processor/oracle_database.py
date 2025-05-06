import logging
import oracledb
import database

from recipient import Recipient

def get_routing_plan_id(batch_id: str):
    with database.cursor() as cursor:
        try:
            result = cursor.callfunc("PKG_NOTIFY_WRAP.f_get_next_batch", oracledb.STRING, [batch_id])
            database.connection().commit()
            return result
        except oracledb.Error as e:
            logging.error("Error calling PKG_NOTIFY_WRAP.f_get_next_batch: %s", e)
            raise

def get_recipients(batch_id: str) -> list[Recipient]:
    recipient_data = []

    with database.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT * FROM v_notify_message_queue WHERE batch_id = :batch_id",
                {"batch_id": batch_id},
            )
            recipient_data = cursor.fetchall()
        except oracledb.Error as e:
            logging.error("Error executing query: %s", e)

    return [Recipient(rd) for rd in recipient_data]

def update_recipient(recipient: Recipient, attr: str):
    attr = attr.lower()
    if attr not in ["message_id", "message_status"]:
        raise ValueError(f"Invalid attribute for Recipient update: {attr}")

    with database.cursor() as cursor:
        try:
            cursor.execute(
                (
                    "UPDATE v_notify_message_queue "
                    f"SET {attr} = :{attr} "
                    "WHERE nhs_number = :nhs_number"
                ),
                {
                    attr: getattr(recipient, attr),
                    "nhs_number": recipient.nhs_number
                },
            )
            database.connection().commit()
        except oracledb.Error as e:
            logging.error("Error updating recipient: %s", e)
            database.connection().rollback()
            raise

def update_message_id(recipient: Recipient):
    update_recipient(recipient, "message_id")

def update_message_status(recipient: Recipient):
    update_recipient(recipient, "message_status")