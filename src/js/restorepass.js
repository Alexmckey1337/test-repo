function sendPassToEmail() {

    let data = {
        'email': document.getElementById('send_letter').value
    };

    let json = JSON.stringify(data);
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/password_forgot/', json, function (data) {
        showPopup(data.detail);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);

        }
    });
}

$("document").ready(function () {
    document.getElementById('getpass').addEventListener('click', function () {
        sendPassToEmail();
    });
};
