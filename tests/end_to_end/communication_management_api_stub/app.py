from flask import Flask, request
import dotenv
import json
from jsonschema import validate, ValidationError
import time
import uuid

app = Flask(__name__)

dotenv.load_dotenv()

request_cache = {}


@app.route('/api/message/batch', methods=['POST'])
def message_batches():
    json_data = default_response_data() | request.json
    batch_reference = json_data["data"]["attributes"]["messageBatchReference"]
    request_cache[batch_reference] = json_data
    messages = messages_with_ids(json_data["data"]["attributes"]["messages"])

    if not validate_with_schema(json_data):
        return json.dumps({"error": "Invalid body"}), 422

    return json.dumps({
        "data": {
            "type": "MessageBatch",
            "id": json_data["data"].get("id"),
            "attributes": {
                "messageBatchReference": batch_reference,
                "routingPlan": {
                    "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                    "name": "Plan Abc",
                    "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                    "createdDate": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                },
                "messages": messages
            }
        }
    }), 201


@app.route('/api/statuses', methods=['GET'])
def statuses():
    batch_reference = request.args.get("batchReference")
    status = request.args.get("supplierStatus")

    if not batch_reference:
        return json.dumps({"error": "Missing batchReference"}), 422

    if batch_reference not in request_cache:
        return json.dumps({"error": "Message batch not found"}), 404

    messages = request_cache[batch_reference]["data"]["attributes"]["messages"]
    message_status_data = []

    for message in messages:
        message_status_data.append({
            "message_reference": message["messageReference"],
            "channel": "nhsapp",
            "channelStatus": "delivered",
            "supplierStatus": status,
        })

    return {
        "status": "success",
        "data": message_status_data
    }, 201


def default_response_data():
    return {
        "data": {
            "id": "2ZljUiS8NjJNs95PqiYOO7gAfJb",
            "attributes": {
                "messageBatchReference": "d3f31ae4-1532-46df-b121-3503db6b32d6",
                "messages": [
                    {
                        "messageReference": "703b8008-545d-4a04-bb90-1f2946ce1575",
                        "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                    }
                ]
            }
        }
    }


def messages_with_ids(messages: list[dict]) -> list[dict]:
    for message in messages:
        message["id"] = uid(27) if not message.get("id") else message["id"]

    return messages


def uid(n) -> str:
    return uuid.uuid4().hex[0:n]


def validate_with_schema(data: dict):
    try:
        schema = json.load(open("schema.json"))
        subschema = schema["paths"]["/v1/message-batches"]["post"]["requestBody"]["content"]["application/vnd.api+json"]["schema"]
        validate(instance=data, schema=subschema)
        return True, ""
    except ValidationError as e:
        return False, e.message
    except KeyError as e:
        return False, f"Invalid body: {e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
