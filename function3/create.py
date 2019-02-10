
"""
{ 
 "DbName": "DbName",
 "DbUser": "DbUser",
 "RdsEndpoint": "RdsEndpoint",
 "RdsPort": "1433",
 "ParameterStore": "DbPassword"
 }
 """

import boto3
import pymssql
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def create_table(cursor):
    cursor.execute("""
    IF OBJECT_ID('persons', 'U') IS NOT NULL
        DROP TABLE persons
    CREATE TABLE persons (
        id INT NOT NULL,
        name VARCHAR(100),
        salesrep VARCHAR(100),
        PRIMARY KEY(id)
    )
    """)
    cursor.executemany(
        "INSERT INTO persons VALUES (%d, %s, %s)",
        [(1, 'John Smith', 'John Doe'),
        (2, 'Jane Doe', 'Joe Dog'),
        (3, 'Mike T.', 'Sarah H.')])

    # you must call commit() to persist your data if you don't set autocommit to True
    cursor.execute('SELECT * FROM persons;')
    row = cursor.fetchall()
    for i in row:
        print(i)
    return i


def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    responseSSM = ssm.get_parameters(
        Names=[
            event['ParameterStore'],
        ],
        WithDecryption=True
    )
    password = responseSSM["Parameters"][0]["Value"]
    try:
        conn = pymssql.connect(
            server = event['RdsEndpoint'],
            user = event['DbUser'],
            password = password,
            port='1433',
            as_dict = True,
            autocommit = True)

        # Check if connection was successful
        if (conn) is None:
            return "ERROR:Connection unsuccessful"
        else:
            print("SUCCESS: Connection to RDS SQL instance succeeded")
            conn.autocommit(True)
            cursor = conn.cursor()
            cursor.execute("""
            IF  NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = N'zamira')
                BEGIN
                    CREATE DATABASE [zamira]
                END;
            """)
            conn.autocommit(False)
            conn.close()
        # use the database that you created before
        conn = pymssql.connect(
            server = event['RdsEndpoint'],
            user = event['DbUser'],
            password = password,
            port='1433',
            database='zamira',
            as_dict = True,
            autocommit = True)
        if (conn) is None:
            return "ERROR:Connection unsuccessful"
        else:
            cursor = conn.cursor()
            create_table(cursor)
    except:
        logger.error("ERROR: Unexpected error: Could not backup the database.")
        sys.exit()
    logger.info("SUCCESS: Backup of database successfully")

