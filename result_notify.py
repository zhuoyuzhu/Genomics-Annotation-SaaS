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

# Connect to SQS and get the message queue
sqs_conn = boto3.resource('sqs')
my_queue = sqs_conn.get_queue_by_name(QueueName='zhuoyuzhu_job_results')
# Connect to SES
client = boto3.client('ses')


# Send the confirmation email to the user
def send_email(job_id, link, email, user_person, user_role, result_file):

        # Send a job confirmation email to the user with the specified job request link
        response_notification = client.send_email(
        		# Source email address
                Source='zhuoyuzhu@ucmpcs.org',
                Destination={
                        'ToAddresses': [
                                email
                        ]
                },
                Message={
                        'Subject': {
                                'Data': 'Job Result with Job id: ' + job_id,
                                'Charset': 'ascii'
                        },
                        'Body': {
                                'Html': { # Email content
                                        'Data': 'Hi ' + user_person + ',\n\n' + 'You can find your job result with job id:'+ job_id + ' from the link here: ' + link + '\n\nThanks,',
                                        'Charset': 'ascii'
                                }
                        }
                },
                ReplyToAddresses=[
                        'zhuoyuzhu@ucmpcs.org'
                ],
                ReturnPath='zhuoyuzhu@ucmpcs.org'
        )

        # If the user is a free user, we need to schedule an archive job task 30 mins later
        if user_role == 'free_user':
                subprocess.Popen(["python", "archive_free.py", job_id + '!'  + user_role + '!' + result_file])



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
                        msg_body = eval(eval(message.body)['Message'])
                        # Retrieve the message about user from SQS
                        job_id = msg_body['job_id']
                        link = msg_body['link']
                        email = msg_body['email']
                        user_person = msg_body['user_person']
                        user_role = msg_body['user_role']
                        result_file = msg_body['result_file']

                        # Send an email message to the user
                        send_email(job_id, link, email, user_person, user_role, result_file)
                        # Delete the message from the queue, if job was successfully submitted
                        message.delete()


