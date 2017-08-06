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
import driver
import urlparse

# Get the access key and secret key for the current session
session = botocore.session.get_session()
ACCESS_KEY = session.get_credentials().access_key
SECRET_KEY = session.get_credentials().secret_key
session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# Region name
region_name = request.app.config['mpcs.aws.app_region']
# Create a reference of dynamoDB
dynamodb = boto3.resource('dynamodb', region_name = region_name)
ann_table = dynamodb.Table('zhuoyuzhu_annotations')


# A rudimentary timer for coarse-grained profiling
class Timer(object):
        def __init__(self, verbose=False):
                self.verbose = verbose

        def __enter__(self):
                self.start = time.time()
                return self

        def __exit__(self, *args):
                self.end = time.time()
                self.secs = self.end - self.start
                self.msecs = self.secs * 1000  # millisecs
                if self.verbose:
                        print "Elapsed time: %f ms" % self.msecs


if __name__ == '__main__':
        # Call the AnnTools pipeline
        if len(sys.argv) > 1:

		# Get job_id, s3key and file name
                input_file_name = sys.argv[1]
                files = input_file_name.split('/')
                first = input_file_name.find('/')
                second = input_file_name.rindex('/')
                s3key = input_file_name[first + 1:second]
                job_id = files[3]

		# Calculate how much time taken to run the annotation job request
                with Timer() as t:
                        driver.run(input_file_name, 'vcf')
                print "Total runtime: %s seconds" % t.secs

                # Get the input file upload path
                s3 = session.resource('s3')
                bucket = s3.Bucket('gas-results')
                index = input_file_name.rindex('/')
                prefix = input_file_name[:index]
                rindex = input_file_name.find('.')
                filename = input_file_name[index + 1:rindex]
                findex = prefix.find('/')
                path = prefix[findex + 1:index]

		# Upload the result file
                bucket.upload_file(prefix + '/' + filename + '.annot.vcf', 'zhuoyuzhu/' + path + '/' + filename + '.annot.vcf')

                # Upload the log file
                bucket.upload_file(prefix + '/' + filename + '.vcf.count.log', 'zhuoyuzhu/' + path + '/' + filename + '.vcf.count.log')

                # Create a job item and persist it to the annotations database
                result_file = 'zhuoyuzhu/' + s3key + '~' + filename + '.annot.vcf'
                log_file = 'zhuoyuzhu/' + s3key + '~' + filename + '.vcf.count.log'

		# Update annotation job details in DynamoDB
                updateData = ann_table.update_item(
                        Key={
                                'job_id': job_id
                        },
                        UpdateExpression="set s3_results_bucket = :a, s3_key_result_file=:b, s3_key_log_file=:c, complete_time=:d, job_status=:e, results_file_archive_id=:f",
                        ExpressionAttributeValues={
                                ':a': "gas-results",
                                ':b': result_file,
                                ':c': log_file,
                                ':d': int(time.time()),
                                ':e': "COMPLETED",
				':f': "Not available"
                        },
                        ReturnValues="UPDATED_NEW"
                )

		# Update DynamoDB successfully
                print("UpdateItem succeeded:")

                # Clean up (delete) local job files
                shutil.rmtree(prefix)

		# Publish a notification message to the SNS topic
		DBresponse = ann_table.get_item(Key={'job_id': job_id})
        	item = DBresponse['Item']
		email_addr =  item['user_email_addr']
		user_person = item['username']
		user_role = item['user_role']
		completion_time = item['complete_time']
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
        	client = boto3.client('sns')
        	response_notification = client.publish(
                	TopicArn = request.app.config['mpcs.aws.sns.job_complete_topic'],
                	Message = json.dumps(data)
        	)


        else:
                print 'A valid .vcf file must be provided as input to this program.'





