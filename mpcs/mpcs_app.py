# mpcs_app.py
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
#
# Application logic for the GAS
#
##
__author__ = 'Zhuoyu Zhu <zhuoyuzhu@uchicago.edu>'

import stripe
import base64
import datetime
import hashlib
import hmac
import json
import sha
import string
import time
import urllib
import urlparse
import uuid
import boto3
import subprocess
import boto3
import botocore
import pytz
import botocore.session
from boto3.dynamodb.conditions import Key
from mpcs_utils import log, auth
from bottle import route, request, response, redirect, template, static_file, run, post, get
from datetime import datetime, timedelta
from boto3 import client
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr

# Use the boto session object only to get AWS credentials
session = botocore.session.get_session()
aws_access_key_id = str(session.get_credentials().access_key)
aws_secret_access_key = str(session.get_credentials().secret_key)
aws_session_token = str(session.get_credentials().token)

# Create a reference of dynamoDB
region_name = request.app.config['mpcs.aws.app_region']
dynamodb = boto3.resource('dynamodb', region_name = region_name)
ann_table = dynamodb.Table(request.app.config['mpcs.aws.dynamodb.annotations_table'])

# Define s3 policy property
bucket_name = request.app.config['mpcs.aws.s3.inputs_bucket']
encryption = request.app.config['mpcs.aws.s3.encryption']
acl = request.app.config['mpcs.aws.s3.acl']
result_bucket = request.app.config['mpcs.aws.s3.results_bucket']

# Job Request Topic
job_request_topic = request.app.config['mpcs.aws.sns.job_request_topic']


'''
*******************************************************************************
Set up static resource handler - DO NOT CHANGE THIS METHOD IN ANY WAY
*******************************************************************************
'''
@route('/static/<filename:path>', method='GET', name="static")
def serve_static(filename):
  # Tell Bottle where static files should be served from
  return static_file(filename, root=request.app.config['mpcs.env.static_root'])

'''
*******************************************************************************
Home page
*******************************************************************************
'''
@route('/', method='GET', name="home")
def home_page():
	log.info(request.url)
	return template(request.app.config['mpcs.env.templates'] + 'home', auth=auth)

'''
*******************************************************************************
Registration form
*******************************************************************************
'''
@route('/register', method='GET', name="register")
def register():
  log.info(request.url)
  return template(request.app.config['mpcs.env.templates'] + 'register',
    auth=auth, name="", email="", username="", 
    alert=False, success=True, error_message=None)

@route('/register', method='POST', name="register_submit")
def register_submit():
  try:
    auth.register(description=request.POST.get('name').strip(),
                  username=request.POST.get('username').strip(),
                  password=request.POST.get('password').strip(),
                  email_addr=request.POST.get('email_address').strip(),
                  role="free_user")
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register', 
      auth=auth, alert=True, success=False, error_message=error)  

  return template(request.app.config['mpcs.env.templates'] + 'register', 
    auth=auth, alert=True, success=True, error_message=None)

@route('/register/<reg_code>', method='GET', name="register_confirm")
def register_confirm(reg_code):
  log.info(request.url)
  try:
    auth.validate_registration(reg_code)
  except Exception, error:
    return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
      auth=auth, success=False, error_message=error)

  return template(request.app.config['mpcs.env.templates'] + 'register_confirm',
    auth=auth, success=True, error_message=None)

'''
*******************************************************************************
Login, logout, and password reset forms
*******************************************************************************
'''
@route('/login', method='GET', name="login")
def login():
  log.info(request.url)
  redirect_url = "/"
  # If the user is trying to access a protected URL, go there after auhtenticating
  if request.query.redirect_url.strip() != "":
    redirect_url = request.query.redirect_url

  return template(request.app.config['mpcs.env.templates'] + 'login', 
    auth=auth, redirect_url=redirect_url, alert=False)

@route('/login', method='POST', name="login_submit")
def login_submit():
  auth.login(request.POST.get('username'),
             request.POST.get('password'),
             success_redirect=request.POST.get('redirect_url'),
             fail_redirect='/login')

@route('/logout', method='GET', name="logout")
def logout():
  log.info(request.url)
  auth.logout(success_redirect='/login')


'''
*******************************************************************************
*
CORE APPLICATION CODE IS BELOW...
*
*******************************************************************************
'''

'''
*******************************************************************************
Subscription management handlers
*******************************************************************************
'''
import stripe

# Display form to get subscriber credit card info
@route('/subscribe', method='GET', name="subscribe")
def subscribe():
	
	log.info(request.url)
  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)

	return template(request.app.config['mpcs.env.templates'] + 'subscribe', auth=auth, alert=False)

