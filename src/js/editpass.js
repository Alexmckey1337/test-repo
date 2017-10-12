'use strict';
import URLS from './modules/Urls/index';
import {showAlert} from "./modules/ShowNotifications/index";
import ajaxRequest from './modules/Ajax/ajaxRequest';
import getLastId from './modules/GetLastId/index';

function changePass() {
    let hash = getLastId();
    if (!hash) {
        showAlert('неверный ключ активации');
    }
    let data = {
        "password1": document.getElementsByTagName('input')[0].value,
        "password2": document.getElementsByTagName('input')[1].value,
        "activation_key": hash
    };
    let json = JSON.stringify(data);
    ajaxRequest(URLS.password_view(), json, function (data) {
        showAlert(data.detail);
        setTimeout(function () {
            window.location.href = '/entry/';
        }, 1500);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);

        }
    });
}

$("document").ready(function () {
    document.getElementById('create').addEventListener('click', function () {
        changePass();
    })
});
