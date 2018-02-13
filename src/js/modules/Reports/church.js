'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import getData, {postData, deleteData} from '../Ajax/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index"
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {btnDeals} from "../Deals/index";
import {showChurchPayments} from '../Payment/index';
import {showAlert, showConfirm} from "../ShowNotifications/index";
import updateHistoryUrl from '../History/index';
import reverseDate from '../Date';
import dataHandling from '../Error';
import {getOrderingData} from "../Ordering/index";
import {convertNum} from "../ConvertNum/index";

export function ChurchReportsTable(config = {}, pagination = true) {
    Object.assign(config, getTabsFilterParam(), getTypeTabsFilterParam(), getOrderingData());
    getData(URLS.event.church_report.list(), config).then(data => {
        makeChurchReportsTable(data, config, pagination);
    }).catch(err => dataHandling(err));
}

export function churchReportsTable(config = {}, pagination = true) {
    Object.assign(config, getSearch('search_title'), getFilterParam(), getTabsFilterParam(), getTypeTabsFilterParam(), getOrderingData());
    (pagination) && updateHistoryUrl(config);
    getData(URLS.event.church_report.list(), config).then(data => {
        makeChurchReportsTable(data, config, pagination);
    }).catch(err => dataHandling(err));
}

function getTypeTabsFilterParam() {
    let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');

    return {is_submitted};
}

function makeChurchReportsTable(data, config = {}, pagination = true) {
    let tmpl = $('#databaseChurchReports').html();
    _.map(data.results, item => {
        let date = new Date(reverseDate(item.date, '-')),
            weekNumber = moment(date).isoWeek(),
            startDate = moment(date).startOf('isoWeek').format('DD.MM.YY'),
            endDate = moment(date).endOf('isoWeek').format('DD.MM.YY');
        item.date = `${weekNumber} нед. (${startDate} - ${endDate})`;
    });
    let rendered = _.template(tmpl)(data);
    $('#churchReports').html(rendered);
    let count = data.count,
        pages = Math.ceil(count / CONFIG.pagination_count),
        page = config.page || 1,
        showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
        text = `Показано ${showCount} из ${count}`,
        paginationConfig = {
            container: ".reports__pagination",
            currentPage: page,
            pages: pages,
            callback: churchReportsTable
        };
    if (pagination) {
        makePagination(paginationConfig);
        makeSortForm(data.table_columns);
        $('.table__count').text(text);
        fixedTableHead();
        new OrderTable().sort(churchReportsTable, ".table-wrap th");
    }
    $('.preloader').hide();
    btnDeals();
    btnControls(pagination, config);
    btnEditReport();
}

function btnControls(pagination, config = {}) {
    $("button.complete").on('click', function () {
        let id = $(this).attr('data-id'),
            data = {"done": true};
        postData(URLS.event.church_report.detail(id), data, {method: 'PATCH'}).then( _ => {
            (pagination) ? churchReportsTable() : churchReportsTable(config, pagination);
        }).catch(err => dataHandling(err));
    });

    $('.show_payments').on('click', function () {
        let id = $(this).data('id');
        showChurchPayments(id);
    });
}

function btnEditReport() {
    $("#churchReports").find('.edit').on('click', function () {
        let id = $(this).attr('data-id');
        getData(URLS.event.church_report.detail(id)).then(data => {
            let dateReportsFormatted = new Date(reverseDate(data.date, ',')),
                thisMonday = (moment(dateReportsFormatted).day() === 1) ?
                    moment(dateReportsFormatted).format()
                    :
                    (moment(dateReportsFormatted).day() === 0) ?
                        moment(dateReportsFormatted).subtract(6, 'days').format()
                        :
                        moment(dateReportsFormatted).day(1).format(),
                thisSunday = (moment(dateReportsFormatted).day() === 0) ?
                    moment(dateReportsFormatted).format()
                    :
                    moment(dateReportsFormatted).day(7).format();
            $('#reportDate').datepicker({
                autoClose: true,
                minDate: new Date(thisMonday),
                maxDate: new Date(thisSunday),
            });
            $('#chReportForm').get(0).reset();
            completeFields(data);
            $('#editReport, .bg').addClass('active');
        }).catch(err => dataHandling(err));
    });
}

