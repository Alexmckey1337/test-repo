import URLS from './modules/Urls/index';
import {setCookie} from './modules/Cookie/cookie';
import ajaxRequest from './modules/Ajax/newAjaxRequest';
import {hidePopup} from './modules/Popup/popup';

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

    let data = {
        "username": username,
        "email": username,
        "password": password,
        "remember_me": !remember_me
    };
    if (checkEmptyFields(username, password) == false) {
        let next;
        let loginData = JSON.stringify(data);
        authUserFunc(loginData).then(function (res) {
            if (res.status) {
                setCookie('key', res.key, {
                    path: '/'
                });
                next = getUrlParameter('next');
                if (next) {
                    window.location.href = next;
                } else {
                    window.location.href = '/';
                }
                console.log(getCookie('key'));
            } else {
                clearFields();
                $('.account .invalid').html(res.detail);
                document.querySelector(".account .invalid").style.display = 'block'
            }
        }).catch(function (res) {
            console.log(res);
            let error = JSON.parse(res.responseText);
            let errKey = Object.keys(error);
            let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`)
            $('.account .invalid').html(html).show();
            clearFields();
        });

    } else {
        $('.account .invalid').html('Поле e-mail или пароль пустое');
        document.querySelector(".account .invalid").style.display = 'block';
        clearFields();
    }
}

function authUserFunc(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.login(),
            data: config,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function (req) {
                $('.account .invalid').html('Неверно введён e-mail или пароль').show();
                clearFields();
            }
        };

        ajaxRequest(data, status, reject)
    });
}

function clearFields() {
    document.getElementById('psw').value = '';
}

function checkEmptyFields(username, password) {
    let empty = false;
    if (username.length == 0) {
        empty = true;
    }

    if (password.length == 0) {
        empty = true;
    }
    return empty;
}

function logIn() {
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

    $('.close').on('click', function () {
        hidePopup();
    });
});