import logging
import requests


def test_batch_processor_schedules_message_status_handler(batch_id, helpers, recipient_data):
    helpers.seed_message_queue(batch_id, recipient_data)
    trigger_batch_notifications(batch_id)
    with helpers.cursor() as cursor:
        cursor.execute(
            "SELECT nhs_number FROM v_notify_message_queue WHERE batch_id = :batch_id AND message_status = 'read'",
            {"batch_id": batch_id},
        )
        results = cursor.fetchall()
        assert len(results) == len(recipient_data), "Not all messages were marked as read"
        for result in results:
            assert result[0] in [rd[0] for rd in recipient_data], "NHS number not found in recipient data"


def trigger_batch_notifications(batch_id):
    response = requests.post("http://localhost:9000/2015-03-31/functions/function/invocations", json={"batch_id": batch_id})
    logging.info("Response: %s", response.json())
