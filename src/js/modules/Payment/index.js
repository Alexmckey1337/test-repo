'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import getData from '../Ajax/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import {showAlert} from "../ShowNotifications/index";
import {churchReportsTable} from '../Reports/church';
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
import {getOrderingData} from "../Ordering/index";
import beautifyNumber from '../beautifyNumber';
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import OrderTable from '../Ordering/index';
import fixedTableHead from '../FixedHeadTable/index';

export function createPayment(data, id) {
    let resData = {
        method: 'POST',
        url: URLS.partner.create_payment(id)
    };
    Object.assign(resData, data);
    return new Promise(function (resolve, reject) {
        let codes = {
            201: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}

export function completeChurchPayment(id) {
    return new Promise(function () {
        let data = {
            "done": true,
        };
        let config = JSON.stringify(data);
        ajaxRequest(URLS.event.church_report.detail(id), config, function () {
            churchReportsTable();
            document.getElementById('popup').style.display = '';
        }, 'PATCH', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showAlert(data.detail);
            }
        });
    })
}

export function showChurchPayments(id) {
    getChurchPayment(id).then(function (data) {
        let payments_table = '';
        let sum, date_time, manager;
        data.forEach(function (payment) {
            sum = payment.sum_str;
            date_time = payment.sent_date;
            manager = `${payment.manager.last_name} ${payment.manager.first_name} ${payment.manager.middle_name}`;
            payments_table += `<tr><td>${sum}</td><td>${date_time}</td><td>${manager}</td></tr>`
        });
        $('#popup-payments table').html(payments_table);
        $('#popup-payments').css('display', 'block');
    })
}

export function getChurchPayment(id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.event.church_report.payments(id), null, function (data) {
            resolve(data);
        }, 'GET', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                reject();
                showAlert(data.detail)
            }
        })
    })
}

export function createChurchPaymentsTable(config) {
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getChurchPaymentsDeals(config).then(function (data) {
        let count = data.count,
            page = config['page'] || 1,
            pages = Math.ceil(count / CONFIG.pagination_count),
            showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
            id = "tableChurchReportsPayments",
            currency = data.payments_sum,
            uah = (currency.uah.sum != null) ? beautifyNumber(currency.uah.sum) : 0,
            usd = (currency.usd.sum != null) ? beautifyNumber(currency.usd.sum) : 0,
            eur = (currency.eur.sum != null) ? beautifyNumber(currency.eur.sum) : 0,
            rub = (currency.rur.sum != null) ? beautifyNumber(currency.rur.sum) : 0,
            text = `Показано ${showCount} из ${count} на сумму: ${uah} грн, ${usd} дол, ${eur} евро, ${rub} руб`;
        let paginationConfig = {
            container: ".payments__pagination",
            currentPage: page,
            pages: pages,
            callback: createChurchPaymentsTable
        };
        makePaymentsTable(data, id);
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createChurchPaymentsTable, ".table-wrap th");
    }).catch(function (err) {
        console.log(err);
    });
}

function getChurchPaymentsDeals(config) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.church_report.deals(),
            method: 'GET',
            data: config,
            headers: {
                'Content-Type': 'application/json'
            },
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

function makePaymentsTable(data, id) {
    let tmpl = document.getElementById('databasePayments').innerHTML;
    let rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        makeQuickEditPayments(this);
    });
    fixedTableHead();
}

function makeQuickEditPayments(el) {
    let id = $(el).attr('data-id'),
        payer = $(el).attr('data-name');
    getPaymentDetail(id).then(data => {
        console.log(data);
        createUpdatePayment(data, payer, id);
        $('#popup-update_payment').css('display', 'block');
    });
}

function getPaymentDetail(id) {
    let url = URLS.payment.payment_detail(id),
        defaultOption = {
            method: 'GET',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
    if (typeof url === "string") {
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}

function createUpdatePayment(data, name, id) {
    let rate = data.rate,
        rateField = $('#new_payment_rate');
    $('#payment_name').text(name);
    $('#payment_date').text(data.created_at);
    rateField.val(rate).prop('readonly', false);
    (data.currency_rate.id == '2') && rateField.prop('readonly', true);
    $('#new_payment_sum').val(data.sum);
    $('#payment_sent_date').val(data.sent_date);
    $('.note').val(data.description);
    $('#complete-payment').attr('data-id', id);
    $('#delete-payment').attr('data-id', id);
}

export function updateDealsPayment(id, data = {}) {
    let url = URLS.payment.edit_payment(id),
        defaultOption = {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify(data),
        };
    if (typeof url === "string") {
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}

export function cleanUpdateDealsPayment() {
    let $inputs = $('#payment-form').find('input:visible');
    $inputs.each(function () {
        $(this).val('');
    });
    $('#payment-form').find('.note').val('');
    $('#payment_name').text('');
    $('#payment_date').text('');
}

export function deleteDealsPayment(id) {
    let url = URLS.payment.edit_payment(id),
        defaultOption = {
            method: 'DELETE',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
    if (typeof url === "string") {
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}

export function showPayments(id, type) {
    let url = (type === 'people') ? URLS.deal.payments(id) : URLS.church_deal.payments(id);
    getData(url).then(function (data) {
        let payments_table = '';
        let sum, date_time, manager;
        data.forEach(function (payment) {
            sum = payment.sum_str;
            date_time = payment.sent_date;
            manager = `${payment.manager.last_name} ${payment.manager.first_name} ${payment.manager.middle_name}`;
            payments_table += `<tr><td>${sum}</td><td>${date_time}</td><td>${manager}</td></tr>`
        });
        $('#popup-payments table').html(payments_table);
        $('#popup-payments').css('display', 'block');
    })
}

// function getPayment(id) {
//     return new Promise(function (resolve, reject) {
//         ajaxRequest(URLS.deal.payments(id), null, function (data) {
//             resolve(data);
//         }, 'GET', true, {
//             'Content-Type': 'application/json'
//         }, {
//             403: function (data) {
//                 data = data.responseJSON;
//                 reject();
//                 showAlert(data.detail)
//             }
//         })
//     })
// }

export function createPaymentsTable(config) {
    Object.assign(config, getSearch('search_purpose_fio'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getPaymentsDeals(config).then(function (data) {
        let count = data.count,
            page = config['page'] || 1,
            pages = Math.ceil(count / CONFIG.pagination_count),
            showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
            id = "paymentsList",
            currency = data.payments_sum,
            uah = (currency.uah.sum != null) ? beautifyNumber(currency.uah.sum) : 0,
            usd = (currency.usd.sum != null) ? beautifyNumber(currency.usd.sum) : 0,
            eur = (currency.eur.sum != null) ? beautifyNumber(currency.eur.sum) : 0,
            rub = (currency.rur.sum != null) ? beautifyNumber(currency.rur.sum) : 0,
            text = `Показано ${showCount} из ${count} на сумму: ${uah} грн, ${usd} дол, ${eur} евро, ${rub} руб`;
        let paginationConfig = {
            container: ".payments__pagination",
            currentPage: page,
            pages: pages,
            callback: createPaymentsTable
        };
        makePaymentsTable(data, id);
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createPaymentsTable, ".table-wrap th");
    }).catch(function (err) {
        console.log(err);
    });
}

function getPaymentsDeals(config) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.payment.deals(),
            method: 'GET',
            data: config,
            headers: {
                'Content-Type': 'application/json'
            },
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