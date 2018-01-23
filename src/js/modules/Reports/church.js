'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
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
import {completeChurchPayment, showChurchPayments} from '../Payment/index';
import {showAlert, showConfirm} from "../ShowNotifications/index";
import updateHistoryUrl from '../History/index';
import reverseDate from '../Date';

export function ChurchReportsTable(config={},fixTableHead) {
    Object.assign(config, getTabsFilterParam());
    getChurchReports(config).then(data => {
        makeChurchReportsTable(data,{},fixTableHead);
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

function makeChurchReportsTable(data, config = {},fixTableHead = true) {
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
    },
        $input = $('#updateReport').find('input,textarea'),
        $inputTithe = $('#updateReport').find('.report-tithe');
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('.table__count').text(text);
    if(fixTableHead){
        fixedTableHead();
    }
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
    btnDelReport();

    $("#churchReports").find('tr').on('click',function (event) {
        let target = event.target,
            reportId = $(this).find('#reportId').data('id'),
            msg = 'Вы действительно хотите удалить данный отчет',
            url = URLS.event.church_report.detail(reportId);
        $('.save-update').attr('disabled',true);
        if(!$(target).is('a')){
            getData(url).then(function (data) {
                let dateReportsFormatted = new Date(data.date.split('.').reverse().join(',')),
                    eventDay = [dateReportsFormatted.getDate()],
                    eventMonth = [dateReportsFormatted.getMonth()],
                    thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).subtract(6, 'days').format() : moment(dateReportsFormatted).day(1).format(),
                    thisSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
                $('#reportDate').datepicker({
                    autoClose: true,
                    minDate: new Date(thisMonday),
                    maxDate: new Date(thisSunday),
                    onRenderCell: function (date, cellType) {
                        var currentDay = date.getDate(),
                            currentMonth = date.getMonth();
                        if (cellType == 'day' && eventDay.indexOf(currentDay) != -1 && eventMonth.indexOf(currentMonth) != -1) {
                            return {
                                html: '<span class="selectedDate">' + currentDay + '</span>'
                            }
                        }
                    },
                    onSelect: function () {
                        $('.save-update').attr('disabled',false);
                    }
                });
                completeFields(data);
                $('#updateReport,.bg').addClass('active');
            });
            $input.each(function (i, elem) {
                $(elem).on('input', function () {
                    $('.save-update').attr('disabled',false);
                })
            });
            $inputTithe.each(function (i,elem) {
                $(elem).removeClass('error');
                $(elem).on('input', function () {
                    let tithe = parseFloat($('#reportTithe').val()),
                        donat = parseFloat($('#reportDonations').val());
                    if ($('#reportTithe').val() === '' && $('#reportDonations').val() === ''){
                        $('#reportTransferPayments').val('0.0');
                    }else if ($('#reportDonations').val() === ''){
                        $('#reportTransferPayments').val(((tithe+0)*0.15).toFixed(1));
                    }else if ($('#reportTithe').val() === ''){
                        $('#reportTransferPayments').val(((0+donat)*0.15).toFixed(1));
                    }else{
                        $('#reportTransferPayments').val(((tithe+donat)*0.15).toFixed(1));
                    }
                })
            });
            $.validate({
                lang: 'ru',
                form: '#updateReport'
            });
        }
    });
}

function btnDelReport() {
    $("button.delete_btn").on('click', function () {
        let id = $(this).attr('data-id');
        showConfirm('Удаление', 'Вы действительно хотите удалить данный отчет?', function () {
            deleteChurchPayment(id).then(() => {
                showAlert('Отчет успешно удален!');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                churchReportsTable({page: page, church: currentСhurch}, false);
            }).catch((error) => {
                let errKey = Object.keys(error),
                    html = errKey.map(errkey => `${error[errkey]}`);
                showAlert(html[0], 'Ошибка');
            });
        }, () => {
        });
    });
}

export function deleteReport(config = {}, fixedHead = true) {
    let msg = 'Вы действительно хотите удалить данный отчет',
        reportId = parseInt($('#updateReport').find('#id_report').text()),
        url = URLS.event.church_report.detail(reportId);
    showConfirm('Удаление', msg, function () {
        deleteData(url).then(function () {
            churchReportsTable(config,fixedHead);
            showAlert('Отчет удален');
        })
    });
}

function completeFields(data) {
    $('#id_report').text(data.id);
    $('#reportChurch').text(data.church.title);
    $("#reportPastor").text(data.pastor.fullname);
    $('#reportChurch').data('id',data.church.id);
    $("#reportPastor").data('id',data.pastor.id);
    $('#reportDate').val(data.date);
    $('#reportCountPeople').val(data.total_peoples);
    $('#reportCountNewPeople').val(data.total_new_peoples);
    $('#reportCountRepentance').val(data.total_repentance);
    $('#reportTithe').val(data.total_tithe);
    $('#reportDonations').val(data.total_donations);
    $('#reportTransferPayments').val(data.transfer_payments);
    $('#reportPastorTithe').val(data.total_pastor_tithe);
    $('#reportComment').val(data.comment);
    $('#updateReport').attr('data-status',data.status);
}

function savedData() {
    return {
        "id": parseInt($('#id_report').text()),
        "pastor": $('#reportPastor').data('id'),
        "church": $('#reportChurch').data('id'),
        "date": $('#reportDate').val().split('.').reverse().join('-'),
        "total_peoples": $('#reportCountPeople').val(),
        "total_new_peoples": $('#reportCountNewPeople').val(),
        "total_repentance": $('#reportCountRepentance').val(),
        "transfer_payments": $('#reportTransferPayments').val(),
        "total_tithe": $('#reportTithe').val(),
        "total_donations": $('#reportDonations').val(),
        "total_pastor_tithe": $('#reportPastorTithe').val(),
        "comment": $('#reportComment').val(),
    }
}
export function saveReport(config={},fixedHead=true) {
    let reportId = parseInt($('#updateReport').find('#id_report').text()),
        saveUrl = URLS.event.church_report.detail(reportId),
        createUrl = URLS.event.church_report.submit(reportId),
        data = savedData(),
        status = parseInt($('#updateReport').attr('data-status'));
    if(status === 2){
        let config = {
            method: 'PATCH',
        };
        postData(saveUrl, data, config).then(function () {
            churchReportsTable(config,fixedHead);
            showAlert("Отчет изменен");
            $('#updateReport,.bg').removeClass('active');
        });
    }else if (status === 1){
        postData(createUrl, data).then(function () {
            churchReportsTable(config,fixedHead);
            showAlert("Отчет заполнен");
            $('#updateReport,.bg').removeClass('active');
        });
    }
}

export function churchReportsTable(config = {},fixedHead=true) {
    let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');
    config.is_submitted = is_submitted;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    updateHistoryUrl(config);
    getChurchReports(config).then(data => {
        makeChurchReportsTable(data, config,fixedHead);
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