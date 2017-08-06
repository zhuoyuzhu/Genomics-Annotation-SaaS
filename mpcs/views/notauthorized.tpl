%include('views/header.tpl')

<!-- If the user is not authoized to view certain page -->
<div class="container">
        <div class="page-header">
                <h2>Annotation Details</h2>
        </div>
        <br>
        <div class="form-wrapper">
                <h3>Not authorized to view this job</h3>
        </div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Not authorized to view')
