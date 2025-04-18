import dotenv
import scheduled_lambda_function as lambda_function
import os
import requests_mock

dotenv.load_dotenv(".env.test")


def test_message_status_handler_updates_message_status(batch_id, recipient_data, helpers):
    message_references = [r[1] for r in recipient_data]
    helpers.seed_message_queue(batch_id, recipient_data)
    helpers.call_get_next_batch(batch_id)

    with requests_mock.Mocker() as rm:
        rm.get(
            f"{os.getenv('COMMGT_BASE_URL')}/api/statuses",
            status_code=201,
            json={
                'status': 'success',
                'data': [
                    {
                        'channel': 'nhsapp',
                        'channelStatus': 'delivered',
                        'supplierStatus': 'read',
                        'message_id': '2WL3qFTEFM0qMY8xjRbt1LIKCzM',
                        'message_reference': message_references[0]
                    },
                    {
                        'channel': 'nhsapp',
                        'channelStatus': 'delivered',
                        'supplierStatus': 'read',
                        'message_id': '5EL3qFTEFM0qMY8xjRbt1LIKCzM',
                        'message_reference': message_references[1]
                    },
                ]
            }
        )

        lambda_function.lambda_handler({"batch_id": batch_id}, {})

    with helpers.cursor() as cur:
        cur.execute(
            "SELECT message_id FROM v_notify_message_queue WHERE batch_id = :batch_id AND message_status = 'read'",
            batch_id=batch_id
        )
        results = cur.fetchall()

    assert len(results) == 2
    assert results[0][0] == message_references[0]
    assert results[1][0] == message_references[1]
