import boto3
import json
import oracledb
import os

PORT = os.getenv("port")
SID = os.getenv("sid")
BCSS_SECRET_NAME = os.getenv("bcss_secret_name")
BCSS_HOST = os.getenv("bcss_host")
REGION_NAME = os.getenv("region_name")


def oracle_connection(client):
    try:
        get_secret_value_response = client.get_secret_value(SecretId=BCSS_SECRET_NAME)

        secret = json.loads(get_secret_value_response["SecretString"])
        db_user = secret["username"]
        db_password = secret["password"]

        dsn_tns = oracledb.makedsn(BCSS_HOST, PORT, SID)
        connection = oracledb.connect(user=db_user, password=db_password, dsn=dsn_tns)

        return connection
    except Exception as e:
        return {"statusCode": 500, "body": f"Error Connecting to Database: {str(e)}"}


def get_connection():
    client = boto3.client(service_name="secretsmanager", region_name=REGION_NAME)
    connection = oracle_connection(client)
    return connection


def get_cursor(connection):
    return connection.cursor()


def commit_changes(connection):
    connection.commit()


def close_connection(connection):
    connection.close()


def close_cursor(cursor):
    cursor.close()
