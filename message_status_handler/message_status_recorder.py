import database

def record_message_statuses(batch_id: str, json_data: dict):
    response_codes = []
    message_references = [item['message_reference'] for item in json_data['data']]

    with database.cursor() as cursor:
        for message_reference in message_references:
            response_codes.append(update_message_status(cursor, batch_id, message_reference))

        cursor.connection.commit()

    return response_codes


def update_message_status(cursor, batch_id: str, message_reference: str):
    response_code = 1
    var = cursor.var(int)

    cursor.execute(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        {
            "in_val1": batch_id,
            "in_val2": message_reference,
            "in_val3": "read",
            "out_val": var,
        },
    )

    response_code = var.getvalue()

    return response_code
