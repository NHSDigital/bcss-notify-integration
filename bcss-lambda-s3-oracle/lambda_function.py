"""Lambda function to monitor Oracle tablespace utilisation and send SNS alerts."""
import json
import os
import boto3
import oracledb

# Constants for environment variables
HOST = os.getenv("host")
PORT = os.getenv("port")
SID = os.getenv("sid")
TABLESPACE_NAME = os.getenv("tablespace")
SECRET_NAME = os.getenv("secret_name")
REGION_NAME = os.getenv("region_name")
TS_THRESHOLD = int(os.getenv("ts_threshold", "85"))  # Default threshold of 85%


def lambda_handler(event, context):
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
        print("Starting lambda execution")
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

        print(f"Connected to database: {SID}")
        print(f"Database Version: {connection.version}")
        print(f"Fetching Utilization of tablespace: {TABLESPACE_NAME}")

        # Query tablespace utilisation
        cursor.execute(
            """
            SELECT ROUND(((t.totalspace - NVL(fs.freespace, 0)) / t.totalspace) * 100, 2) AS used_pct
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
        print(f"Tablespace Utilization(%): {utilisation}")

        if utilisation > TS_THRESHOLD:
            print(
                f"Tablespace:{TABLESPACE_NAME} utilisation is above threshold "
                f"({TS_THRESHOLD}%), alert required"
            )
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Threshold exceeded",
                    "utilisation": utilisation
                })
            }

        print(f"Tablespace:{TABLESPACE_NAME} utilisation is below threshold")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Utilisation normal",
                "utilisation": utilisation
            })
        }

    except Exception as err:
        print(f"Error: {str(err)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(err)})}
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
