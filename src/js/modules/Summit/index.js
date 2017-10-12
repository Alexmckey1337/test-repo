'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
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

export function predeliteAnket(id) {
    let config = {
        url: URLS.summit_profile.predelete(id),
    };
    return new Promise((resolve, reject) => {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject);
    })
}

export function deleteSummitProfile(id) {
    let config = {
        url: URLS.summit_profile.detail(id),
        method: "DELETE"
    };
    return new Promise((resolve, reject) => {
        let codes = {
            204: function () {
                resolve('Пользователь удален из саммита');
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject);
    })
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

export function registerUser(id, summit_id, description) {
    let data = {
        "user": id,
        "summit": summit_id,
        "description": description,
    };

    let json = JSON.stringify(data);
    registerUserToSummit(json);
}

function registerUserToSummit(config) {
    ajaxRequest(URLS.summit_profile.list(), config, function (data) {
        showAlert("Пользователь добавлен в саммит.");
        createSummitUsersTable();
    }, 'POST', true, {
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
        }
    });
}

export function makePotencialSammitUsersList() {
    let param = {'summit_id': 7};
    let search = $('#searchUsers').val();
    if (search) {
        param['search'] = search;
    }
    console.log(param);
    param.summit_id = $('#summitUsersList').data('summit');
    getPotencialSammitUsers(param).then(function (data) {
        let html = '';
        data = data.results;
        for (let i = 0; i < data.length; i++) {
            html += '<div class="rows-wrap"><button data-master="' + data[i].master_short_fullname + '" data-name="' + data[i].fullname + '" data-id="' + data[i].id + '">Выбрать</button><div class="rows"><div class="col"><p><span><a href="/account/' + data[i].id + '">' + data[i].fullname + '</a></span></p></div><div class="col"><p><span>' + data[i].country + '</span>,<span> ' + data[i].city + '</span></p></div></div></div>';
        }
        if (data.length > 0) {
            $('#searchedUsers').html(html);
        } else {
            $('#searchedUsers').html('<div class="rows-wrap"><div class="rows"><p>По запросу не найдено учасников</p></div></div>');
        }
        $('.choose-user-wrap .splash-screen').addClass('active');
        let but = $('.rows-wrap button');
        but.on('click', function () {
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

function getPotencialSammitUsers(config) {
    console.log(config);
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.summit_search(), config, function (data) {
            resolve(data);
        });
    });
}

export function setDataForPopup(id, name, master) {
    $('#complete').attr('data-id', id);
    $('#client-name').html(name);
    $('#responsible-name').html(master);
}