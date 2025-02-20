import json
import oracledb
import os

PORT = os.getenv("port")
SID = os.getenv("sid")
BCSS_SECRET_NAME = os.getenv("bcss_secret_name")
BCSS_HOST = os.getenv("bcss_host")


def oracle_connection(client):
    try:
        get_secret_value_response = client.get_secret_value(SecretId=BCSS_SECRET_NAME)

        # Extract database credentials from the secret
        secret = json.loads(get_secret_value_response["SecretString"])
        db_user = secret["username"]
        db_password = secret["password"]

        # Create the DSN (Data Source Name) for the Oracle connection
        dsn_tns = oracledb.makedsn(BCSS_HOST, PORT, SID)
        connection = oracledb.connect(user=db_user, password=db_password, dsn=dsn_tns)

        return connection
    except Exception as e:
        # Change to logger
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
