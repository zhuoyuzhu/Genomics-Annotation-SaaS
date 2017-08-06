<!--
subscribe.tpl - Get user's credit card details to send to Stripe service
Copyright (C) 2011-2017 Vas Vasiliadis <vas@uchicago.edu>
University of Chicago
-->

%include('views/header.tpl')
<!-- Captures the user's credit card information and uses Javascript to send to Stripe -->

<!-- Subscribe to Stripe Premium user page -->
<div class="container">
	<div class="page-header">
		<h2>Subscribe</h2>
	</div>

	<p>You are subscribing to the GAS Premium plan. Please enter your credit card details to complete your subscription.</p><br />
	
	<div class="form-wrapper">
		    <form role="form" action="/subscribe" method="post" id="subscribe_form" name="subscribe_submit">

		        <div class="row">
			        <div class="form-group col-md-5">
		            	<label for="creditcardname">Name on credit card:</label>
				<input class="form-control input-lg required" type="text" size="20" data-stripe="name" placeholder="Enter your name on credit card"/>
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-5">
		            	<label for="creditcardnumber">Credit card number:</label>
		                <input class="form-control input-lg required" type="text" size="20" data-stripe="number" placeholder="Enter your credit card number"/>
		            </div>
		        </div>

		        <div class="row">
			        <div class="form-group col-md-5">
			        <label for="verificationcode">Credit card verification code:</label>
				<input class="form-control input-lg required" type="text" size="20" data-stripe="cvc" placeholder="Enter your credit card verification code"/>
		            </div>
		        </div>

		        <div class="row">
                                <div class="form-group col-md-5">
                                <label for="expirationmonth">Credit card expiration month:</label>
				<input class="form-control input-lg required" type="text" size="20" data-stripe="exp-month" placeholder="Enter your credit card expiration month"/>
                            </div>
                        </div>

			<div class="row">
                                <div class="form-group col-md-5">
                                <label for="expirationyear">Credit card expiration year:</label>
				<input class="form-control input-lg required" type="text" size="20" data-stripe="exp-year" placeholder="Enter your credit card expiration year"/>
                            </div>
                        </div>

		        <br />
		        <div class="form-actions">
		            <input id="bill-me" class="btn btn-lg btn-primary" type="submit" value="Subscribe">
		        </div>
		    </form>
	    </div>

</div> <!-- container -->

%rebase('views/base', title='GAS - Subscribe')
