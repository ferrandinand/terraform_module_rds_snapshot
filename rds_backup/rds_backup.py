#!/usr/bin/env python


import boto3
import datetime
import os
import logging

class RDSBackup(object):

    def __init__(self):
        self.logger = logging.getLogger('RDS')
        self.logger.addHandler(logging.NullHandler())

    def connect(self, session):
        self.client = session.client('rds')

    def get_backups_instance(self, instance):
        backups = self.client.describe_db_snapshots(DBInstanceIdentifier=instance)['DBSnapshots']

        return backups

    def get_all_instances(self):
        instances = self.client.describe_db_instances()

        return instances['DBInstances']

    def get_number_backups_instance(self, instance):
        backups = self.get_backups_instance(instance)

        return (backups.__len__())

    def get_expired_backups_instance(self, instance, expiration_range_days):

        from_date = datetime.datetime.now() - datetime.timedelta(days=expiration_range_days)

        backups = self.get_backups_instance(instance)
        expired_backups = []
        
        for backup in backups:
            if backup['Status'] == "available" and backup['SnapshotType'] != "automated":
                if backup['SnapshotCreateTime'].date() < from_date.date():
                    self.logger.info("Found an old backup: "+ backup['DBSnapshotIdentifier'])
                    expired_backups.append({'DBSnapshotIdentifier':backup['DBSnapshotIdentifier']}) 

 
        return expired_backups

    def get_all_expired_backups(self, expiration_range_days):

        expired_backups = []
        expired_backups_instance = []
        instances = self.get_all_instances()

        for instance in instances:
            self.logger.debug("Looking for backups instance: "+ instance['DBInstanceIdentifier'])
            expired_backups_instance = self.get_expired_backups_instance(instance['DBInstanceIdentifier'],expiration_range_days)
            if expired_backups_instance:
                expired_backups.append(expired_backups_instance)

            self.logger.debug(instance['DBInstanceIdentifier'] + \
                " instance found "+ str(self.get_number_backups_instance(instance['DBInstanceIdentifier'])) + \
                " backups")
                
        return expired_backups
    
    def create_rds_backup(self, instance):
        self.client.create_db_snapshot(DBInstanceIdentifier=instance, \
            DBSnapshotIdentifier=instance + "-" +\
            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        self.logger.info("Created snapshot for instance: "+ instance)

        return True

    def backup_all_dbs(self):
        instances = self.get_all_instances()

        for instance in instances:
            self.create_rds_backup(instance['DBInstanceIdentifier'])
            self.logger.info("Doing backup for: "+ instance['DBInstanceIdentifier'])


    def delete_expired_backups(self, retention_period):
        expired_backups = self.get_all_expired_backups(retention_period)

        for expired_backup in expired_backups:
            for remove_backup in expired_backup:
                self.client.delete_db_snapshot(DBSnapshotIdentifier=remove_backup['DBSnapshotIdentifier'])
                self.logger.info("Removing snapshot for: "+ remove_backup['DBSnapshotIdentifier'])

            


