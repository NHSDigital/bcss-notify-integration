from flask import Flask, request
import dotenv
import logging
from scheduled_lambda_function import lambda_handler

app = Flask(__name__)

dotenv.load_dotenv()


@app.route('/schedule', methods=['POST'])
def schedule():
    batch_id = request.json["batch_id"]

    logging.info("Scheduling status check for batch ID: %s", batch_id)

    lambda_response = lambda_handler({"batch_id": batch_id}, {})

    logging.info("Lambda response: %s", lambda_response)
    return lambda_response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8889)
