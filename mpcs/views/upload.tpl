<!--
upload.tpl - Direct upload to Amazon S3 using signed POST request
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')

<!-- Upload input file page -->
<div class="container">
	<div class="page-header">
		<h2>Annotate VCF File</h2>
	</div>

	<div class="form-wrapper">
		<form role="form" action="http://gas-inputs.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
			<input type="hidden" name="key" value="zhuoyuzhu/user/{{s3_key_name}}~${filename}" />
			<input type="hidden" name="AWSAccessKeyId" value={{aws_access_key_id}} />
			<input type="hidden" name="x-amz-security-token" value={{aws_session_token}} />
			<input type="hidden" name="acl" value={{acl}} />
			<input type="hidden" name="x-amz-server-side-encryption" value={{encryption}} />
			<input type="hidden" name="success_action_redirect" value={{redirect_url}} />
			<input type="hidden" name="policy" value={{policy}} />
			<input type="hidden" name="signature" value={{signature}} />

      		<div class="row">
        		<div class="form-group col-md-5">
          			<label for="upload">Select VCF Input File</label>
          			<div class="input-group col-md-12">
            			<span class="input-group-btn">
            	<!-- Check if the user is a free user -->
				% if auth.current_user.role == 'free_user':
              			<span class="btn btn-default btn-file btn-lg">Browse&hellip; <input type="file" name="file" id="upload-file" /></span>
				% else:
				<span class="btn btn-default btn-file btn-lg">Browse&hellip; <input type="file" name="file" /></span>
				% end
            			</span>
            			<input type="text" class="form-control" readonly />
          			</div>
        		</div>
      		</div>
		<br />
			<div class="form-actions">
				<input id="Annotate" class="btn btn-lg btn-primary" type="submit" value="Annotate" />
			</div>
    		</form>
  	</div>
  
</div> <!-- container -->

%rebase('views/base', title='GAS - Annotate')
