from contextlib import contextmanager
import boto3
import json
import logging
import oracledb
import os


class DatabaseConnectionError(Exception):
    """Raised when there is an error connecting to the database"""


client = None


@contextmanager
def connection():
    try:
        conn = oracledb.connect(**connection_params())
        try:
            yield conn
        finally:
            conn.close()
    except oracledb.Error as e:
        logging.error("Error Connecting to Database: %s", e)
        raise DatabaseConnectionError(f"Error Connecting to Database: {str(e)}")


@contextmanager
def cursor():
    cursor = None
    try:
        with connection() as conn:
            cursor = conn.cursor()

            yield cursor

    finally:
        cursor.close()


def connection_params() -> dict:
    secret = get_secret()
    db_user: str = secret["username"]
    db_password: str = secret["password"]
    host: str = os.getenv("bcss_host", "")
    port: str = os.getenv("port", "1521")
    sid: str = os.getenv("sid", "")
    dsn_tns = f"{host}:{port}/{sid}"

    return {"user": db_user, "password": db_password, "dsn": dsn_tns}


def get_secret() -> dict:
    secret_name = os.getenv("bcss_secret_name")
    secret_str = get_client().get_secret_value(
        SecretId=secret_name)["SecretString"]
    return json.loads(secret_str)


def get_client():
    global client
    if not client:
        client = boto3.client(
            service_name="secretsmanager",
            region_name=os.getenv("region_name")
        )

    return client
