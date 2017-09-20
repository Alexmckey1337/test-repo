'use strict';
import URLS from '../Urls/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';

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