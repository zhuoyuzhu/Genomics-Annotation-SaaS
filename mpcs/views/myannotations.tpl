%include('views/header.tpl')

<!-- Displaying all the annotation jobs belonging to user -->
<div class="container">
	<div class="page-header">
		<h2>My Annotations</h2>
	</div>

	<div class="form-actions">
		<a href="{{get_url('annotate')}}"><input class="btn btn-lg btn-primary" type="submit" value="Request New Annotations" /></a>
		<br><br><hr>
        </div>

	<div class="form-wrapper">

  		<table class="table table-hover">
    			<thead>
      				<tr>
        				<th>Request ID</th>
        				<th>Request Time</th>
        				<th>VCF File Name</th>
					<th>Status</th>
      				</tr>
    			</thead>
    			<tbody>
          <!-- Displaying all the annotation jobs belonging to user -->
				<% if len(items) != 0: 
					for item in items: %>  
				
            <tr>
                <td><a href="https://zhuoyuzhu.ucmpcs.org/annotations/{{item['job_id']}}">{{item['job_id']}}</a></td>
                <td>{{item['submit_time']}}</td>
                <td>{{item['input_file_name']}}</td>
                <td>{{item['job_status']}}</td>
            </tr>
					% end
				% end
					
    			</tbody>
  		</table>
  	</div>

</div> <!-- container -->

%rebase('views/base', title='GAS - My Annotations')
