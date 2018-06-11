'use strict';
import 'hint.css/hint.min.css';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import getData, {postData} from "../Ajax/index";
import ajaxRequest from '../Ajax/ajaxRequest';
import getSearch from '../Search/index';
import {getOrderingData} from "../Ordering/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {getFilterParam} from "../Filter/index";
import {btnDeals} from "../Deals/index";
import {showAlert} from "../ShowNotifications/index";
import shortenText from '../shortenText';
import errHandling from '../Error';
import pageCursor from '../pageCursor';

export function createSummitUsersTable(data = {}) {
    let page = data.page || $('.pagination__input').val() || 1,
        summitId = data.summit || $('#summitsTypes').find('.active').data('id') || $('#summitUsersList').data('summit'),
        config = {page};
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, data);
    Object.assign(config, getOrderingData());
    Object.assign(config, getFilterParam());

    getData(URLS.summit.users(summitId), config).then(data => {
        let count = data.count,
            page = config.page || 1,
            pages = Math.ceil(count / CONFIG.pagination_count),
            showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
                container: ".users__pagination",
                currentPage: page,
                pages: pages,
                callback: createSummitUsersTable
            };
        makeSammitsDataTable(data, "summitUsersList");
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createSummitUsersTable, ".table-wrap th");
    }).catch(err => {
        errHandling(err);
        $('.preloader').css('display', 'none');
    });
}

export function updateSummitUsersTable() {
    $('.preloader').css('display', 'block');
    let page = $('.pagination .pagination__input').val();
    createSummitUsersTable({page: page});
}

function makeSammitsDataTable(data, selector) {
    let tmpl = document.getElementById('databaseUsers').innerHTML,
        rendered = _.template(tmpl)(data);
    document.getElementById(selector).innerHTML = rendered;
    $('table').on('click', '.quick-edit', function () {
        makeQuickEditSammitCart(this);
    });
    btnDeals(true);

    $('#summitUsersList').on('click', '.show_payments', function () {
        let id = $(this).data('id');
        showSummitPayments(id);
    });
    $('.send_email').on('click', function () {
        let id = $(this).attr('data-id');
        getData(URLS.summit.send_code(id)).then(_ => {
            showAlert('Код отправлен на почту');
            createSummitUsersTable();
        }).catch(err => errHandling(err));
    });
    fixedTableHead();
    pageCursor();
}

function showSummitPayments(id) {
    let url = URLS.summit_profile.list_payments(id);
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
    }).catch(err => errHandling(err));
}

function makeQuickEditSammitCart(el) {
    let anketID, id, link, url;
    anketID = $(el).closest('td').find('a').data('ankets');
    id = $(el).closest('td').find('a').data('id');
    link = $(el).closest('td').find('a').data('link');
    url = URLS.summit_profile.detail(anketID);
    ajaxRequest(url, null, function (data) {
        $('#fullNameCard').text(data.full_name);
        $('#userDescription').val(data.description);
        $('#summit-valueDelete').val(data.total_sum);
        $('#member').prop("checked", data.is_member);
        $('#userID').val(data.user_id);
        $('#applyChanges').data('id', data.id);
        $('#preDeleteAnket').attr('data-id', data.user_id).attr('data-anket', data.id);
        $('#popupParticipantInfo').css('display', 'block');
    }, 'GET', true, {
        'Content-Type': 'application/json'
    });
}

export function unsubscribeOfSummit(id) {
    ajaxRequest(URLS.summit_profile.detail(id), null, function () {
        let data = {};
        data['summit'] = summit_id;
        getUsersList(path, data);
        document.querySelector('#popupDelete').style.display = 'none';
    }, 'DELETE', true, {
        'Content-Type': 'application/json'
    });
}

export function updateSummitParticipant(profileID, data) {
    updateSummitProfile(profileID, JSON.stringify(data));
}

export function updateSummitProfile(profileID, config) {
    ajaxRequest(URLS.summit_profile.detail(profileID), config, function (data) {
        showAlert("Данные участника саммита изменены.");
        createSummitUsersTable();
    }, 'PATCH', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);
        },
        404: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);
        },
        403: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);
        },
        405: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);
        }
    });
}

