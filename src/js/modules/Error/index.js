'use strict';
import {showAlert} from '../ShowNotifications/index';

export default function (data) {
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
}