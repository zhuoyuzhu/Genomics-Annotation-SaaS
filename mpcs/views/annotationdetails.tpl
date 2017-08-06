%include('views/header.tpl')

<!-- Annotation Details template -->
<div class="container">
        <div class="page-header">
                <h2>Annotation Details</h2>
        </div>
	<br>
        <div class="form-wrapper">
		% for item in items:
                <table class="table table-hover">
                        <tbody>
                                <tr>
                                        <td><span style="font-weight:bold">Request ID:</span> {{item['job_id']}}</td>
                                </tr>
                                <tr>
                                        <td><span style="font-weight:bold">Request Time:</span> {{item['submit_time']}}</td>
                                <tr>
                                        <td><span style="font-weight:bold">VCF Input File:</span> {{item['input_file_name']}}</td>
                                </tr>
				<tr>
                                        <td><span style="font-weight:bold">Status:</span> {{item['job_status']}}</td>
                                </tr>
				<tr>
                    <!-- Check if the job's still running, if not displaying come back later -->
					% if new_link != 2:
                                        <td><span style="font-weight:bold">Complete Time:</span> {{item['complete_time']}}</td>
					% else:
					<td><span style="font-weight:bold">Complete Time:</span> Job's still running!</td>
					% end
                             	</tr>
                        </tbody>
                </table>
		<br>
		<table class="table table-hover">
                        <tbody>
                                <tr>
                                        <td>
                    <!-- Check if the job's still running or if the user is premium -->
					% if new_link == 1:
						<span style="font-weight:bold">Annotated Results File:</span><a href="{{upgrade_url}}"> upgrade to Premium for download</a>
					% elif new_link == 0:
						<span style="font-weight:bold">Annotated Results File:</span><a href="{{download_url}}"> download</a>
					% else:
						<span style="font-weight:bold">Annotated Results File:</span>  Not available, Come back later! Job's still running!
					% end
					</td>
                                </tr>
                                <tr>
                    <!-- Check if the job's still running or if the user is premium -->
					% if new_link != 2:
                                        <td><span style="font-weight:bold">Annotated Log File:</span><a href="{{redirect_url}}"> view</a></td>
					% else:
					<td><span style="font-weight:bold">Annotated Log File:</span> Not available, Come back later! Job's still running!</td>
					% end
                                </tr>
                        </tbody>
                </table>
		% end
		<hr>
		<a href="{{get_url('annotations_list')}}">&larr; Back to annotations list</a>
        </div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Annotation Details')
