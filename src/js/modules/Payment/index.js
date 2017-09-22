'use strict';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import {showAlert} from "../ShowNotifications/index";
import {churchReportsTable} from '../Reports/church';

export function createPayment(data, id) {
    let resData = {
        method: 'POST',
        url: URLS.partner.create_payment(id)
    };
    Object.assign(resData, data);
    return new Promise(function (resolve, reject) {
        let codes = {
            201: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}

export function completeChurchPayment(id) {
    return new Promise(function () {
        let data = {
            "done": true,
        };
        let config = JSON.stringify(data);
        ajaxRequest(URLS.event.church_report.detail(id), config, function () {
            churchReportsTable();
            document.getElementById('popup').style.display = '';
        }, 'PATCH', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showAlert(data.detail);
            }
        });
    })
}

export function showChurchPayments(id) {
    getChurchPayment(id).then(function (data) {
        let payments_table = '';
        let sum, date_time, manager;
        data.forEach(function (payment) {
            sum = payment.sum_str;
            date_time = payment.sent_date;
            manager = `${payment.manager.last_name} ${payment.manager.first_name} ${payment.manager.middle_name}`;
            payments_table += `<tr><td>${sum}</td><td>${date_time}</td><td>${manager}</td></tr>`
        });
        $('#popup-payments table').html(payments_table);
        $('#popup-payments').css('display', 'block');
    })
}

export function getChurchPayment(id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.event.church_report.payments(id), null, function (data) {
            resolve(data);
        }, 'GET', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                reject();
                showAlert(data.detail)
            }
        })
    })
}