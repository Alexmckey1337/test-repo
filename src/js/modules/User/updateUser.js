'use strict';
import URLS from '../Urls/index';
import ajaxSendFormData from '../Ajax/ajaxSendFormData';
import {showAlert} from '../ShowNotifications/index';

export function updateUser(id, data, success = null) {
    let url = URLS.user.detail(id);
    let config = {
        url: url,
        data: data,
        method: 'PATCH'
    };
    return ajaxSendFormData(config).then(function (data) {
        if (success) {
            $(success).text('Сохранено');
            setTimeout(function () {
                $(success).text('');
            }, 3000);
        }
        return data;
    }).catch(function (data) {
        let msg = "";
        if (typeof data == "string") {
            msg += data;
        } else {
            let errObj = null;
            if (typeof data != 'object') {
                errObj = JSON.parse(data);
            } else {
                errObj = data;
            }
            for (let key in errObj) {
                msg += key;
                msg += ': ';
                if (errObj[key] instanceof Array) {
                    errObj[key].forEach(function (item) {
                        msg += item;
                        msg += ' ';
                    });
                } else if (typeof errObj[key] == 'object') {
                    let errKeys = Object.keys(errObj[key]),
                        html = errKeys.map(errkey => `${errObj[key][errkey]}`).join('');
                    msg += html;
                } else {
                    msg += errObj[key];
                }
                msg += '; ';
            }
        }
        showAlert(msg);

        return false;
    });
}

export function updateOrCreatePartner(id, data, success = null) {
    let url = (!id) ? URLS.partner.list() : URLS.partner.detail(id);
    let config = {
        url: url,
        data: data,
        method: (!id) ? 'POST' : 'PATCH'
    };
    return ajaxSendFormData(config).then(function (data) {
        if (success) {
            $(success).text('Сохранено');
            setTimeout(function () {
                $(success).text('');
            }, 3000);
        }
        return data;
    }).catch(function (data) {
        let msg = "";
        if (typeof data == "string") {
            msg += data;
        } else {
            let errObj = null;
            if (typeof data != 'object') {
                errObj = JSON.parse(data);
            } else {
                errObj = data;
            }
            for (let key in errObj) {
                msg += key;
                msg += ': ';
                if (errObj[key] instanceof Array) {
                    errObj[key].forEach(function (item) {
                        msg += item;
                        msg += ' ';
                    });
                } else if (typeof errObj[key] == 'object') {
                    let errKeys = Object.keys(errObj[key]),
                        html = errKeys.map(errkey => `${errObj[key][errkey]}`).join('');
                    msg += html;
                } else {
                    msg += errObj[key];
                }
                msg += '; ';
            }
        }
        showAlert(msg);

        return false;
    });
}