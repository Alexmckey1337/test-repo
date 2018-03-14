'use strict';
import {showAlert} from '../ShowNotifications/index';

export default function (data) {
    let msg = "";
    if (data instanceof Error) {
        msg = data.message;
    } else if (typeof data === "string") {
        msg += data;
    } else {
        let errObj = null;
        (typeof data != 'object') ? errObj = JSON.parse(data) : errObj = data;
        for (let key in errObj) {
            msg += key;
            msg += ': ';
            if (errObj[key] instanceof Array) {
                errObj[key].forEach(function (item) {
                    msg += item;
                    msg += ' ';
                });
            } else if (typeof errObj[key] === 'object') {
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