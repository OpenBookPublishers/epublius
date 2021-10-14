jQuery(document).ready(function() {

    if(localStorage.getItem('cookies') != 'notified'){
	// Normally we would use UIkit.notification('message');
	// but for XHTML compatibility I am toggling visibility
	// of an element on the page.
	$("#cookies-consent").removeClass("uk-hidden");

	localStorage.setItem('cookies', 'notified');
    }
});
