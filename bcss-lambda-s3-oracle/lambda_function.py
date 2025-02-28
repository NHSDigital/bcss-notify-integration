import json
import boto3
import base64
import os
import oracledb

# sns_client = boto3.client("sns")

# Constants for environment variables
HOST = os.getenv("host")
PORT = os.getenv("port")
SID = os.getenv("sid")
TS_THRESHOLD = int(os.getenv("ts_threshold"))
TABLESPACE_NAME = os.getenv("tablespace")
# SNS_ARN = os.getenv('sns_arn')
SECRET_NAME = os.getenv("secret_name")
REGION_NAME = os.getenv("region_name")


def lambda_handler(event, context):
    try:
        print("Starting lambda execution")
        # Set up session and client
        session = boto3.Session()
        print("After session")
        #       client = session.client(service_name='secretsmanager', region_name=REGION_NAME)
        client = session.client(service_name="secretsmanager")
        print("After client")
        # Calling SecretsManager
        get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)
        print("After get secret", get_secret_value_response)
        # Extracting the key/value from the secret
        secret = json.loads(get_secret_value_response["SecretString"])
        db_user = secret["username"]
        db_password = secret["password"]

        # Connecting to RDS Oracle Database
        dsn_tns = f"{db_user}/{db_password}@{HOST}:{PORT}/{SID}"
        connection = oracledb.connect(dsn_tns)
        cursor = connection.cursor()
        for row in cursor.execute("select NHS_NUMBER from MPI"):
            print(row)

        print("Connected to database:", SID)
        print("Database Version:", connection.version)

        print("Fetching Utilization of tablespace:", TABLESPACE_NAME)
        cursor.execute(
            """
            SELECT ROUND(((t.totalspace - NVL(fs.freespace, 0)) / t.totalspace) * 100, 2) AS "%Used"
            FROM (
                SELECT ROUND(SUM(d.bytes) / (1024 * 1024)) AS totalspace, d.tablespace_name tablespace
                FROM dba_data_files d
                WHERE d.tablespace_name = :id
                GROUP BY d.tablespace_name
            ) t,
            (
                SELECT ROUND(SUM(f.bytes) / (1024 * 1024)) AS freespace, f.tablespace_name tablespace
                FROM dba_free_space f
                WHERE f.tablespace_name = :id
                GROUP BY f.tablespace_name
            ) fs
            WHERE t.tablespace = fs.tablespace (+)
        """,
            {"id": TABLESPACE_NAME},
        )

        result = cursor.fetchone()
        for row in result:
            print("Tablespace Utilization(%):", row)

        if row > TS_THRESHOLD:
            print(
                f"Tablespace:{TABLESPACE_NAME} utilization is above threshold ({TS_THRESHOLD}%), Publishing message to SNS"
            )
            response = sns_client.publish(
                TopicArn=SNS_ARN,
                Message=f"Tablespace:{TABLESPACE_NAME} utilization is above threshold. Please check immediately.",
            )
            return {"statusCode": 200, "body": json.dumps(response)}

        print(f"Tablespace:{TABLESPACE_NAME} utilization is below threshold")

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
    finally:
        # Close Cursor and Connection
        cursor.close()
        connection.close()