export function calcTransPayments() {
    $('#reportTithe, #reportDonations').on('input', function () {
        let tithe = convertNum($('#reportTithe').val(), '.') || 0,
            donat = convertNum($('#reportDonations').val(), '.') || 0,
            calc = (tithe + donat) * 0.15;
        $('#reportTransferPayments').val(convertNum(calc.toFixed(2), ','));
    });
}

export function deleteReport(callback, config = {}, pagination = true) {
    let msg = 'Вы действительно хотите удалить данный отчет',
        id = $('#delete_report').attr('data-id');
    showConfirm('Удаление', msg, function () {
        deleteData(URLS.event.church_report.detail(id)).then(function () {
            $('.preloader').css('display', 'block');
            callback(config, pagination);
            showAlert('Отчет удален');
            $('#editReport, .bg').removeClass('active');
        }).catch(err => dataHandling(err));
    });
}

function completeFields (data) {
    let total_tithe = convertNum(data.total_tithe, ','),
        total_donations = convertNum(data.total_donations, ','),
        transfer_payments = convertNum(data.transfer_payments, ','),
        total_pastor_tithe = convertNum(data.total_pastor_tithe, ',');
    $('#delete_report').attr('data-id', data.id);
    $('#send_report').attr({
        'data-id': data.id,
        'data-status': data.status
    });
    $('#reportChurch').text(data.church.title).attr('data-id', data.church.id);
    $("#reportPastor").text(data.pastor.fullname).attr('data-id', data.pastor.id);
    $('#reportDate').val((data.status === 2) ? data.date : '');
    $('#reportCountPeople').val((data.status === 2) ? data.total_peoples : '');
    $('#reportCountNewPeople').val((data.status === 2) ? data.total_new_peoples : '');
    $('#reportCountRepentance').val((data.status === 2) ? data.total_repentance : '');
    $('#reportTithe').val((data.status === 2) ? total_tithe : '');
    $('#reportDonations').val((data.status === 2) ? total_donations : '');
    $('#reportTransferPayments').val(transfer_payments);
    $('#reportPastorTithe').val((data.status === 2) ? total_pastor_tithe : '');
    $('#reportComment').val(data.comment);
    $('.cur_name').text(`(${data.currency.short_name})`);
    $('#report_title').text((data.status === 2) ? 'Редактирование' : 'Подача');
    $('#send_report').text((data.status === 2) ? 'Сохранить' : 'Подать');
    if (!data.can_submit) {
        showAlert(data.cant_submit_cause);
        $('#send_report').attr({disabled: true});
    } else {
        $('#send_report').attr({disabled: false});
    }
}

function reportData() {
    let data = {},
        $input = $('#editReport').find('input, textarea');
    $input.each(function () {
        let field = $(this).attr('name');
        if (field) {
            if (field === 'date') {
                data[field] = reverseDate($(this).val(), '-');
            } else if (field === 'comment') {
                data[field] = $(this).val();
            } else {
                data[field] = convertNum($(this).val(), '.');
            }
        }
    });
    return data;
}

export function sendReport(pagination = true, option = {}) {
    const ID = $('#send_report').attr('data-id'),
        status = $('#send_report').attr('data-status'),
        URL = (status === '2') ?
            URLS.event.church_report.detail(ID)
            :
            URLS.event.church_report.submit(ID),
        MSG = (status === '2') ?
            'Изменения в отчете поданы'
            :
            'Отчет успешно подан';
    let data = reportData(),
        config = {},
        page = $('.pagination__input').val();
    (status === '2') && (config.method = 'PUT');
    postData(URL, data, config).then(function () {
        let conf = {page};
        (!pagination) && (Object.assign(conf, option));
        churchReportsTable(conf, pagination);
        showAlert(MSG);
        $('#editReport, .bg').removeClass('active');
    }).catch(err => dataHandling(err));
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
    $(dateTitle).text('Дата служения: ');
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