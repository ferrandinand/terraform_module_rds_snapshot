
#!/usr/bin/env python

from rds_backup import RDSBackup
import boto3
import logging

logging.basicConfig()
logging.getLogger('RDS').setLevel(logging.INFO)

def handler(event, context):
    try:
      rdscon = RDSBackup()
      session = boto3.Session()
      rdscon.connect(session)
      rdscon.backup_all_dbs()

      return
    except Exception as e:
      raise e

if __name__ == '__main__':
    handler(0, 0)
