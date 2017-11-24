window.onload = function () {
    var input = document.getElementById('code'),
        select = document.getElementById('summit');

    input.value = '';
    input.focus();
    select.addEventListener('change', function () {
        input.value = '';
        input.focus();
    });
    document.body.addEventListener("click", function (event) {
        (event.target.tagName != 'SELECT') && input.focus();
    })
};
