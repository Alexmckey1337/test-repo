function authUser() {
    var username = document.getElementById('login').value;
    var password = document.getElementById('psw').value;
    //var remember_me = document.getElementById('remember_me').getElementsByTagName("INPUT")[0]
    var remember = false
        //	if (remember_me.className == 'checkbox active'){
        //		remember = true
        //	}
    var data = {
        "username": username,
        "email": username,
        "password": password,
        'remember_me': remember
    }
    if (checkEmptyFields(username, password) == false) {

        var json = JSON.stringify(data);
        ajaxRequest(config.DOCUMENT_ROOT+'api/login/', json, function(JSONobj) {
            showPopup(JSONobj.message);
            if (JSONobj.status == true) {
                setTimeout(function() {
                    window.location.href = '/events';
                }, 1500);
            } else {
                loginError(JSONobj.message);
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });

    }
}

function loginError(text) {
    document.getElementById('error_alert').innerHTML = '* ' + text;
    document.getElementById('error_alert').style.display = 'block';
    document.getElementById('login').style.border = '1px solid #DC3030'
    document.getElementById('psw').style.border = '1px solid #DC3030'
}

function clearStyle() {
    document.getElementById('error_alert').style.display = 'none'
    document.getElementById('login_alert').style.display = 'none'
    document.getElementById('pass_alert').style.display = 'none'
    document.getElementById('login').style.border = '1px solid #fff'
    document.getElementById('psw').style.border = '1px solid #fff'
}

function addErrorStyle(errorId, fieldId) {
    document.getElementById(errorId).style.display = 'block'
    document.getElementById(fieldId).style.border = '1px solid #DC3030'
}

function checkEmptyFields(username, password) {
    var empty = false
    if (username.length == 0) {
        addErrorStyle('login_alert', 'login');
        empty = true;
    }

    if (password.length == 0) {
        addErrorStyle('pass_alert', 'psw');
        empty = true;
    }
    return empty;
}

function logIn() {
    clearStyle()
    authUser();
}