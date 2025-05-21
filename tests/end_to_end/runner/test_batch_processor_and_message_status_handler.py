import logging
import requests
import time


def test_batch_processor_and_message_status_handler_lambdas(batch_id, helpers, recipient_data):
    helpers.seed_message_queue(batch_id, recipient_data)
    trigger_batch_notification_processor_lambda() # IRL this is a scheduled lambda function call at 0800hrs and 0900hrs.
    time.sleep(2)  # IRL this is a scheduled lambda function call around 2300hrs.
    trigger_message_status_handler_lambda()
    with helpers.cursor() as cursor:
        cursor.execute("SELECT nhs_number FROM v_notify_message_queue WHERE message_status = 'read'")
        results = cursor.fetchall()
        assert len(results) == len(recipient_data), "Not all messages were marked as read"
        for result in results:
            assert result[0] in [rd[0] for rd in recipient_data], "NHS number not found in recipient data"


def trigger_batch_notification_processor_lambda():
    response = requests.post("http://localhost:9000/2015-03-31/functions/function/invocations", json={})
    logging.info("Response: %s", response.json())


def trigger_message_status_handler_lambda():
    response = requests.post("http://localhost:9001/2015-03-31/functions/function/invocations", json={})
    logging.info("Response: %s", response.json())
