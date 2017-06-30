function sendPassToEmail() {

    let data = {
        'email': document.getElementById('send_letter').value
    };

    let json = JSON.stringify(data);
    ajaxRequest(URLS.password_forgot(), json, function (data) {
        showPopup(data.detail);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);

        },
        500: function () {
            $('.account .invalid').html('Проверьте введённый e-mail').show();
            $('#send_letter').val('');
        }
    });
}

$("document").ready(function () {
    document.getElementById('getpass').addEventListener('click', function () {
        sendPassToEmail();
    })
});