export function registerUser(id, summit_id) {
    let author = $('#client_author_reg').val(),
        data = {
            "user": id,
            "summit": summit_id,
        };
    author && Object.assign(data, {author});
    postData(URLS.summit_profile.list(), data).then(() => {
        showAlert("Пользователь добавлен в саммит.");
        createSummitUsersTable();
        $('#searchedUsers').find(`button[data-id=${id}]`).prop('disabled', true);
        $('#popup').css('display', 'none');
    }).catch(err => errHandling(err))
}

function makePotencialSammitUsersTable(data, text) {
    if (!data.results.length) {
        $('#searchedUsers').html('<div class="rows-wrap"><div class="rows"><p>По запросу пользователей не найдено</p></div></div>');
        return;
    }
    let pagination = `<div class="top-pag">
                <div class="table__count"></div>
                <div class="pagination search_users_pagination"></div>
            </div>
            <div class="table-wrap clearfix">
                <div id="potentialUsersList" class="table scrollbar-inner"></div>
            </div>`,
        table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Страна/город</th>
                                <th>Ответственный</th>
                                <th>Email</th>
                                <th>Номер телефона</th>
                                <th>Действие</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
        return `<tr>
                        <td><a target="_blank" href="/account/${item.id}" 
                                class="hint--top-right hint--info shorten" aria-label="${item.fullname}">
                                ${shortenText(item.fullname.trim())}</a>
                        </td>
                        <td>${item.country}/${item.city}</td>
                        <td>${item.master_short_fullname}</td>
                        <td>${item.email}</td>
                        <td>${item.phone_number}</td>
                        <td>
                            <button class="add_participant" data-id="${item.id}">Выбрать</button>
                        </td>
                    </tr>`;
    }).join('')}</tbody></table>`;
    $('#searchedUsers').html(pagination).find('.table__count').text(text);
    $('#potentialUsersList').html(table);
}

export function makePotencialSammitUsersList(config = {}) {
    const SUMMIT_ID = $('#summitUsersList').attr('data-summit');
    Object.assign(config, {summit_id: SUMMIT_ID});
    let search = $('#searchUsers').val();
    search && Object.assign(config, {search});
    getData(URLS.summit_search(), config).then(data => {
        let count = data.count,
            page = config.page || 1,
            pages = Math.ceil(count / CONFIG.pagination_count_small),
            showCount = (count < CONFIG.pagination_count_small) ? count : data.results.length,
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
                container: ".search_users_pagination",
                currentPage: page,
                pages: pages,
                callback: makePotencialSammitUsersList
            };
        makePotencialSammitUsersTable(data, text);
        makePagination(paginationConfig);
        $('.preloader').css('display', 'none');
        $('.choose-user-wrap .splash-screen').addClass('active');
    });
}

export function setDataForAddParticipantPopup(id) {
    $('#popup').attr('data-id', id);
    getData(URLS.user.summit_info(id)).then(data => {
        console.log(data)
        let bishop = data.bishop,
            email = data.email,
            name = data.fullname;
        $('#client_img').attr('src', data.image);
        $('#client_name').text(name ? name : '');
        $('#client_department').text(data.departments.map(item => item.title).join(','));
        $('#client_bisop').text(bishop ? bishop.title : '');
        $('#client_email').val(email ? email : '');
        $('#client_phone').val(data.phone_number);
    })
}

export function makeAuthorRegList(id) {
    getData(URLS.summit.author_registration(id)).then(data => {
        const options = data.map(option => `<option value="${option.id}">${option.title}</option>`);
        $('#client_author_reg').html(`<option value="">Без ответственного</option>`).append(options).select2();
    });
}

export function addUserToSummit(id) {
    const SUMMIT_ID = $('#summitUsersList').attr('data-summit');
    makeAuthorRegList(SUMMIT_ID);
    setDataForAddParticipantPopup(id);
    $('#popup').css('display', 'block');
}