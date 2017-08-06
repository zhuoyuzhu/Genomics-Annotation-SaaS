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

# Region name
region_name = request.app.config['mpcs.aws.app_region']
# Connect to SQS and get the message queue
sqs_conn = boto3.resource('sqs', region_name)
my_queue = sqs_conn.get_queue_by_name(QueueName=request.app.config['mpcs.aws.sqs.job_request_queue'])

# Create a reference of dynamoDB
dynamodb = boto3.resource('dynamodb', region_name)
ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])

# Run annotation analysis job request
def run_annotation(job_id, user, filename, bucket_name, s3key):

	# Get the s3 bucket
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # Check if the user exists
    d = 'AnnotationResult/user/' + user + '/'
    if os.path.exists(d) == False:
    	os.mkdir(d)

	# Create a directory for each submitted job_id request
    directory = 'AnnotationResult/user/' + user + '/' + job_id + '/'
    os.mkdir(directory)

    # Download the input file from s3 input bucket
    bucket.download_file(s3key, 'AnnotationResult/user/' + user + '/' +  job_id + '/' + filename)

	# Update the job status only if the current status is pending
	DBresponse = ann_table.get_item(Key={'job_id': job_id})
	item = DBresponse['Item']
	if item['job_status'] == 'PENDING':
		ann_table.update_item(Key={'job_id': job_id}, UpdateExpression='SET job_status = :v', ExpressionAttributeValues= {':v': 'RUNNING'})

        # Launch annotation job as a background process
        subprocess.Popen(["python", "run.py", 'AnnotationResult/user/' + user + '/' + job_id + '/' + filename])
        response.status = 200
        f = open('AnnotationResult/user/' + user + '/' + job_id + '/status.txt', 'w+')
        f.write("code:\t" + response.status + "\tdata:\t" + str(job_id) + "\tfilename:\t" + filename + '\n')
        f.close()



# Poll the message queue in a loop 
while True:

	# Attempt to read a message from the queue
	# Use long polling to wait between polls
	print("Asking SQS for up to 10 messages...")
	# Get messages
	messages = my_queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=20)

	if len(messages) > 0:
		print('Got messages')
		for message in messages:
			# Retrieve the message details
			msg_body = eval(eval(message.body)['Message'])
			job_id = msg_body['job_id'] 
			username = msg_body['username']
			filename = msg_body['input_file_name']
			bucket_name = msg_body['s3_inputs_bucket']
			s3_key = msg_body['s3_key_input_file']

			# Run annotation analysis
			run_annotation(job_id, username, filename, bucket_name, s3_key)

    		# Delete the message from the queue, if job was successfully submitted
			message.delete()



