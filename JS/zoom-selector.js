$(document).ready(function() {
	if($.cookie('TEXT_SIZE')) {
		$('div[id="mainwin"]').addClass($.cookie('TEXT_SIZE'));	
	}
	$('.zoom-selector').click(function() {
		var textSize = $(this).attr('class');
		$('div[id="mainwin"]').removeClass('small medium large').addClass(textSize);
		$.cookie('TEXT_SIZE',textSize, { path: '/', expires: 10000 });
		return false;
	});
});
