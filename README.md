# Genomics-Annotation-SaaS

Section 1 —- A full-functional GAS accessible: https://zhuoyuzhu.ucmpcs.org

a. Two instances running the web application: zhuoyuzhu-capstone-webserver

b. Two instances running the annotator: zhuoyuzhu-capstone-annotator

c. One instance running job result notify and archive: zhuoyuzhu-Utilities

d. One instance running restoring job from Glacier to S3 bucket: zhuoyuzhu-Restore

e. Existing username: michaelzhu Password: miller911


Section 2 —- Full source code

a. Web Server EC2 Python code (mpcs folder): mpcs_app.py

b. Annotator EC2 Python code (anntools folder): jobs_runner.py and run.py

c. Utilitise EC2 Python code: result_notify.py and archive_free.py

d. Restore EC2 Python code: restore.py

e. Template created and changed: annotationdetails.tpl, logcontent.tpl, myannotations.tpl, notauthorized.tpl, profile.tpl, script.tpl(upload file validation for free user), subscribe_confirm.tpl, subscribe.tpl, upload_confirm.tpl, upload.tpl

f. AWS Web Server EC2 user data file: auto_scaling_user_data_web_server.txt

g. AWS Annotator EC2 user data file: auto_scaling_user_data_annotator.txt

h. Configuration files (mpcs folder): mpcs.conf

i. Load test the annotator farm: annTest.py


Section 3 —- Capstone project Zhuoyu Zhu (Include all the screenshots and explanation)

1. Capstone Project—Zhuoyu Zhu.pdf: Describe the approaches used for archive job 

2. For Stripe credit card testing: Use https://stripe.com/docs/testing#cards


Section 4 —- Reference:

1. JavaScript file upload size validation: https://stackoverflow.com/questions/3717793/javascript-file-upload-size-validation

2. Publish SNS message for Lambda function via boto3 (Python2): http://stackoverflow.com/questions/34029251/aws-publish-sns-message-for-lambda-function-via-boto3-python2

3. Insert, Update, Read from DynamoDB: http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.Python.03.html#GettingStarted.Python.03.03

4. Download a file from s3 bucket: http://stackoverflow.com/questions/29378763/how-to-save-s3-object-to-a-file-using-boto3

5. Upload files from s3 bucket: http://stackoverflow.com/questions/37017244/uploading-a-file-to-a-s3-bucket-with-a-prefix-using-boto3

6. Send an email message to user’s email: http://boto3.readthedocs.io/en/latest/reference/services/ses.html#ses

7. Iterate displaying multiple job details within template: https://bottlepy.org/docs/dev/stpl.html

8. User download result file to local PC: https://stackoverflow.com/questions/43215889/downloading-a-file-from-an-s3-bucket-to-the-users-computer

9. How to generate url from boto3 in amazon web services: https://stackoverflow.com/questions/33549254/how-to-generate-url-from-boto3-in-amazon-web-services

10. Archive result files from S3 bucket to Glacier: https://stackoverflow.com/questions/41833565/s3-buckets-to-glacier-on-demand-is-it-possible-from-boto3-api

11. Event scheduler (sched) for archive request: https://docs.python.org/2/library/sched.html

12. Run subprocess: https://docs.python.org/2/library/subprocess.html

13. Extract the Stripe token from the submitted form: https://stripe.com/docs/charges

14. Create a new Stripe customer: https://stripe.com/docs/api?lang=python#create_customer

15. Initiate a Glacier archive retrieval job: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html#Glacier.Client.initiate_job

16. Get object details restored from Glacier: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html#Glacier.Job.get_output

