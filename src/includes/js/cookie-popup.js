jQuery(document).ready(function() {

    if(localStorage.getItem('cookies') != 'notified'){
	window.alert('cookies alert');

	localStorage.setItem('cookies', 'notified');
    }
});
