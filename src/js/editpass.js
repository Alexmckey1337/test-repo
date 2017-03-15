function changePass() {

    let hash = getLastId();

    if (!hash) {
        showPopup('неверный ключ активации');
    }

    let data = {
        "password1": document.getElementsByTagName('input')[0].value,
        "password2": document.getElementsByTagName('input')[1].value,
        "activation_key": hash
    };

    let json = JSON.stringify(data);
    ajaxRequest('/api/v1.0/password_view/', json, function (data) {
        showPopup(data.detail);
        setTimeout(function () {
            window.location.href = '/entry/';
        }, 1500);
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
    document.getElementById('create').addEventListener('click', function () {
        changePass()
    })
});
