import oracle_connection as db


def read_queue_table_to_dict(connection, logger):
    cursor = db.get_cursor(connection)
    try:
        cursor.execute(
            "select NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS from V_NOTIFY_MESSAGE_QUEUE"
        )
        columns = [col[0] for col in cursor.description]
        queue_data = cursor.fetchall()

        if not queue_data:
            raise (TypeError("No data found in queue table"))

        queue_dict = [dict(zip(columns, row)) for row in queue_data]
        db.close_cursor(cursor)
        return queue_dict
    except Exception as e:
        logger.error(f"Error reading queue table to dict: {e}")
        raise


def call_update_message_status(cursor, data):
    response_code = 1
    var = cursor.var(int)
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
