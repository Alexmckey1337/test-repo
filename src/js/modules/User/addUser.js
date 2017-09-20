'use strict';
import URLS from '../Urls/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';

export function addUserToHomeGroup(user_id, hg_id, exist = false) {
    let url = URLS.user.set_home_group(user_id);
    let config = {
        url: url,
        method: "POST",
        data: {
            home_group_id: hg_id
        }
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}

export function addUserToChurch(user_id, id, exist = false) {
    let url = URLS.user.set_church(user_id);
    let config = {
        url: url,
        method: "POST",
        data: {
            church_id: id
        }
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}