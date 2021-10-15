function is_allowed_size_str(size) {
    return ['small', 'medium', 'large'].indexOf(size) >= 0;
}

$(document).ready(function() {

    const cookieTextSize = localStorage.getItem('text-size');

    if (is_allowed_size_str(cookieTextSize)) {
        $('div[id="mainwin"]').addClass(cookieTextSize);
    }
    $('.zoom-selector').click(function() {
        // we cannot simply use 'small', 'medium', or 'large' as the ID, so
        // we use 'zoom-{size}' - now we strip that part to obtain the size.
        var textSize = $(this).attr('id').replace('zoom-', '');

        if (is_allowed_size_str(textSize)) {
            $('div[id="mainwin"]')
                .removeClass('small medium large')
                .addClass(textSize);
	    localStorage.setItem('text-size', textSize);
            return false;
        }
    });
});
