import logging


# TODO: This module should import the oracle module and be responsible for the connection and cursor
def read_queue_table_to_dict(cursor):
    cursor.execute(f"select NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS from V_NOTIFY_MESSAGE_QUEUE")
    columns = [col[0] for col in cursor.description]
    queue_data = cursor.fetchall()

    #Dict for NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS for everything fetched from queue table
    queue_dict = [dict(zip(columns, row)) for row in queue_data]

    return queue_dict


def call_update_message_status(cursor, recipient):
    var = cursor.var(int)
    data = {
        "in_val1": recipient["BATCH_ID"],
        "in_val2": recipient["MESSAGE_ID"],
        "in_val3": "read",
        "out_val": var,
    }

    # Will need to loop through all the message_ids (in_val2) in a batch (in_val1) and update the status to the new status (in_val3)
    response_code = 1
    logging.info("Run PKG_NOTIFY_WRAP.F_UPDATE_MESSAGE_STATUS")
    cursor.execute(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )
    response_code = var.getvalue()
    logging.info('Response Code: ', response_code)

    return response_code
