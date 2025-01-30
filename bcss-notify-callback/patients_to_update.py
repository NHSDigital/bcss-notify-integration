def patient_to_update(message_id, queue_dict, var) -> list[dict]:
    # Create dict to map MESSAGE ID to queue_patient data
    queue_dict_by_message_id = {str(queue_patient["MESSAGE_ID"]): queue_patient for queue_patient in queue_dict}
    data = False
    if message_id in queue_dict_by_message_id:
        print('Message ID found: ', message_id)
        queue_patient = queue_dict_by_message_id[message_id]

        # Store in data dict here and add to an array? in_val1,2,3 
        data = {"in_val1": queue_patient["BATCH_ID"], "in_val2": queue_patient["MESSAGE_ID"], "in_val3": "read", "out_val": var}
    return data