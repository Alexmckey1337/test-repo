'use strict';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';

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

export function getChurchesListINDepartament(department_ids) {
    return new Promise(function (resolve, reject) {
        let url;
        if (department_ids instanceof Array) {
            url = `${URLS.church.for_select()}?`;
            let i = 0;
            department_ids.forEach(function (department_id) {
                i++;
                url += `department=${department_id}`;
                if (department_ids.length != i) {
                    url += '&';
                }
            })
        } else {
            url = (department_ids != null) ? `${URLS.church.for_select()}?department=${department_ids}` : `${URLS.church.for_select()}`;
        }
        let data = {
            url: url,
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }

        };
        newAjaxRequest(data, status, reject)
    })
}

export function getHomeGroupsINChurches(id) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${URLS.home_group.for_select()}?church_id=${id}`,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }

        };
        newAjaxRequest(data, status, reject)
    });
}

export function getCountries() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.country(), null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

export function getRegions(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.region(), config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    })
}

export function getCities(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.city(), config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    })
}