'use strict';
import URLS from '../Urls/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import {showAlert} from "../ShowNotifications/index";
import {hidePopup} from "../Popup/popup";

export function addHomeGroup(e, el, callback) {
    e.preventDefault();
    let data = getAddHomeGroupData();
    let json = JSON.stringify(data);

    addHomeGroupToDataBase(json).then(function (data) {
        clearAddHomeGroupData();
        hidePopup(el);
        callback();
        showAlert(`Домашняя группа ${data.get_title} добавлена в базу данных`);
    }).catch(function (data) {
        hidePopup(el);
        showAlert('Ошибка при создании домашней группы');
    });
}

export function clearAddHomeGroupData() {
    $('#added_home_group_date').val('');
    $('#added_home_group_title').val('');
    $('#added_home_group_city').val('');
    $('#added_home_group_address').val('');
    $('#added_home_group_phone').val('');
    $('#added_home_group_site').val('');
}

function addHomeGroupToDataBase(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.home_group.list(),
            data: config,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };
        let status = {
            201: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }
        };
        newAjaxRequest(data, status, reject)
    });
}