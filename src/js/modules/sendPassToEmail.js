'use strict';
import ajaxRequest from './Ajax/ajaxRequest';
import URLS from './Urls/index';
import {showAlert} from './ShowNotifications/index';

export default function sendPassToEmail() {
    let data = {
        'email': document.getElementById('send_letter').value
    },
        json = JSON.stringify(data);
    ajaxRequest(URLS.password_forgot(), json, function (data) {
        showAlert(data.detail);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);

        },
        500: function () {
            $('.account .invalid').html('Проверьте введённый e-mail').show();
            $('#send_letter').val('');
        }
    });
}