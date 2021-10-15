function is_allowed_size_str(size) {
    return ['small', 'medium', 'large'].indexOf(size) >= 0;
}

document.addEventListener("DOMContentLoaded", function() {

    let textSize = localStorage.getItem('text-size');
    let mainwin = document.querySelector('#mainwin')

    if (is_allowed_size_str(textSize)) {
	mainwin.classList.add(textSize);
    }

    const selectors = document.querySelectorAll('.zoom-selector');

    selectors.forEach(el => el.addEventListener('click', event => {
        // we cannot simply use 'small', 'medium', or 'large' as the ID, so
        // we use 'zoom-{size}' - now we strip that part to obtain the size.
	const button = event.target.parentNode;
        textSize = button.getAttribute('id').replace('zoom-', '');

        if (is_allowed_size_str(textSize)) {
            mainwin.classList.remove('small', 'medium', 'large')
            mainwin.classList.add(textSize);

	    localStorage.setItem('text-size', textSize);
        }
    }));
});
