import json
import oracledb
import os

PORT = os.getenv("port")
SID = os.getenv("sid")
SECRET_NAME = os.getenv("secret_name")
BCSS_SECRET_NAME = os.getenv("bcss_secret_name")

def oracle_connection(client):
    get_secret_value_response = client.get_secret_value(SecretId=BCSS_SECRET_NAME)
        
    # Extract database credentials from the secret
    secret = json.loads(get_secret_value_response["SecretString"])
    db_user = secret["username"]
    db_password = secret["password"]

    # Create the DSN (Data Source Name) for the Oracle connection
    dsn_tns = oracledb.makedsn(BCSS_HOST, PORT, SID)
    connection = oracledb.connect(user=db_user, password=db_password, dsn=dsn_tns)

    return connection