# Process the subscription request
@route('/subscribe', method='POST', name="subscribe_submit")
def subscribe_submit():
	log.info(request.url)
  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)

  try:

	 # Extract the Stripe token from submited form -- stripe_token
	 stripe.api_key = request.app.config['mpcs.stripe.secret_key']
	 token = request.POST['stripe_token']

   # Create a premium customer subscribing to premium plan
	 print 'Welcome to Stripe'
	 customer = stripe.Customer.create(description=auth.current_user.username, source=token, email=auth.current_user.email_addr)
	 stripe.Subscription.create(customer=customer.id, plan="premium_plan",)
	
	 # Update the user's profile in our user database
	 auth.current_user.update(role="premium_user")
  except stripe.error.CardError, e:
    print 'This credit card has been declined'


  # Get the current username
	username = auth.current_user.username
	res = ann_table.query(
                        IndexName='username_index',
                        KeyConditionExpression=Key('username').eq(username))
  items = res['Items']
  client = boto3.client('glacier', region_name = region_name)

	# Check if we have any job within our DynamoDB
	if len(items) > 0:
		for item in items:
			# Update the user role to premium in DynamoDB
			updateData = ann_table.update_item(
				Key={
					'job_id': item['job_id']
				},
				UpdateExpression="set user_role=:a",
				ExpressionAttributeValues={
					':a': "premium_user"
				},
				ReturnValues="UPDATED_NEW"
			)

			# Check if we should initiate archive request
			if item['results_file_archive_id'] != 'Not available':
				re = client.initiate_job(vaultName='ucmpcs', jobParameters={"Type": "archive-retrieval", "ArchiveId": item['results_file_archive_id'], "SNSTopic": request.app.config['mpcs.aws.sns.glacier_topic'], "Tier": "Expedited"})
				
	return template(request.app.config['mpcs.env.templates'] + 'subscribe_confirm', auth=auth, stripe_id=customer.id, alert=False)



'''
*******************************************************************************
Display the user's profile with subscription link for Free users
*******************************************************************************
'''
@route('/profile', method='GET', name="profile")
def user_profile():
	log.info(request.url)
  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
	# Upgrade link to become a premium user
  temp = str(request.url).split('/profile')
  upgrade_link = temp[0] + '/subscribe'

	return template(request.app.config['mpcs.env.templates'] + 'profile', auth=auth, upgrade_link=upgrade_link, alert=False)


'''
*******************************************************************************
Creates the necessary AWS S3 policy document and renders a form for
uploading an input file using the policy document
*******************************************************************************
'''
@route('/annotate', method='GET', name="annotate")
def upload_input_file():
	log.info(request.url)

  # Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)

  # Generate unique ID to be used as S3 key (name)
  key_name = auth.current_user.username + '/' + str(uuid.uuid4())

  # Redirect to a route that will call the annotator
  redirect_url = str(request.url) + "/job"	

  # Get the current time
	current = datetime.now(pytz.timezone('US/Central'))
        expiration = current + timedelta(hours=24)
        expiration = expiration.isoformat()
        time = expiration[:23]
        time = time + "Z"


  # Define the S3 policy doc to allow upload via form POST
  policy_document = str({
    "expiration": time,
    "conditions": [
      {"bucket": bucket_name},
      ["starts-with","$key", request.app.config['mpcs.aws.s3.key_prefix']],
      ["starts-with", "$success_action_redirect", redirect_url],
      {"x-amz-server-side-encryption": encryption},
      {"x-amz-security-token": aws_session_token},
      {"acl": acl}]})

  # Encode the policy document - ensure no whitespace before encoding
  policy = base64.b64encode(policy_document.translate(None, string.whitespace))

  # Sign the policy document using the AWS secret key
  signature = base64.b64encode(hmac.new(aws_secret_access_key, policy, hashlib.sha1).digest())

  # Render the upload form
  return template(request.app.config['mpcs.env.templates'] + 'upload',
    auth=auth, bucket_name=bucket_name, s3_key_name=key_name,
    aws_access_key_id=aws_access_key_id,     
    aws_session_token=aws_session_token, redirect_url=redirect_url,
    encryption=encryption, acl=acl, policy=policy, signature=signature)


'''
*******************************************************************************
Accepts the S3 redirect GET request, parses it to extract 
required info, saves a job item to the database, and then
publishes a notification for the annotator service.
*******************************************************************************
'''
@route('/annotate/job', method='GET')
def create_annotation_job_request():

	# Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)

	# Get bucket name, key, and job ID from the S3 redirect URL
  bucket_name = request.query['bucket']
  s3key = request.query['key']
      
  # Get the file name  
	filename = s3key.split("~")[1]
        index = s3key.split("~")[0].rindex('/')
        job_id = s3key.split("~")[0][index + 1:]
        first = s3key.find('/')
        second = s3key.rindex('/')

  # Create a job item and persist it to the annotations database
  data = {
          "job_id": job_id,
          "username": auth.current_user.username,
          "input_file_name": filename,
          "s3_inputs_bucket": bucket_name,
          "s3_key_input_file": s3key,
          "submit_time": int(time.time()),
          "job_status": "PENDING",
		      "user_email_addr": auth.current_user.email_addr,
		      "user_role": auth.current_user.role
  }

  # Insert the new data into data table
  ann_table.put_item(Item=data)

  # Publish a notification message to the SNS topic
  client = boto3.client('sns', region_name = region_name)
  response_notification = client.publish(
          TopicArn = job_request_topic,
          Message = json.dumps(data)
  )
  
  # Render upload_confirm template      
	return template(request.app.config['mpcs.env.templates'] + 'upload_confirm', auth=auth, job_id=job_id, alert=False)


