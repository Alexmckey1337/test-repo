'use strict';
import 'hint.css/hint.min.css';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import getData, {postData} from "../Ajax/index";
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getOrderingData} from "../Ordering/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {getFilterParam} from "../Filter/index";
import {showAlert} from "../ShowNotifications/index";
import shortenText from '../shortenText';

export function createSummitUsersTable(data = {}) {
    let page = data.page || $('.pagination__input').val();
    let summitId = data.summit || $('#summitsTypes').find('.active').data('id') || $('#summitUsersList').data('summit');
    let config = {
        page: page
    };
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, data);
    Object.assign(config, getOrderingData());

    getSummitUsers(summitId, config).then(function (data) {
        let filter_data = {};
        let common_table = Object.keys(data.common_table);
        filter_data.results = data.results.map(function (item) {
            let data;
            data = item;
            data.ankets_id = item.id;
            common_table.forEach(function (field) {
                data[field] = item[field];
            });
            return data;
        });
        filter_data.user_table = data.user_table;
        common_table.forEach(function (item) {
            filter_data.user_table[item] = data.common_table[item];
        });
        let count = data.count;
        let page = config.page || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
        let id = "summitUsersList";
        let text = `Показано ${showCount} из ${count}`;
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createSummitUsersTable
        };
        makeSammitsDataTable(filter_data, id);
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.user_table);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createSummitUsersTable, ".table-wrap th");
    });
}

function getSummitUsers(summitId, config = {}) {
    Object.assign(config, getFilterParam());
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.summit.users(summitId),
            data: config,
            method: 'GET',
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

function makeSammitsDataTable(data, id) {
    let tmpl = document.getElementById('databaseUsers').innerHTML,
        rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        makeQuickEditSammitCart(this);
    });
    $('.send_email').on('click', function () {
        let id = $(this).attr('data-id');
        getData(URLS.summit.send_code(id)).then(() => {
            showAlert('Код отправлен на почту');
            createSummitUsersTable();
        }).catch(err => {
            showAlert(err.detail);
        });
    });
    fixedTableHead();
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

// export function predeliteAnket(id) {
//     let config = {
//         url: URLS.summit_profile.predelete(id),
//     };
//     return new Promise((resolve, reject) => {
//         let codes = {
//             200: function (data) {
//                 resolve(data);
//             },
//             400: function (data) {
//                 reject(data)
//             }
//         };
//         newAjaxRequest(config, codes, reject);
//     })
// }

// export function deleteSummitProfile(id) {
//     let config = {
//         url: URLS.summit_profile.detail(id),
//         method: "DELETE"
//     };
//     return new Promise((resolve, reject) => {
//         let codes = {
//             204: function () {
//                 resolve('Пользователь удален из саммита');
//             },
//             400: function (data) {
//                 reject(data)
//             }
//         };
//         newAjaxRequest(config, codes, reject);
//     })
// }

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

export function registerUser(id, summit_id, description) {
    let data = {
        "user": id,
        "summit": summit_id,
        "description": description,
    };
    // let json = JSON.stringify(data);
    postData(URLS.summit_profile.list(), data).then(() => {
        showAlert("Пользователь добавлен в саммит.");
        createSummitUsersTable();
        $('#searchedUsers').find(`button[data-id=${id}]`).prop('disabled', true);
    }).catch((err) => {
        showAlert('Ошибка добавления пользователя');
        console.log(err);
    })
    // registerUserToSummit(json);
}

// function registerUserToSummit(config) {
//     ajaxRequest(URLS.summit_profile.list(), config, function (data) {
//         showAlert("Пользователь добавлен в саммит.");
//         createSummitUsersTable();
//     }, 'POST', true, {
//         'Content-Type': 'application/json'
//     }, {
//         400: function (data) {
//             data = data.responseJSON;
//             showAlert(data.detail);
//         },
//         404: function (data) {
//             data = data.responseJSON;
//             showAlert(data.detail);
//         },
//         403: function (data) {
//             data = data.responseJSON;
//             showAlert(data.detail);
//         }
//     });
// }

export function makePotencialSammitUsersList(config = {}) {
    let param = {'summit_id': 7},
        search = $('#searchUsers').val();
    if (search) {
        param['search'] = search;
    }
    Object.assign(param, config);
    param.summit_id = $('#summitUsersList').data('summit');
    getData(URLS.summit_search(), param).then(data => {
        let pagination = `<div class="top-pag">
                              <div class="table__count"></div>
                              <div class="pagination search_users_pagination"></div>
                          </div>
                          <div class="table-wrap clearfix">
                              <div id="potentialUsersList" class="table scrollbar-inner"></div>
                          </div>`;
        let table = `<table>
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
                                ${item.fullname}</a>
                        </td>
                        <td>${item.country}/${item.city}</td>
                        <td>${item.master_short_fullname}</td>
                        <td>${item.email}</td>
                        <td>${item.phone_number}</td>
                        <td>
                            <button data-master="${item.master_short_fullname}" 
                                    data-name="${item.fullname}" 
                                    data-id="${item.id}">
                                    Выбрать
                            </button>
                        </td>
                    </tr>`;
        }).join('')}</tbody></table>`;
        if (data.results.length > 0) {
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
            $('#searchedUsers').html(pagination).find('.table__count').text(text);
            makePagination(paginationConfig);
            $('#potentialUsersList').html(table);
            $('.preloader').css('display', 'none');
            $('.shorten').each(function (i, el) {
                let cutTxt = shortenText(el.text.trim());
                $(this).text(cutTxt);
            });
        } else {
            $('#searchedUsers').html('<div class="rows-wrap"><div class="rows"><p>По запросу учасников не найдено</p></div></div>');
        }
        $('.choose-user-wrap .splash-screen').addClass('active');
        let btn = $('#searchedUsers').find('table').find('button');
        btn.on('click', function () {
            let id = $(this).attr('data-id'),
                name = $(this).attr('data-name'),
                master = $(this).attr('data-master');
            $('#summit-value').val("0");
            $('#summit-value').attr('readonly', true);
            $('#popup textarea').val("");
            setDataForPopup(id, name, master);
            $('#popup').css('display', 'block');
        });
    });
}

// function getPotencialSammitUsers(config) {
//     console.log(config);
//     return new Promise(function (resolve, reject) {
//         ajaxRequest(URLS.summit_search(), config, function (data) {
//             resolve(data);
//         });
//     });
// }

export function setDataForPopup(id, name, master) {
    $('#complete').attr('data-id', id);
    $('#client-name').html(name);
    $('#responsible-name').html(master);
}