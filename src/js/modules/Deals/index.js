'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import getData, {postData, deleteData} from "../Ajax/index";
import moment from 'moment/min/moment.min.js';
import numeral from 'numeral/min/numeral.min.js';
import getSearch from '../Search/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable, {getOrderingData} from '../Ordering/index';
import {showAlert, showConfirm} from "../ShowNotifications/index";
import {showPayments} from "../Payment/index";
import {convertNum} from "../ConvertNum/index";

export function btnDeals() {
    $("button.pay").on('click', function () {
        let id = $(this).attr('data-id'),
            val = $(this).attr('data-value'),
            value = numeral(val).value(),
            total = $(this).attr('data-total_sum'),
            total_sum = isNaN(numeral(total).value()) ? parseFloat(total) : numeral(total).value(),
            diff = (value - total_sum).toFixed(2),
            currencyName = $(this).attr('data-currency-name'),
            currencyID = $(this).attr('data-currency-id'),
            payer = $(this).attr('data-name'),
            responsible = $(this).attr('data-responsible'),
            date = $(this).attr('data-date');
        $('#complete-payment').attr('data-id', id);
        diff = diff > 0 ? diff : 0;
        $('#payment_name').text(payer);
        $('#payment_responsible').text(responsible);
        $('#payment_date').text(date);
        $('#payment_sum, #all_payments').text(`${convertNum(value, ',')} ${currencyName}`);
        clearSumChange(total_sum);
        sumChange(diff, currencyName, currencyID, total_sum);
        $('#complete-payment').prop('disabled', false);
        $('#popup-create_payment').css('display', 'block');
        $('#new_payment_rate').focus();
    });
}

function clearSumChange(total) {
    $('#payment-form').get(0).reset();
    $('#new_payment_sum').val('');
    $('#new_payment_rate').val('').prop('readonly', false);
    $('#sent_date').val(moment(new Date()).format('DD.MM.YYYY'));
    $('#payment-form').find('textarea').val('');
    $('#user_payment').text(convertNum(total, ','));
}

function sumChange(diff, currencyName, currencyID, total) {
    let currencies = $('#new_payment_rate'),
        payment = $('#new_payment_sum'),
        curr;
    $('#close_sum').text(`${convertNum(diff, ',')} ${currencyName}`);
    currencies.on('keyup', _.debounce(function () {
        if (currencyID != 2) {
            curr = convertNum($(this).val(), '.');
            let uah = parseFloat((diff * curr).toFixed(2));
            payment.val(convertNum(uah, ','));
            $('#user_payment').text(`${convertNum((+diff + +total), ',')} ${currencyName}`);
        }
    }, 500));
    payment.on('keyup', _.debounce(function () {
        if (currencyID != 2) {
            let pay = convertNum($(this).val(), '.');
            curr = convertNum(currencies.val(), '.');
            let result = parseFloat((pay / curr).toFixed(2));
            $('#user_payment').text(`${convertNum((+result + +total), ',')} ${currencyName}`);
        } else {
            let pay = convertNum($(this).val(), '.');
            $('#user_payment').text(`${convertNum((+pay + +total), ',')} ${currencyName}`);
        }
    }, 500));
    if (currencyID === '2') {
        currencies.val('1,0').prop('readonly', true);
        payment.val(convertNum(diff, ','));
        $('#user_payment').text(`${convertNum((+diff + +total).toFixed(2), ',')} ${currencyName}`);
    }
}

export function DealsTable(config = {}) {
    getData(URLS.deal.list(), config).then(data => {
        $('.preloader').css('display', 'none');
        makeDealsTable(data);
    });
}

function makeDealsTable(data, config = {}) {
    let tmpl = $('#databaseDeals').html();
    let rendered = _.template(tmpl)(data);
    $('#dealsList').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".deals__pagination",
        currentPage: page,
        pages: pages,
        callback: dealsTable
    },
        type = $('#statusTabs').find('.current button').attr('data-type');
    makePagination(paginationConfig);
    $('.table__count').text(text);
    fixedTableHead();
    makeSortForm(data.table_columns);
    $('.preloader').css('display', 'none');
    new OrderTable().sort(dealsTable, ".table-wrap th");
    btnDeals();
    $("button.complete").on('click', function () {
        let id = $(this).attr('data-id');
        updateDeals(id, type);
    });
    $('.show_payments').on('click', function () {
        let id = $(this).data('id');
        showPayments(id, type);
    });
    $('.quick-edit').on('click', function () {
        makeQuickEditDeal(this, type);
    });
}

