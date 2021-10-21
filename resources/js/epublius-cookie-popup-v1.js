/* Epublius Cookie Popup v1 | https://github.com/OpenBookPublishers/epublius | (c) 2013 - 2021 Open Book Publishers | GPLv3 License */

document.addEventListener("DOMContentLoaded", function() {

    if(localStorage.getItem('cookies') != 'notified'){
	// Normally we would use UIkit.notification('message');
	// but for XHTML compatibility I am toggling visibility
	// of an element on the page.
	document.querySelector('#cookies-consent')
	    .classList.toggle('uk-hidden');

	localStorage.setItem('cookies', 'notified');
    }
});
