document.addEventListener('DOMContentLoaded', function() {
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    const body = document.body;

    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            body.className = '';
            body.classList.add(this.value + '-theme');
        });
    });
});
