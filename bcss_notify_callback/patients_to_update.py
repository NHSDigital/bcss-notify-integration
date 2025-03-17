from oracle.oracle import get_cursor, close_cursor


def patient_to_update(connection, message_id, queue_dict) -> dict:
    cursor = get_cursor(connection)
    var = cursor.var(int)
    queue_dict_by_message_id = {
        str(queue_patient["MESSAGE_ID"]): queue_patient for queue_patient in queue_dict
    }
    data = False
    if message_id in queue_dict_by_message_id:
        queue_patient = queue_dict_by_message_id[message_id]

        data = {
            "in_val1": queue_patient["BATCH_ID"],
            "in_val2": queue_patient["MESSAGE_ID"],
            "in_val3": "read",
            "out_val": var,
        }
    close_cursor(cursor)
    return data
