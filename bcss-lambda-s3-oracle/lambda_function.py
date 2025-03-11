"""Lambda function to monitor Oracle tablespace utilisation and send alerts."""

import json
import logging
import os
import boto3
import oracledb

# Constants for environment variables
HOST = os.getenv("host")  # Database host
PORT = os.getenv("port")  # Database port
SID = os.getenv("sid")  # Database SID
TABLESPACE_NAME = os.getenv("tablespace")  # Target tablespace
SECRET_NAME = os.getenv("secret_name")  # AWS secret name
REGION_NAME = os.getenv("region_name")  # AWS region
TS_THRESHOLD = int(os.getenv("ts_threshold", "85"))  # Tablespace threshold percentage

# Initialize AWS client
SECRETS_CLIENT = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)

logging.basicConfig(
    format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)


def lambda_handler(_event: dict, _context: object) -> dict:
    """
    AWS Lambda handler to check Oracle tablespace utilisation.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context

    Returns:
        dict: Response containing status code and execution results
    """
    cursor = None
    connection = None

    try:
        logging.info("Starting lambda execution")
        session = boto3.Session()
        client = session.client(service_name="secretsmanager")

        # Fetch database credentials from Secrets Manager
        secret_response = client.get_secret_value(SecretId=SECRET_NAME)
        secret = json.loads(secret_response["SecretString"])
        db_user = secret["username"]
        db_password = secret["password"]

        # Connect to Oracle database
        dsn_tns = f"{db_user}/{db_password}@{HOST}:{PORT}/{SID}"
        connection = oracledb.connect(dsn_tns)
        cursor = connection.cursor()
        logging.info("Connected to database: %s", SID)
        logging.info("Database Version: %s", connection.version)
        logging.info("Fetching Utilization of tablespace: %s", TABLESPACE_NAME)

        # Query tablespace utilisation
        cursor.execute(
            """
            SELECT ROUND(((t.totalspace - NVL(fs.freespace, 0)) / t.totalspace) * 100, 2) 
            AS used_pct
            FROM (
                SELECT ROUND(SUM(d.bytes) / (1024 * 1024)) AS totalspace, 
                       d.tablespace_name tablespace
                FROM dba_data_files d
                WHERE d.tablespace_name = :id
                GROUP BY d.tablespace_name
            ) t,
            (
                SELECT ROUND(SUM(f.bytes) / (1024 * 1024)) AS freespace, 
                       f.tablespace_name tablespace
                FROM dba_free_space f
                WHERE f.tablespace_name = :id
                GROUP BY f.tablespace_name
            ) fs
            WHERE t.tablespace = fs.tablespace (+)
            """,
            {"id": TABLESPACE_NAME},
        )

        result = cursor.fetchone()
        utilisation = result[0] if result else 0
        logging.info("Tablespace Utilization(%%): %s", utilisation)

        if utilisation > TS_THRESHOLD:
            logging.warning(
                "Tablespace:%s utilisation is above threshold\n(%s%%), alert required",
                TABLESPACE_NAME,
                TS_THRESHOLD,
            )
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"message": "Threshold exceeded", "utilisation": utilisation}
                ),
            }
        logging.info("Tablespace:%s utilisation is below threshold", TABLESPACE_NAME)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Utilisation normal", "utilisation": utilisation}
            ),
        }

    except Exception as err:
        logging.error("Error: %s", str(err))
        return {"statusCode": 500, "body": json.dumps({"error": str(err)})}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
