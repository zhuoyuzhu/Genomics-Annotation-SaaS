from bottle import route, run, request, response, error, post, get, template
from datetime import datetime, timedelta
from boto3 import client
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr
import requests
import uuid
import time
import boto3
import os
import shutil
import os.path
import json
import subprocess
import botocore.session
import boto3
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

# Connect to SQS and get the message queue
sqs_conn = boto3.resource('sqs')
my_queue = sqs_conn.get_queue_by_name(QueueName='zhuoyuzhu_glacier')

# DynamoDB reference
dynamodb = boto3.resource('dynamodb')
ann_table = dynamodb.Table('zhuoyuzhu_annotations')


def restore(job_id, arch_id):

        # Start restoring process
        print 'Restore'
        client = boto3.client('glacier')
        re = client.get_job_output(vaultName='ucmpcs',jobId=job_id)
        # Read the content of archive job details
        body = re['body']

        # Retrieve the job details based on the archive id 
        res = ann_table.query(
                        IndexName='results_file_archive_id_index',
                        KeyConditionExpression=Key('results_file_archive_id').eq(arch_id))
        items = res['Items']
        input_file = items[0]['input_file_name']
        result_file = items[0]['s3_key_result_file']
        temp1 = input_file.split('.')
        file_upload = temp1[0] + '.annot.' + temp1[1]
        temp2 = result_file.split('~')
        directory = temp2[0] + '/' + file_upload

        user_data = temp2[0].split('/')
        user = user_data[2]

        # Check if the user exists
        d = 'RestoreJob/user/' + user + '/'
        if os.path.exists(d) == False:
                os.mkdir(d)


        # Create an archive job directory for each restoring request
        file_directory = d + '' + arch_id + '/'
        os.mkdir(file_directory)

        # Write the content to the result file 
        f = open(file_directory + '' + file_upload, 'w+')
        f.write(body.read())
        f.close()

        # Upload to S3 result bucket
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('gas-results')
        bucket.upload_file(file_directory + '' + file_upload, directory)

        # Remove archive job directory
        shutil.rmtree(file_directory)

        # Finsih the restoring job
        print 'Done'



# Poll the message queue in a loop
while True:

        # Attempt to read a message from the queue
        # Use long polling - DO NOT use sleep() to wait between polls
        print("Asking SQS for up to 10 messages...")
        # Get messages
        messages = my_queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=20)

        if len(messages) > 0:
                print('Got messages')
                for message in messages:
                        # Retrieve the message from Amazon SQS
                        msg_body = json.loads(eval(message.body)['Message'])

                        # Get the archive job id and archive id
                        job_id = msg_body['JobId']
                        print 'Restore job id:' + job_id
                        arch_id = msg_body['ArchiveId']
                        print 'ArchiveId: ' + arch_id

                        # Restore the result file from Amazon Glacier to S3 result bucket
                        restore(job_id, arch_id)

                        # Delete the message from the queue, if job was successfully submitted
                        message.delete()


