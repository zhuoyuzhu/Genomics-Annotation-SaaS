from bottle import route, run, request, response, error, post, get, template
from datetime import datetime, timedelta
from boto3 import client
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr
import requests
import uuid
import time
import boto3
import os.path
import json
import subprocess
import botocore.session
import boto3
import sched
import sys
import botocore
import hmac
import hashlib
import base64
import pytz
import urllib2
import urlparse


# Get the access key and secret key for the current session
session = botocore.session.get_session()
ACCESS_KEY = session.get_credentials().access_key
SECRET_KEY = session.get_credentials().secret_key
session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# DynamoDB reference
dynamodb = boto3.resource('dynamodb')
ann_table = dynamodb.Table('zhuoyuzhu_annotations')


# Archive result file from S3 bucket to Amazon Glacier
def archive_data(job_id, user_role, result_file):

        # Pass in user role, job_id, completion_time, username
        glacier_client = boto3.client('glacier')
        s3 = session.resource('s3')
        client = boto3.client('s3')
        bucket = s3.Bucket('gas-results')

        # Get the corresponding job id
        res = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
        items = res['Items']

        # When the 30 mins reach, we check again if the user is premium in case he upgrade to premium within 30 time frame
        # We only archive result file if the user is a free_user role
        if items[0]['user_role'] == 'free_user':
                for obj in bucket.objects.filter(Prefix=result_file):
                		# Archive result file to Glacier
                        archive_res = glacier_client.upload_archive(vaultName='ucmpcs',body=obj.get()['Body'].read())

                        print 'Archive id: ' + archive_res['archiveId']
                        archive_id = archive_res['archiveId']

                        # Update the job details within DynamoDB
                        updateData = ann_table.update_item(
                                Key={
                                        'job_id': job_id
                                },
                                UpdateExpression="set results_file_archive_id = :a",
                                ExpressionAttributeValues={
                                        ':a': archive_id
                                },
                                ReturnValues="UPDATED_NEW"
                        )

                        # Remove the result file from s3 bucket
                        client.delete_object(Bucket='gas-results', Key=result_file)




if __name__ == '__main__':
        # Call the AnnTools pipeline
        if len(sys.argv) > 1:

        		# Retrieve the job_id, user role and result file
                para = sys.argv[1].split('!')
                job_id = para[0]
                user_role = para[1]
                result = para[2]
                temp = result.split('~')
                result_file = temp[0] + '/' + temp[1]

                # Schedule a task in 30 mins
                s = sched.scheduler(time.time, time.sleep)
                s.enter(1800, 1, archive_data, (job_id, user_role, result_file))
                s.run()

        else:
                print 'A valid argument has to be given to this program.'





