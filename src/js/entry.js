let getUrlParameter = function getUrlParameter(sParam) {
    let sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;
    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};
function authUser() {
    let username = document.getElementById('login').value;
    let password = document.getElementById('psw').value;
    let remember_me = document.getElementById('save-profile').checked;
    //let remember = false
    //	if (remember_me.className == 'checkbox active'){
    //		remember = true
    //	}

    let data = {
        "username": username,
        "email": username,
        "password": password,
        "remember_me": !remember_me
    };
    if (checkEmptyFields(username, password) == false) {
        let next;
        let json = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/login/', json, function (JSONobj) {
            //showPopup(JSONobj.message);
            if (JSONobj.status == true) {
                //showPopup(JSONobj.message);
                next = getUrlParameter('next');
                console.log(next);
                if (next) {
                    window.location.href = next;
                } else {
                    window.location.href = '/';
                }
            } else {
                //loginError(JSONobj.message);
                //alert(JSONobj.message)
                clearFields();
                document.querySelector(".account .invalid").style.display = 'block'
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });

    } else {
        document.querySelector(".account .invalid").style.display = 'block';
        clearFields()
    }
}

function clearFields() {
    // document.getElementById('login').value = '';
    document.getElementById('psw').value = '';
}
/*
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
 */
function checkEmptyFields(username, password) {
    let empty = false;
    if (username.length == 0) {
        //  addErrorStyle('login_alert', 'login');
        empty = true;
    }

    if (password.length == 0) {
        //  addErrorStyle('pass_alert', 'psw');
        empty = true;
    }
    return empty;
}

function logIn() {
    // clearStyle()
    authUser();
}

$(document).ready(function () {
    document.getElementById('entry').addEventListener('click', function () {
        logIn();
    });

    $('.entry-input2').keypress(function (e) {
        if (e.which == 13) {
            logIn();
        }
    });

    $('.entry-input1').keypress(function (e) {
        if (e.which == 13) {
            logIn();
        }
    });

});