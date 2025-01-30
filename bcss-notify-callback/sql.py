def read_queue_table_to_dict(cursor):
    cursor.execute(f"select NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS from V_NOTIFY_MESSAGE_QUEUE")
    columns = [col[0] for col in cursor.description]
    queue_data = cursor.fetchall()

    #Dict for NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS for everything fetched from queue table
    queue_dict = [dict(zip(columns, row)) for row in queue_data]

    return queue_dict

def call_update_message_status(cursor, data, var):
    # Will need to loop through all the message_ids (in_val2) in a batch (in_val1) and update the status to the new status (in_val3)
    response_code = 1
    print("Run PKG_NOTIFY_WRAP.F_UPDATE_MESSAGE_STATUS")
    cursor.execute(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )
    response_code = var.getvalue()
    print('Response Code: ', response_code)
    #response_code_array.append(response_code)

    return response_code