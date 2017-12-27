'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
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
import {showAlert, showConfirm} from "../ShowNotifications/index";
import updateHistoryUrl from '../History/index';
import reverseDate from '../Date';

export function ChurchReportsTable(config) {
    Object.assign(config, getTabsFilterParam());
    getChurchReports(config).then(data => {
        makeChurchReportsTable(data);
    });
}

function getChurchReports(config = {}) {
    if (!config.is_submitted) {
        let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');
        config.is_submitted = is_submitted || 'false';
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
    _.map(data.results, item => {
        let date = new Date(reverseDate(item.date, '-')),
            weekNumber = moment(date).week(),
            startDate = moment(date).startOf('isoWeek').format('DD.MM.YY'),
            endDate = moment(date).endOf('isoWeek').format('DD.MM.YY');
        item.date = `${weekNumber} нед. (${startDate} - ${endDate})`;
    });
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
    $("button.delete_btn").on('click', function () {
        let id = $(this).attr('data-id');
        showConfirm('Удаление', 'Вы действительно хотите удалить данный отчет?', function () {
            deleteChurchPayment(id).then(() => {
                showAlert('Отчет успешно удален!');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                churchReportsTable({page: page});
            }).catch((error) => {
                let errKey = Object.keys(error),
                    html = errKey.map(errkey => `${error[errkey]}`);
                showAlert(html[0], 'Ошибка');
            });
        }, () => {
        });
    });
}

export function churchReportsTable(config = {}) {
    let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');
    config.is_submitted = is_submitted;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    updateHistoryUrl(config);
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

export function getChurchReportDetailData(config = {}) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.church_report.detail(REPORTS_ID),
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

    let pastorContainer = document.createElement('p');
    let pastorTitle = document.createElement('span');
    let pastorData = document.createElement('a');
    $(pastorTitle).text('Пастор: ');
    $(pastorData).text(data.pastor.fullname).attr('href', `/account/${data.pastor.id}`);
    $(pastorContainer).append(pastorTitle).append(pastorData);
    $(container).append(pastorContainer);

    let churchContainer = document.createElement('p');
    let churchTitle = document.createElement('span');
    let churchData = document.createElement('a');
    $(churchTitle).text('Церковь: ');
    $(churchData).text(data.church.title).attr('href', `/churches/${data.church.id}`);
    $(churchContainer).append(churchTitle).append(churchData);
    $(container).append(churchContainer);

    let dateContainer = document.createElement('p');
    let dateTitle = document.createElement('label');
    let dateData = document.createElement('input');
    $(dateTitle).text('Дата отчёта: ');
    let dateReportsFormatted = new Date(data.date.split('.').reverse().join(',')),
        thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).subtract(6, 'days').format() : moment(dateReportsFormatted).day(1).format(),
        thisSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
    $(dateData).val(data.date).attr({
        'size': data.date.length,
        'name': 'date',
        'data-validation': 'required'
    }).datepicker({
        autoClose: true,
        minDate: new Date(thisMonday),
        maxDate: new Date(thisSunday),
    });
    $(dateContainer).append(dateTitle).append(dateData);
    $(container).append(dateContainer);

    return container;
}

export function makeReportData(data) {
    let container = document.createElement('div');
    $(container).attr({
        'class': 'report-block'
    });
    let txt = `
             <div class="column col-6">
                    <h3>Отчет по людям</h3>
                    <ul class="info">
                        <li>
                            <div class="label-wrapp">
                                <label for="total_peoples">Количество людей на собрании</label>
                            </div>
                            <div class="input">
                                <input id="total_peoples" type="text" name="total_peoples" 
                                data-validation="number required"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_peoples}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_new_peoples">Количество новых людей</label>
                            </div>
                            <div class="input">
                                <input id="total_new_peoples" type="text" name="total_new_peoples"
                                data-validation="number required"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_new_peoples}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_repentance">Количество покаяний</label>
                            </div>
                            <div class="input">
                                <input id="total_repentance" type="text" name="total_repentance"
                                data-validation="number required"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_repentance}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="comment">Комментарий</label>
                            </div>
                            <div class="input">
                                <textarea name="comment" id="comment">${data.comment}</textarea>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="column col-6">
                    <h3>Отчет по финансам</h3>
                    <ul class="info">
                        <li>
                            <div class="label-wrapp">
                                <label for="total_tithe">Десятины (${data.currency.short_name})</label>
                            </div>
                            <div class="input">
                                <input id="total_tithe" type="text" name="total_tithe"
                                 data-validation="number required" data-validation-allowing="float"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_tithe}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_donations">Пожертвования (${data.currency.short_name})</label>
                            </div>
                            <div class="input">
                                <input id="total_donations" type="text" name="total_donations"
                                data-validation="number required" data-validation-allowing="float"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_donations}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="currency_donations">Пожертвования в другой валюте</label>
                            </div>
                            <div class="input">
                                <textarea name="currency_donations" id="currency_donations">${data.currency_donations}</textarea>
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="transfer_payments">15% к перечислению (${data.currency.short_name})</label>
                            </div>
                            <div class="input">
                                <input name="transfer_payments" id="transfer_payments"
                                 value="${(data.status == 1 || data.status == 3) ? '' : data.transfer_payments}" readonly>
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_pastor_tithe">Десятина пастора (${data.currency.short_name})</label>
                            </div>
                            <div class="input">
                                <input name="total_pastor_tithe" id="total_pastor_tithe"
                                data-validation="number required" data-validation-allowing="float"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_pastor_tithe}">
                            </div>
                        </li>
                    </ul>
                </div>`;
    $(container).append(txt);
    return container;
}

export function sendForms(btn, data) {
    let $input = $('#databaseChurchReportsForm').find('input:not(:hidden), textarea');
    if (btn.attr('data-update') == 'true') {
        updateReports(JSON.stringify(data)).then((res) => {
            btn.attr({
                'data-click': false,
                'data-update': false,
            });
            btn.text('Редактировать');
            $input.each(function () {
                $(this).attr('disabled', true);
            });
            showAlert('Изменения в отчете поданы');
        }).catch((res) => {
            let error = JSON.parse(res.responseText);
            let errKey = Object.keys(error);
            let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
            showAlert(html);
        });
    } else {
        submitReports(JSON.stringify(data)).then((data) => {
            btn.text('Редактировать').attr({
                'data-click': false,
                'data-update': false,
            });
            $input.each(function () {
                $(this).attr('disabled', true);
            });
            showAlert('Отчет успешно подан');
        }).catch((res) => {
            let error = JSON.parse(res.responseText);
            let errKey = Object.keys(error);
            let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
            showAlert(html);
        });
    }
}

function updateReports(config) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise((resolve, reject) => {
        let data = {
            method: 'PUT',
            url: URLS.event.church_report.detail(REPORTS_ID),
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

function submitReports(config) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise((resolve, reject) => {
        let data = {
            method: 'POST',
            url: URLS.event.church_report.submit(REPORTS_ID),
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

function deleteChurchPayment(id) {
    let url = URLS.event.church_report.detail(id),
        defaultOption = {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
    if (typeof url === "string") {
        return fetch(url, defaultOption).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp;
            } else {
                let json = resp.json();
                return json.then(err => {
                    throw err;
                });
            }
        });
    }
}