import json
import os
import logging
import boto3
import oracledb

PORT = os.getenv("port")
SID = os.getenv("sid")
BCSS_SECRET_NAME = os.getenv("bcss_secret_name")
BCSS_HOST = os.getenv("bcss_host")
REGION_NAME = os.getenv("region_name")


def create_oracle_connection(client):
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
    session = boto3.Session()
    client = session.client(service_name="secretsmanager", region_name=REGION_NAME)
    connection = create_oracle_connection(client)
    return connection


def get_cursor(connection):
    return connection.cursor()


def get_queue_table_records(connection, logger):
    cursor = get_cursor(connection)
    try:
        cursor.execute(
            cursor,
            "select NHS_NUMBER, MESSAGE_ID, BATCH_ID, MESSAGE_STATUS from V_NOTIFY_MESSAGE_QUEUE",
        )

        columns = [col[0] for col in cursor.description]
        queue_data = cursor.fetchall()

        if not queue_data:
            raise TypeError("No data found in queue table")

        queue_dict = [dict(zip(columns, row)) for row in queue_data]
        close_cursor(cursor)
        return queue_dict
    except Exception as e:
        logger.error(f"Error reading queue table to dict: {e}")
        raise


def call_update_message_status(connection, data):
    cursor = get_cursor(connection)
    response_code = 1
    var = cursor.var(int)
    cursor.execute(
        """
            begin
                :out_val := pkg_notify_wrap.f_update_message_status(:in_val1, :in_val2, :in_val3);
            end;
        """,
        data,
    )
    response_code = var.getvalue()
    close_cursor(cursor)

    return response_code


def query_tablespace_utilisation(cursor, tablespace_name, ts_threshold):
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
        {"id": tablespace_name},
    )

    result = cursor.fetchone()
    utilisation = result[0] if result else 0
    logging.info("Tablespace Utilization(%%): %s", utilisation)

    if utilisation > ts_threshold:
        logging.warning(
            "Tablespace:%s utilisation is above threshold\n(%s%%), alert required",
            tablespace_name,
            ts_threshold,
        )
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Threshold exceeded", "utilisation": utilisation}
            ),
        }
    logging.info("Tablespace:%s utilisation is below threshold", tablespace_name)
    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "Utilisation normal", "utilisation": utilisation}
        ),
    }


def commit_changes(connection):
    connection.commit()


def close_connection(connection):
    connection.close()


def close_cursor(cursor):
    cursor.close()
