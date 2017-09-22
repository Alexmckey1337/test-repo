'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index"
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {btnDeals} from "../Deals/index";
import {completeChurchPayment, showChurchPayments} from '../Payment/index';

export function ChurchReportsTable(config) {
    Object.assign(config, getTabsFilterParam());
    getChurchReports(config).then(data => {
        makeChurchReportsTable(data);
    });
}

function getChurchReports(config = {}) {
    if (!config.status) {
        let status = parseInt($('#statusTabs').find('.current').find('button').data('status'));
        config.status = status || 1;
    }
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.church_report.list(),
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

function makeChurchReportsTable(data, config = {}) {
    let tmpl = $('#databaseChurchReports').html();
    let rendered = _.template(tmpl)(data);
    $('#churchReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: churchReportsTable
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('.table__count').text(text);
    fixedTableHead();
    new OrderTable().sort(churchReportsTable, ".table-wrap th");
    $('.preloader').hide();
    btnDeals();
    $("button.complete").on('click', function () {
        let id = $(this).attr('data-id');
        completeChurchPayment(id);
    });
    $('.show_payments').on('click', function () {
        let id = $(this).data('id');
        showChurchPayments(id);
    });
}

export function churchReportsTable(config = {}) {
    let status = $('#statusTabs').find('.current').find('button').data('status');
    config.status = status;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    getChurchReports(config).then(data => {
        makeChurchReportsTable(data, config);
    })
}

export function createChurchPayment(id, sum, description) {
    return new Promise(function (resolve, reject) {
        let config = {
            "sum": sum,
            "description": description,
            "rate": $('#new_payment_rate').val(),
            // "currency": $('#new_payment_currency').val(),
            "sent_date": $('#sent_date').val().split('.').reverse().join('-'),
            "operation": $('#operation').val()
        };
        let json = JSON.stringify(config);
        let data = {
            url: URLS.event.church_report.create_uah_payment(id),
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: json
        };
        let status = {
            200: function (req) {
                resolve(req);
            },
            201: function (req) {
                resolve(req);
            },
            403: function () {
                reject('Вы должны авторизоватся');
            },
            400: function (err) {
                reject(err);
            }

        };
        newAjaxRequest(data, status);
    })
}