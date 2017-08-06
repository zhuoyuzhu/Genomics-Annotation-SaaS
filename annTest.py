__author__ = 'Zhuoyu Zhu <zhuoyuzhu@uchicago.edu>'

from bottle import route, run, request, response, error, post, get, template
from datetime import datetime, timedelta
from boto3 import client
from boto3.session import Session
import requests
import uuid
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
import re
import pytz
import sys
import time
import urlparse

count = 0
while True:

	# The message data we will publish to the topic
    data = {
        "job_id": job_id,
        "link": "https://zhuoyuzhu.ucmpcs.org/annotations/" + job_id,
		"email": email_addr,
		"user_person": user_person,
		"user_role": user_role,
		"completion_time": int(completion_time),
		"result_file": item['s3_key_result_file']
    }

    if count > 10:
    	time.sleep(120)
    	count = count - 8

    client = boto3.client('sns')
    response_notification = client.publish(
    	TopicArn = 'arn:aws:sns:us-east-1:127134666975:zhuoyuzhu_job_request_notify',
        Message = json.dumps(data)
	)
	count = count + 1
    time.sleep(25)



