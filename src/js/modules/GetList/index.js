'use strict';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';

export function getResponsible(ids, level, search = "") {
    let responsibleLevel;
    if (level === 0 || level === 1) {
        responsibleLevel = level + 1;
    } else {
        responsibleLevel = level;
    }
    return new Promise(function (resolve, reject) {
        let url = `${URLS.user.short()}?level_gte=${responsibleLevel}&search=${search}`;
        if (ids instanceof Array) {
            ids.forEach(function (id) {
                url += '&department=' + id;
            });
        } else {
            (ids !== null) && (url += '&department=' + ids);
        }
        ajaxRequest(url, null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}