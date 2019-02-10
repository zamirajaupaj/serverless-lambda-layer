"""
{ 
 "DbName": "DbName",
 "DbUser": "DbUser",
 "S3BucketName": "S3BucketName",
 "KmsKeyId": "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx",
 "RdsEndpoint": "RdsEndpoint",
 "RdsPort": "1433",
 "ParameterStore": "DbPassword",
 "Region": "eu-west-1",
 "AccountId": "123456789"
 }
 """

import boto3
import pymssql
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def status_row_to_dic(row):
  for i in row:
    output = {
            'taskId': i['task_id'],
            'taskType': i['task_type'],
            'lifecycle': i['lifecycle'],
            'createdAt': i['created_at'].isoformat(),
            'lastUpdated': i['last_updated'].isoformat(),
            'databaseName': i['database_name'],
            's3ObjectArn': i['S3_object_arn'],
            'overwriteS3BackupFile': i['overwrite_S3_backup_file'],
            'kmsMasterKeyArn': i['KMS_master_key_arn'],
            'taskProgress': i['task_progress'],
            'taskInfo': i['task_info']
    }
    # outputs = { key: value for (key, value) in i.output()}
    if i['task_progress'] == 0:
        print('Backup Complete')
        return output
    else:
        print('Backup in Progress')
        return output

def backup_db(cursor, dbName, S3BucketName, KmsKeyId, Region, AccountId, FileName):
    try:
        sql = (
            "exec msdb.dbo.rds_backup_database " \
            f"@source_db_name='{dbName}', "  \
            f"@s3_arn_to_backup_to='arn:aws:s3:::{S3BucketName}/{FileName}', " \
            f"@kms_master_key_arn='arn:aws:kms:{Region}:{AccountId}:key/{KmsKeyId}', " \
            "@overwrite_S3_backup_file=1, " \
            "@type='FULL';" 
        )
        cursor.execute(sql)
        row = cursor.fetchall()
        return status_row_to_dic(row)
    except:
        logger.error("ERROR: Unexpected error: Could not backup the database.")
        sys.exit()
    logger.info("SUCCESS: Backup of database successfully")

def status_db(cursor):
    try:
        sql = (
            f"exec msdb.dbo.rds_task_status; "
        )
        cursor.execute(sql)
        row = cursor.fetchall()
        if not row:
            return 'No task executed before', 0
        else:
            for i in row:
                if i['lifecycle'] == 'SUCCESS' and i['% complete'] == 100:
                    output = {
                        'taskId': i['task_id'],
                        'taskType': i['task_type'],
                        'databaseName': i['database_name'],
                        '%Complete': i['% complete'],
                        'Duration': i['duration(mins)'],
                        'lifecycle': i['lifecycle'],
                        'taskInfo': i['task_info'],
                        'createdAt': i['created_at'].isoformat(),
                        'lastUpdated': i['last_updated'].isoformat(),
                        's3ObjectArn': i['S3_object_arn'],
                        'overwriteS3BackupFile': i['overwrite_S3_backup_file'],
                        'kmsMasterKeyArn': i['KMS_master_key_arn']
                    }
                    return output, i['lifecycle'] 
                elif i['lifecycle'] == 'CREATED':
                    return i['lifecycle'], 'As soon as you call rds_backup_database or rds_restore_database, a task is created and the status is set to:  CREATED'
                elif i['lifecycle'] == 'IN_PROGRESS':
                    return i['lifecycle'], 'It can take up to 5 minutes for the status to change from IN_PROGRESS to SUCCESS'
                elif i['lifecycle'] == 'CANCEL_REQUESTED':
                    return i['lifecycle'], 'As soon as you call rds_cancel_task, the status of the task is set to CANCEL_REQUESTED. '
                elif i['lifecycle'] == 'CANCELLED':
                    return i['lifecycle'], 'After a task is successfully canceled, the status of the task is set to CANCELLED. '
                else:
                    i['lifecycle'] == 'ERROR'
                return 'ERROR: ', i['lifecycle']
    except:
        logger.error("ERROR: Unexpected error:.")
        sys.exit()
    logger.info("SUCCESS: status is Complete successfully")

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
            return "ERROR: Connection unsuccessful"
        else:
            print("SUCCESS: Connection to RDS SQL instance succeeded")
            cursor = conn.cursor()
            status = status_db(cursor)
            
            if status[1] == 'SUCCESS' or status[1] == 'ERROR' or status[1] == 'CANCELLED'or status[1] == 'CANCEL_REQUESTED' or status[1] == 0:
                backup_db(cursor,  event['DbName'], event['S3BucketName'], event['KmsKeyId'],event['Region'], event['AccountId'], event['FileName'])
            else:
                return "ERROR: Unexpected error: status is not complete", status[1] 
    except:
        logger.error("ERROR: Unexpected error: Could not connect to SQL instance.")
        sys.exit()
    logger.info("SUCCESS: Connection to RDS SQL instance succeeded")

