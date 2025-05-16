import database
import logging
import oracledb


def fetch_batch_ids():
    batch_ids = []

    with database.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT DISTINCT batch_id FROM v_notify_message_queue WHERE message_status = :status",
                {"status": "sending"}
            )
            batch_ids = [row[0] for row in cursor.fetchall()]
        except oracledb.Error as e:
            logging.error("Error fetching batch IDs: %s", e)

    return batch_ids
