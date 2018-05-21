'use strict';
import {CONFIG} from "../config";
import URLS from '../Urls/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getFilterParam} from '../Filter/index';
import OrderTable, {getOrderingData} from '../Ordering/index';
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import {makeDataTable} from '../Table/index';
import updateHistoryUrl from '../History/index';

export function createUsersTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    updateHistoryUrl(config);
    getUsers(config).then(function (data) {
        let count = data.count;
        let page = config['page'] || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
        let id = "database_users";
        let text = `Показано ${showCount} из ${count}`;
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createUsersTable
        };
        makeDataTable(data, id);
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createUsersTable, ".table-wrap th");
    }).catch(function (err) {
        console.log(err);
    });
}

function getUsers(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.user.table(),
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
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