'''
*******************************************************************************
List all annotations for the user
*******************************************************************************
'''
@route('/annotations', method='GET', name="annotations_list")
def get_annotations_list():
	# Check that user is authenticated
	auth.require(fail_redirect='/login?redirect_url=' + request.url)

  # Get the current username
	username = auth.current_user.username
	res = ann_table.query(
			IndexName='username_index', 
			KeyConditionExpression=Key('username').eq(username))

  # Get all the relevant detail about current user
	items = res['Items']

  # Modify the date and time format that is rendered into template file
	result_data = list()
	for item in items:
		item['submit_time'] = datetime.fromtimestamp(int(item['submit_time'])).strftime('%Y-%m-%d %H:%M')
		result_data.append(item)
	
  # Render myannotations template
	return template(request.app.config['mpcs.env.templates'] + 'myannotations', auth=auth, items=result_data, alert=False)


'''
*******************************************************************************
Display details of a specific annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>', method='GET', name="annotation_details")
def get_annotation_details(job_id):
	# Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
	
  # Get the current user name
  username = auth.current_user.username
	res = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
  items = res['Items']

	download_url = ''
	# Construct a signed download URL for user to download result file from s3 bucket
	if items[0]['job_status'] != 'RUNNING':
		resultfile = items[0]['s3_key_result_file'].split('~')
		client = boto3.client('s3')
		download_url = client.generate_presigned_url(
				ClientMethod='get_object', 
				Params = {
					'Bucket': request.app.config['mpcs.aws.s3.results_bucket'], 
					'Key': resultfile[0] + '/' + resultfile[1]
				}
		)

  # Display annotation detail for specified job
	current_time = 0
  # Check if the job is still running
	if items[0]['job_status'] == 'RUNNING':
		new_link = 2
		
    # Check if the given username match the username within database
		if username == items[0]['username']:
      # Modify the date and time format that is rendered into template file
      result_data = list()
      for item in items:
        item['submit_time'] = datetime.fromtimestamp(int(item['submit_time'])).strftime('%Y-%m-%d %H:%M')
        result_data.append(item)

      # Display annotation job detail template
      return template(request.app.config['mpcs.env.templates'] + 'annotationdetails', auth=auth, items=result_data, new_link=new_link, alert=False)
    else:
      # Display the not authorized template if username doesn't match
      return template(request.app.config['mpcs.env.templates'] + 'notauthorized', auth=auth, alert=False)

  # The specified job has completed
	else:
		current_time = int(items[0]['complete_time'])
		time_pass = int(time.time()) - current_time
		new_link = 0

    # Check if 30mins passed and the current user is a free user role
		if time_pass > 1800 and auth.current_user.role == 'free_user':
			new_link = 1

    # redirect url and upgrade url
		redirect_url = str(request.url) + "/log"
    temp = str(request.url).split('/')
		upgrade_url = temp[0] + '/subscribe'
		if username == items[0]['username']:
			# Modify the date and time format that is rendered into template file
      result_data = list()

      # Convert the date into standard format
      for item in items:
        item['submit_time'] = datetime.fromtimestamp(int(item['submit_time'])).strftime('%Y-%m-%d %H:%M')
        item['complete_time'] = datetime.fromtimestamp(int(item['complete_time'])).strftime('%Y-%m-%d %H:%M')
        result_data.append(item)

      return template(request.app.config['mpcs.env.templates'] + 'annotationdetails', auth=auth, items=result_data, download_url=download_url, redirect_url=redirect_url, new_link=new_link, upgrade_url=upgrade_url, alert=False)
		else:
			return template(request.app.config['mpcs.env.templates'] + 'notauthorized', auth=auth, alert=False)


'''
*******************************************************************************
Display the log file for an annotation job
*******************************************************************************
'''
@route('/annotations/<job_id>/log', method='GET', name="annotation_log")
def view_annotation_log(job_id):
	# Check that user is authenticated
  auth.require(fail_redirect='/login?redirect_url=' + request.url)
	
  # Get all the relevant detail about the specified job id
  res = ann_table.query(KeyConditionExpression=Key('job_id').eq(job_id))
  items = res['Items']

	# Display the log file in the browser
  logfile = items[0]['s3_key_log_file'].split('~')
  s3 = boto3.resource('s3')
  obj = s3.Object(result_bucket, logfile[0] + '/' + logfile[1])
  log_content =  obj.get()['Body'].read().decode('utf-8')

  # Render the log file content
	return template(request.app.config['mpcs.env.templates'] + 'logcontent', auth=auth, log_content=log_content, alert=False)


### EOF
