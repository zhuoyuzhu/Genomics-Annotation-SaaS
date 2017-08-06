%include('views/header.tpl')

<!-- User Profile Template -->
<div class="container">
        <div class="page-header">
                <h2>User's Profile</h2>
        </div>
        <br>
        <div class="form-wrapper">
                <table class="table table-hover">
                        <tbody>
                                <tr>
                                        <td><span style="font-weight:bold">Full Name:</span> {{auth.current_user.description}}</td>
                                </tr>
                                <tr>
                                        <td><span style="font-weight:bold">Username:</span> {{auth.current_user.username}}</td>
                                <tr>
                                        <td><span style="font-weight:bold">Subscription Level:</span> {{auth.current_user.role}}</td>
                                </tr>
                                <!-- Check if the user is a free user role -->
				% if auth.current_user.role == 'free_user':
                                <tr>
                                        <td><span style="font-weight:bold">Upgrade to Premium:</span><a href="{{upgrade_link}}"> Upgrade Link</a></td>
                                </tr>
				% end

                        </tbody>
                </table>
        </div>

</div> <!-- container -->

%rebase('views/base', title='GAS - User Profile')