export function dealsTable(config = {}) {
    let type = $('#statusTabs').find('.current button').attr('data-type'),
        url = (type === 'people') ? URLS.deal.list() : URLS.church_deal.list();
    Object.assign(config, getSearch('search'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    Object.assign(config, getTabsFilterParam());
    getData(url, config).then(data => {
        $('.preloader').css('display', 'none');
        makeDealsTable(data, config);
    })
}

function updateDeals(id, type) {
    let data = {
        "done": true,
    },
        url = (type === 'people') ? URLS.deal.detail(id) : URLS.church_deal.detail(id);
    postData(url, data, {method: 'PATCH'}).then(() => {
        updateDealsTable();
        document.getElementById('popup').style.display = '';
    }).catch(err => {
       showAlert('Ошибка при отправке на сервер');
       console.log(err);
    });
}

export function updateDealsTable() {
    $('.preloader').css('display', 'block');
    let page = $('#sdelki').find('.pagination__input').val();
    dealsTable({page: page});
}

function makeQuickEditDeal(el, type) {
    let id = $(el).attr('data-id'),
        popup = $('#popup-create_deal'),
        url = (type === 'people') ? URLS.deal.detail(id) : URLS.church_deal.detail(id);
    $('#send_new_deal').prop('disabled', false);
    getData(url).then(data => {
        let sum = numeral(data.value).value(),
            txt = `<div class="block_line">
                        <p>Плательщик:</p>
                        <p>${data.full_name}</p>
                    </div>
                    <div class="block_line">
                        <p>Менеджер:</p>
                        <p>${data.responsible_name}</p>
                    </div>`;
        $('#append-info').empty().append(txt);
        $('#new_deal_type').find(`option[value="${data.type}"]`).prop('selected', true).trigger('change');
        $('#new_deal_sum').val(sum);
        $('#new_deal_date').val(data.date_created);
        popup.find('.note').val(data.description);
        popup.find('.currency').val(data.currency.short_name);
        $('#send_new_deal').attr('data-id', id);
        $('#delete_deal').attr('data-id', id);
        popup.css('display', 'block');
    });
}

export function makeDuplicateDeals(config = {}) {
    let typeDeal = $('.partner_block_wrap').first().attr('data-type'),
        popup = $('#create_duplicate_deal_pop'),
        url = (typeDeal === 'CH') ? URLS.church_deal.check_duplicates() : URLS.deal.check_duplicates();
    getData(url, config).then(data => {
        let table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Сумма</th>
                                <th>Дата сделки</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
                            return `<tr>
                                        <td>${item.full_name}</td>
                                        <td>${item.value}</td>
                                        <td>${item.date_created}</td>
                                    </tr>`;
                        }).join('')}</tbody>
                        </table>`;
        let count = data.count,
            page = config.page || 1,
            pages = Math.ceil(count / CONFIG.pagination_duplicates_count),
            showCount = (count < CONFIG.pagination_duplicates_count) ? count : data.results.length,
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
                container: ".duplicate_users__pagination",
                currentPage: page,
                pages: pages,
                callback: makeDuplicateDeals
            };
        makePagination(paginationConfig);
        popup.find('.table__count').text(text);
        $('#table_duplicate_deal').html('').append(table);
        $('.preloader').css('display', 'none');
        popup.css('display', 'block');
    });
}

export function makeDuplicateDealsWithCustomPagin(config = {}) {
    let type = $('#statusTabs').find('.current button').attr('data-type'),
        url = (type === 'people') ? URLS.deal.find_duplicates() : URLS.church_deal.find_duplicates();
    Object.assign(config, getSearch('search'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    getData(url, config).then(data => {
        if (data.count !== 0) {
            let table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Сумма</th>
                                <th>Дата сделки</th>
                            </tr>
                        </thead>
                        <tbody>${data.deal_ids.map(item => {
                return `<tr>
                            <td class="edit">
                                <button class="delete_btn" data-id="${item.id}"></button>
                                ${data.partnership_fio}
                            </td>
                            <td>${ (item.payment_sum) ? item.payment_sum : 0 } / ${data.value}</td>
                            <td>${data.date_created}</td>
                        </tr>`;
                        }).join('')}</tbody>
                        </table>`;
            let count = data.count,
            page = config.page || 1,
            pages = count,
            text = `Показана ${page}-я страница из ${count}`,
            paginationConfig = {
                container: ".duplicate_users__pagination",
                currentPage: page,
                pages: pages,
                callback: makeDuplicateDealsWithCustomPagin
            };
            $("#table_duplicate").on('click', '.delete_btn', function () {
                let id = $(this).attr('data-id'),
                    pageCount = $('#create_duplicate_pop').find('.pagination__input').val();
                deleteDeal(id, pageCount, makeDuplicateDealsWithCustomPagin);
            });
        makePagination(paginationConfig);
        $('.pop-up_duplicate__table').find('.table__count').text(text);
        $('#table_duplicate').html('').append(table);
            $('.pop-up_duplicate__table').css('display', 'block');
        } else {
            showAlert('Дубликаты не найдены');
        }
        $('.preloader').css('display', 'none');
    });
}

export function deleteDeal(id, pageCount, callback) {
    let msg = 'Вы действительно хотите удалить данную сделку',
        type = $('#statusTabs').find('.current button').attr('data-type'),
        url = (type === 'people') ? URLS.deal.detail(id) : URLS.church_deal.detail(id);
    showConfirm('Удаление', msg, function () {
        deleteData(url).then(() => {
            showAlert('Сделка удалена');
            callback({page: pageCount});
            $('#popup-create_deal').css('display', 'none');
        }).catch(err => {
            showConfirm('Подтверждение удаления', err.message, function () {
                let force = JSON.stringify({"force": true});
                deleteData(url, {body: force}).then(() => {
                    showAlert('Сделка удалена');
                    callback({page: pageCount});
                    $('#popup-create_deal').css('display', 'none');
                }).catch(err => {
                    showAlert('При удалении сделки произошла ошибка');
                    console.log(err);
                });
            }, () => {
            });
        });
    }, () => {
    });
}


