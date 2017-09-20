"use strict";
import URLS from '../Urls/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';

export function getChurchStats(id) {
    let resData = {
        url: `${URLS.event.church_report.dashboard_count()}?user_id=${id}`
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}

export function getHomeGroupStats(id) {
    let resData = {
        url: `${URLS.event.home_meeting.dashboard_count()}?user_id=${id}`
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}

export function getChurchData(id) {
    let resData = {
        url: `${URLS.church.dashboard_count()}?user_id=${id}`
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}

export function getUsersData(id) {
    let resData = {
        url: `${URLS.user.dashboard_count()}?user_id=${id}`
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}
