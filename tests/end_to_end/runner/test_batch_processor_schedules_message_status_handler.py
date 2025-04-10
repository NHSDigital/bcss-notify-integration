import logging
import requests


def test_batch_processor_schedules_message_status_handler(batch_id, helpers, recipient_data):
    helpers.seed_message_queue(batch_id, recipient_data)
    trigger_batch_notifications(batch_id)


def trigger_batch_notifications(batch_id):
    import time; time.sleep(25)
    response = requests.post("http://localhost:9000/2015-03-31/functions/function/invocations", {"batch_id": batch_id})
    logging.info("Response: %s", response.json())
