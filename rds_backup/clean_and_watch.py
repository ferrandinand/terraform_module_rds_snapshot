
#!/usr/bin/env python

from rds_backup import RDSBackup
import os
import boto3
import logging

logging.basicConfig()
logging.getLogger('RDS').setLevel(logging.INFO)

def handler(event, context):

    try:
        expiration_range_days = int(os.environ['BACKUP_RETENTION_DAYS'])
    
    except Exception as e:
      logging.fatal('Error getting BACKUP_RETENTION_DAYS environment var')
      raise e


    try:
      rdscon = RDSBackup()
      session = boto3.Session()
      rdscon.connect(session)
      rdscon.delete_expired_backups(expiration_range_days)

      return
    except Exception as e:
      raise e

if __name__ == '__main__':
    handler(0, 0)
      
