import logging
import json
import os
import uuid
import boto3

from oracle_database import OracleDatabase
from bcss_notify_batch_processor import BCSSNotifyBatchProcessor
from bcss_notify_request_handler import BCSSNotifyRequestHandler


# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # You can change this to DEBUG, ERROR, etc.

# Set up log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a stream handler to output logs to CloudWatch
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

HOST = os.getenv("host")
PORT = os.getenv("port")
SID = os.getenv("sid")
TABLESPACE_NAME = os.getenv("tablespace")
SNS_ARN = os.getenv("sns_arn")
SECRET_NAME = os.getenv("secret_arn")
REGION_NAME = os.getenv("region_name")
NHS_NOTIFY_BASE_URL = os.getenv("nhs_notify_base_url")
ROUTING_CONFIG_ID = os.getenv("routing_config_id")
TOKEN_URL = os.getenv("token_url")

# Initialize AWS clients
secrets_client = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)


def get_secret(secret_name):
    """Retrieve a secret value from AWS Secrets Manager."""
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])
    return secret

def lambda_handler(event, context):
    logger.info("Lambda function has started.")

    db_secret = get_secret(SECRET_NAME)
    notify_secrets = get_secret("bcss-notify-nonprod-pem-key")

    db_user = db_secret["username"]
    db_password = db_secret["password"]

    private_key = notify_secrets["private-key"]

    db_config = {
        "user": db_user,
        "password": db_password,
        "dsn": f"{HOST}:{PORT}/{SID}",
    }

    database = OracleDatabase(**db_config)

    bcss_notify_batch_processor = BCSSNotifyBatchProcessor(database)
    bcss_notify_request_handler = BCSSNotifyRequestHandler(
        TOKEN_URL, private_key, NHS_NOTIFY_BASE_URL, database
    )

    batch_id = str(uuid.uuid4())
    batch_id = None
    logger.debug("DEBUG: BATCH_ID - %s", {batch_id})

    logger.info("Getting routing ID...")
    ROUTING_CONFIG_ID = bcss_notify_batch_processor.get_routing_plan_id()

    logger.info("Getting participants...")
    participants = bcss_notify_batch_processor.get_participants(batch_id)
    logger.info("Got participants.")

    logger.debug("DEBUG: PARTICIPANTS - \n %s", participants)