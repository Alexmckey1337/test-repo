'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import makeSortForm from '../Sort/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
// import updateHistoryUrl from '../History/index';

export function getChurchPastorReports(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.church_report.summary(),
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            data: config
        };
        let status = {
            200: function (req) {
                resolve(req);
            },
            403: function () {
                reject('Вы должны авторизоватся');
            }
        };
        newAjaxRequest(data, status);
    })
}

export function makeChurchPastorReportsTable(data, config = {}) {
    let tmpl = $('#databaseChurchPastorReports').html();
    let rendered = _.template(tmpl)(data);
    $('#churchPastorReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: churchPastorReportsTable
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('#churchPastorReports').find('table').on('click', (e) => {
        if (e.target.className != 'url') return;
        let url = e.target.getAttribute('data-url'),
            type = e.target.getAttribute('data-type'),
            id = e.target.getAttribute('data-id');
        window.location = `${url}?type=${type}&pastor=${id}`;
    });
    $('.table__count').text(text);
    fixedTableHead();
    new OrderTable().sort(churchPastorReportsTable, ".table-wrap th");
    $('.preloader').css('display', 'none');
}

export function churchPastorReportsTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    // updateHistoryUrl(config);
    getChurchPastorReports(config).then(data => {
        makeChurchPastorReportsTable(data, config);
    })
}