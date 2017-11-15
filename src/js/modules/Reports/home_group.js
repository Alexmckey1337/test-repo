'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import {deleteData} from "../Ajax/index";
import newAjaxRequest from  '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {showAlert, showConfirm} from "../ShowNotifications/index";
import updateHistoryUrl from '../History/index';

export function HomeReportsTable(config) {
    getHomeReports(config).then(data => {
        makeHomeReportsTable(data);
    });
}

export function homeReportsTable(config = {}) {
    let status = $('#statusTabs').find('.current').find('button').data('status');
    config.status = status;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    updateHistoryUrl(config);
    getHomeReports(config).then(data => {
        makeHomeReportsTable(data, config);
    })
}

function getHomeReports(config = {}) {
    if (!config.status) {
        let status = parseInt($('#statusTabs').find('.current').find('button').data('status'));
        config.status = status || 1;
    }
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.list(),
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

function makeHomeReportsTable(data, config = {}) {
    let tmpl = $('#databaseHomeReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: homeReportsTable
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    fixedTableHead();
    $('.table__count').text(text);
    new OrderTable().sort(homeReportsTable, ".table-wrap th");
    $('.preloader').css('display', 'none');
        $("button.delete_btn").on('click', function () {
        let id = $(this).attr('data-id');
        showConfirm('Удаление', 'Вы действительно хотите удалить данный отчет?', function () {
            deleteData(URLS.event.home_meeting.detail(id)).then(() => {
                showAlert('Отчет успешно удален!');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                homeReportsTable({page: page});
            }).catch((error) => {
                let errKey = Object.keys(error),
                    html = errKey.map(errkey => `${error[errkey]}`);
                showAlert(html[0], 'Ошибка');
            });
        }, () => {
        });
    });
}

export function makeHomeReportDetailTable(data) {
    let tmpl = $('#databaseHomeReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeReports').html(rendered);
    fixedTableHead();
}

export function getHomeReportDetailData(config = {}) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.detail(REPORTS_ID),
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

export function getHomeReportDetailTableData(config = {}) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.visitors(REPORTS_ID),
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

export function makeCaption(data) {
    let container = document.createElement('div');
    let title = document.createElement('h2');
    let dist = {
        night: "О Марафоне",
        home: "Домашней группы",
        service: "О Воскресном Служении"
    };
    if (data.status === 1) {
        $(title).text(`Подача отчета ${dist[data.type.code]}`);
    }
    if (data.status === 2) {
        $(title).text(`Отчет ${dist[data.type.code]}`);
    }
    if (data.status === 3) {
        $(title).html(`Отчет ${dist[data.type.code]} <span>(просрочен)</span>`);
    }
    $(container).append(title);
    let ownerContainer = document.createElement('p');
    let ownerTitle = document.createElement('span');
    let ownerData = document.createElement('a');
    $(ownerTitle).text('Лидер: ');
    $(ownerData).text(data.owner.fullname).attr('href', `/account/${data.owner.id}`);
    $(ownerContainer).append(ownerTitle).append(ownerData);
    $(container).append(ownerContainer);

    let groupContainer = document.createElement('p');
    let groupTitle = document.createElement('span');
    let groupData = document.createElement('a');
    $(groupTitle).text('Домашняя группа: ');
    $(groupData).text(data.home_group.title).attr('href', `/home_groups/${data.home_group.id}`);
    $(groupContainer).append(groupTitle).append(groupData);
    $(container).append(groupContainer);

    let dateContainer = document.createElement('p');
    let dateTitle = document.createElement('label');
    let dateData = document.createElement('input');
    $(dateTitle).text('Дата отчёта: ');
    let dateReportsFormatted = new Date(data.date.split('.').reverse().join(','));
    let thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(1).format();
    let nextSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
    $(dateData).val(data.date).attr({
        'size': data.date.length,
        'data-name': 'date',
    }).datepicker({
        autoClose: true,
        minDate: new Date(thisMonday),
        maxDate: new Date(nextSunday),
    });
    $(dateContainer).append(dateTitle).append(dateData);
    $(container).append(dateContainer);
    if (data.type.code != 'service') {
        let amountContainer = document.createElement('p');
        let amountTitle = document.createElement('label');
        let amountData = document.createElement('input');
        $(amountTitle).text('Сумма пожертвований: ');
        $(amountData).val(data.total_sum).attr({
            'size': 7,
            'data-name': 'total_sum',
        });
        $(amountContainer).append(amountTitle).append(amountData);
        $(container).append(amountContainer);
    }
    return container;
}

export function sendForms(btn, data) {
    let $homeReports = $('#homeReports');
    if (btn.attr('data-update') == 'true') {
        updateReports(JSON.stringify(data)).then((res) => {
            btn.attr({
                'data-click': false,
                'data-update': false,
            });
            btn.text('Редактировать');
            $homeReports.find('input').each(function () {
                $(this).attr('disabled', true);
            });
        });
    } else {
        submitReports(JSON.stringify(data)).then((data) => {
            btn.text('Редактировать').attr({
                'data-click': false,
                'data-update': false,
            });
            $homeReports.find('input').each(function () {
                $(this).attr('disabled', true);
            });
        }).catch((err) => {
            let error = JSON.parse(err.responseText),
                errKey = Object.keys(error);
            let html = errKey.map(errkey => `${error[errkey]}`);
            showAlert(html[0]);
        });
    }
}

function submitReports(config) {
    return new Promise((resolve, reject) => {
        let pathnameArr = window.location.pathname.split('/');
        const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];
        let data = {
            method: 'POST',
            url: URLS.event.home_meeting.submit(REPORTS_ID),
            data: config,
            contentType: 'application/json',
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

function updateReports(config) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise((resolve, reject) => {
        let data = {
            method: 'PUT',
            url: URLS.event.home_meeting.detail(REPORTS_ID),
            data: config,
            contentType: 'application/json',
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function (err) {
                reject(err)
            },
            400: function (err) {
                reject(err)
            }
        };
        newAjaxRequest(data, status, reject)
    })
}