%include('views/header.tpl')
<!-- Annotation Log file Content Template -->
<div class="container">
        <div class="page-header">
                <h2>Annotation Details</h2>
        </div>
        <br>
        <div class="form-wrapper">
                <p>{{log_content}}</p>
        </div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Log File Content')
