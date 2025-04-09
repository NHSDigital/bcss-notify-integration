from contextlib import contextmanager
import boto3
import json
import logging
import oracledb
import os


class DatabaseConnectionError(Exception):
    """Raised when there is an error connecting to the database"""


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
        raise DatabaseConnectionError(f"Error Connecting to Database: {str(e)}") from e


@contextmanager
def cursor():
    cur = None
    try:
        with connection() as conn:
            cur = conn.cursor()
            try:
                yield cur
            finally:
                cur.close()
    except oracledb.Error as e:
        logging.error("Error Creating Cursor: %s", e)
        raise DatabaseConnectionError(f"Error Creating Cursor: {str(e)}") from e


def connection_params() -> dict:
    client = boto3.client(
        service_name="secretsmanager",
        region_name=os.getenv("REGION_NAME"),
    )
    secret = json.loads(
        client.get_secret_value(SecretId=os.getenv("SECRET_ARN"))["SecretString"]
    )
    db_user: str = secret["username"]
    db_password: str = secret["password"]
    host: str = os.environ["DATABASE_HOST"]
    port: str = os.getenv("DATABASE_PORT", "1521")
    sid: str = os.environ["DATABASE_SID"]
    dsn_tns = f"{host}:{port}/{sid}"

    return {"user": db_user, "password": db_password, "dsn": dsn_tns}
