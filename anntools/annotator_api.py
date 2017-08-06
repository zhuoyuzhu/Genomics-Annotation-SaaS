from bottle import route, run, request, response, error, post, get, template
from datetime import datetime, timedelta
from boto3 import client
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr
import requests
import uuid
import os.path
import json
import time
import subprocess
import botocore.session
import boto3
import botocore
import hmac
import hashlib
import base64
import re
import pytz
import urllib2

# Get the access key and secret key for the current session
session = botocore.session.get_session()
ACCESS_KEY = session.get_credentials().access_key
SECRET_KEY = session.get_credentials().secret_key


# Homework 5
@route('/annotations', method='POST')
def run_annotation():
        # Extract job parameters from the request body (NOT the URL query string!)
        body = request.body.read()
        res = json.loads(body)

        bucket_name = res['s3_inputs_bucket']
        job_id = res['job_id']
        filename = res['input_file_name']
        s3key = res['s3_key_input_file']
        user = res['username']

        # Get the input file S3 object and copy it to a local file
        session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_name)

        # Check if the user exists
        d = 'AnnotationResult/user/' + user + '/'
        if os.path.exists(d) == False:
                os.mkdir(d)

        directory = 'AnnotationResult/user/' + user + '/' + job_id + '/'
        os.mkdir(directory)

        # Download the input file from s3 input bucket
        bucket.download_file(s3key, 'AnnotationResult/user/' + user + '/' +  job_id + '/' + filename)
        # Launch annotation job as a background process
        subprocess.Popen(["python", "run.py", 'AnnotationResult/user/' + user + '/' + job_id + '/' + filename])
        response.status = 200
        f = open('AnnotationResult/user/' + user + '/' + job_id + '/status.txt', 'w+')
        f.write("code:\t" + response.status + "\tdata:\t" + str(job_id) + "\tfilename:\t" + filename + '\n')
        f.close()

        # Return response to notify user of successful submission
        data = {'id': job_id, 'input_file': filename}
        return json.dumps({'code': response.status, 'data': data})



run(host='0.0.0.0', port=8888, debug=True, reloader=True)


