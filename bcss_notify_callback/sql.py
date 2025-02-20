def read_queue_table_to_dict(cursor):
    try:
        cursor.execute(
            "select NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS from V_NOTIFY_MESSAGE_QUEUE"
        )
        columns = [col[0] for col in cursor.description]
        queue_data = cursor.fetchall()

        if not queue_data:
            # log warning? error? raise exception, would cause errors later on
            raise (TypeError("No data found in queue table"))

        # Dict for NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS for everything fetched from queue table
        queue_dict = [dict(zip(columns, row)) for row in queue_data]

        return queue_dict
    except Exception as e:
        # logger instead
        print(f"Error reading queue table to dict {e}")
        raise


def call_update_message_status(cursor, data, var):
    # Will need to loop through all the message_ids (in_val2) in a batch (in_val1) and update the status to the new status (in_val3)
    response_code = 1
    cursor.execute(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )
    response_code = var.getvalue()

    return response_code
