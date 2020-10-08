function is_allowed_size_str(size) {
    return ['small', 'medium', 'large'].indexOf(size) >= 0;
}

$(document).ready(function() {
    if (is_allowed_size_str($.cookie('TEXT_SIZE'))) {
        $('div[id="mainwin"]').addClass($.cookie('TEXT_SIZE'));
    }
    $('.zoom-selector').click(function() {
        // we cannot simply use 'small', 'medium', or 'large' as the ID, so
        // we use 'zoom-{size}' - now we strip that part to obtain the size.
        var textSize = $(this).attr('id').replace('zoom-', '');

        if (is_allowed_size_str(textSize)) {
            $('div[id="mainwin"]')
                .removeClass('small medium large')
                .addClass(textSize);
            $.cookie('TEXT_SIZE', textSize, { path: '/', expires: 10000 });
            return false;
        }
    });
});
