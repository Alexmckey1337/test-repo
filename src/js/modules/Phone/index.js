/**
 * Created by volodimir on 12/13/17.
 */
/**
 * Created by volodimir on 11/2/17.
 */
'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'whatwg-fetch';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import {getFilterParam} from "../Filter/index";
import getData, {postData, getDataPhone} from '../Ajax/index';
import getSearch from '../Search/index';
import OrderTable from '../Ordering/index';
import makePagination from '../Pagination/index';
import {makeIptelTable} from '../Account/index';
import updateHistoryUrl from '../History/index';
import makeSelect from '../MakeAjaxSelect/index';

function parseFunc(data, params) {
    params.page = params.page || 1;
    const results = [];
    console.log(data)
    data.results.forEach(function makeResults(element) {
        results.push({
            id: element.id,
            name: element.title,
        });
    });
    return {
        results: results,
        pagination: {
            more: (params.page * 100) < data.count
        }
    };
}
function formatRepo(data) {
    if (data.id === '') {
        return 'ВСЕ';
    } else {
        return `<option value="${data.id}">${data.name}</option>`;
    }
}

export function PhoneTable(config) {
    getDataPhone(URLS.phone.list(), config).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText');
            $('#tablePhone').append(err);
        } else {
            makePhoneTable(data);
        }
    });

}

function makePhoneTable(data, config = {}) {
    let count = data.pages,
        page = config['page'] || 1,
        pages = Math.ceil(count / CONFIG.pagination_count),
        showCount = (count < CONFIG.pagination_count) ? count : data.result.length,
        text = `Показано ${showCount} из ${count}`,
        paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: makePhoneTable
        };
    makePagination(paginationConfig);
    $('.table__count').text(text);
    $('#tablePhoneWrap').html('');
    makeIptelTable(data, '#tablePhoneWrap');
    new OrderTable().sort(phoneTable, ".table-wrap th");
    $('.preloader').hide();
}

export function phoneTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getDataPhone(URLS.phone.list(), config).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText');
            $('#tablePhone').append(err);
        } else {
            makePhoneTable(data, config);
        }
    });
}

function addUserToPhone(data, block) {
    let wrap = `${data.map(item => {
        return `<form class="form-addUser">
                    <p class="form-addUser__phone">${item.extension}</p>
                    <label>
                        <input class="${(item.fullname != null) ? 'inputPh active' : 'inputPh'}" type="text" value="${(item.fullname != null) ? item.fullname : ''}" disabled>
                        <select name="user" class="${(item.fullname != null) ? 'selectPh' : 'selectPh active'}"></select>
                    </label>
                    <button class="${(item.fullname != null) ? 'add' : 'add active'}" type="submit" disabled></button>
                    <button class="${(item.fullname != null) ? 'change active' : 'change'}" type="button"></button>
                    <button class="close" type="button"></button>
                    <span class="saved">Сохранено</span>
                </form>`;
    }).join('')}`;
    $(block).append(wrap);
    $('.selectPh').on('change', function () {
        $(this).parent().parent().find('.add').removeAttr('disabled');
    });
    $('.change').on('click', function () {
        $(this).removeClass('active');
        $(this).parent().children('.add').addClass('active');
        $(this).parent().children('.close').addClass('active');
        $(this).parent().find('.inputPh').removeClass('active');
        $(this).parent().find('.selectPh').addClass('active');
        makeSelect($('.selectPh.active'), '/api/v1.1/users/for_select/', parseFunc, formatRepo);
    });
    $('.close').on('click', function () {
        $(this).removeClass('active');
        $(this).parent().children('.change').addClass('active');
        $(this).parent().find('.inputPh').addClass('active');
        $(this).parent().children('.add').removeClass('active');
        $(this).parent().find('.selectPh').removeClass('active').select2('destroy');
    });
    $('.form-addUser').on('submit', function (e) {
        e.preventDefault();
        let phone = $(this).find('.form-addUser__phone').text(),
            userId = $(this).find('.selectPh').val(),
            data = {
                "user_id": userId,
                "extension": phone
            }
        postData(URLS.phone.changeUser(), data).then(() => {
            let userName = $(this).find('span option[value=' + userId + ']').text();
            console.log(userName);
            $(this).find('.add').removeClass('active');
            $(this).find('.close').removeClass('active');
            $(this).find('.change').addClass('active');
            $(this).find('.inputPh').addClass('active').val(userName);
            $(this).find('.selectPh').removeClass('active').select2('destroy');
            $(this).find('.saved').addClass('active');
            setTimeout(function () {
                $(this).find('.saved').removeClass('active');
            }, 1000);
        });
    })
    makeSelect($('.selectPh.active'), '/api/v1.1/users/for_select/', parseFunc, formatRepo);
}

export function getDataUserPhone() {
    $('#tableAddUserToPhone').html('');
    getDataPhone(URLS.phone.user()).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText');
            $('#popupAddUserToPhone').find('.main-text').append(err);
        } else {
            addUserToPhone(data, '#tableAddUserToPhone');
        }
    });
}





