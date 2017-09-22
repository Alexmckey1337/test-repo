'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import {showAlert} from "../ShowNotifications/index";
import {hidePopup} from "../Popup/popup";
import {getOrderingData} from "../Ordering/index";
import DeleteHomeGroupUser from '../User/deleteHomeGroupUser';
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {addUserToHomeGroupHG} from "../User/addUser";

export function addHomeGroup(e, el, callback) {
    e.preventDefault();
    let data = getAddHomeGroupData();
    let json = JSON.stringify(data);

    addHomeGroupToDataBase(json).then(function (data) {
        clearAddHomeGroupData();
        hidePopup(el);
        callback();
        showAlert(`Домашняя группа ${data.get_title} добавлена в базу данных`);
    }).catch(function (data) {
        hidePopup(el);
        showAlert('Ошибка при создании домашней группы');
    });
}

export function clearAddHomeGroupData() {
    $('#added_home_group_date').val('');
    $('#added_home_group_title').val('');
    $('#added_home_group_city').val('');
    $('#added_home_group_address').val('');
    $('#added_home_group_phone').val('');
    $('#added_home_group_site').val('');
}

function addHomeGroupToDataBase(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.home_group.list(),
            data: config,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };
        let status = {
            201: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }
        };
        newAjaxRequest(data, status, reject)
    });
}

function getAddHomeGroupData() {
    return {
        "opening_date": $('#added_home_group_date').val(),
        "title": $('#added_home_group_title').val(),
        "church": ($('#added_home_group_church_select').length) ? parseInt($('#added_home_group_church_select').val()) : $('#added_home_group_church').attr('data-id'),
        "leader": $('#added_home_group_pastor').val(),
        "city": $('#added_home_group_city').val(),
        "address": $('#added_home_group_address').val(),
        "phone_number": $('#added_home_group_phone').val(),
        "website": $('#added_home_group_site').val()
    }
}

export function saveHomeGroups(el, callback) {
    let $input, $select, phone_number, data, id;
    id = parseInt($($(el).closest('.pop_cont').find('#homeGroupsID')).val());

    data = {
        title: $($(el).closest('.pop_cont').find('#home_groups_title')).val(),
        leader: $($(el).closest('.pop_cont').find('#homeGroupLeader')).val(),
        department: $($(el).closest('.pop_cont').find('#editDepartmentSelect')).val(),
        phone_number: $($(el).closest('.pop_cont').find('#phone_number')).val(),
        website: ($(el).closest('.pop_cont').find('#web_site')).val(),
        opening_date: $($(el).closest('.pop_cont').find('#opening_date')).val() || null,
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val()
    };

    saveHomeGroupsData(data, id).then(function () {
        $(el).text("Сохранено");
        $(el).closest('.popap').find('.close-popup.change__text').text('Закрыть');
        $(el).attr('disabled', true);
        $input = $(el).closest('.popap').find('input');
        $select = $(el).closest('.popap').find('select');

        $select.on('change', function () {
            $(el).text("Сохранить");
            $(el).closest('.popap').find('.close-popup').text('Отменить');
            $(el).attr('disabled', false);
        });

        $input.on('change', function () {
            $(el).text("Сохранить");
            $(el).closest('.popap').find('.close-popup').text('Отменить');
            $(el).attr('disabled', false);
        });

        callback();
    }).catch(function (res) {
        let error = JSON.parse(res.responseText);
        let errKey = Object.keys(error);
        let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
        showAlert(html);
    });
}

function saveHomeGroupsData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        return new Promise(function (resolve, reject) {
            let data = {
                url: URLS.home_group.detail(id),
                data: json,
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            let status = {
                200: function (req) {
                    resolve(req);
                },
                400: function (req) {
                    reject(req);
                }
            };
            newAjaxRequest(data, status, reject)
        })
    }
}

export function createHomeGroupUsersTable(config = {}, id) {
    Object.assign(config, getOrderingData());
    if (id === undefined) {
        id = $('#home_group').data('id');
    }
    getHomeGroupUsers(config, id).then(function (data) {
        let count = data.count;
        let page = config['page'] || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
        let text = `Показано ${showCount} из ${count}`;
        let tmpl = $('#databaseUsers').html();
        let filterData = {};
        filterData.user_table = data.table_columns;
        filterData.results = data.results;
        let rendered = _.template(tmpl)(filterData);
        $('#tableUserINHomeGroups').html(rendered).on('click', '.delete_btn', function () {
            let ID = $(this).closest('td').find('a').data('id'),
                userName = $(this).closest('td').find('a').text(),
                DelUser = new DeleteHomeGroupUser(id, ID, createHomeGroupUsersTable, userName, 'домашней группы');
            DelUser.popup();
        });
        // $('.quick-edit').on('click', function () {
        //     let ID = $(this).closest('.edit').find('a').data('id'),
        //         userName = $(this).closest('td').find('a').text();
        //     initDeleteUserINHomeGroup(id, ID, userName);
        //     // deleteUserINHomeGroup(id, user_id).then(function () {
        //     //     createHomeGroupUsersTable(config, id);
        //     // })
        // });
        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createHomeGroupUsersTable
        };
        makePagination(paginationConfig);
        fixedTableHead();
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createHomeGroupUsersTable, ".table-wrap th");
    })
}

function getHomeGroupUsers(config, id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.home_group.users(id), config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}

export function makeUsersFromDatabaseList(config = {}, id) {
    let $homeGroup = $('#home_group');
    const CH_ID = $homeGroup.data('church-id');
    const ID = $homeGroup.data('id');
    getUsersTOHomeGroup(config, CH_ID).then(function (data) {
        let users = data;
        let html = [];
        if (users.length) {
            users.forEach(function (item) {
                let rows_wrap = document.createElement('div');
                let rows = document.createElement('div');
                let col_1 = document.createElement('div');
                let col_2 = document.createElement('div');
                let place = document.createElement('p');
                let link = document.createElement('a');
                let button = document.createElement('button');
                $(link).attr('href', '/account/' + item.id).text(item.full_name);
                $(place).text();
                $(col_1).addClass('col').append(link);
                $(col_2).addClass('col').append(item.country + ', ' + item.city);
                $(rows).addClass('rows').append(col_1).append(col_2);
                $(button).attr({
                    'data-id': item.id,
                    'disabled': !item.can_add
                }).text('Выбрать').on('click', function () {
                    let id = $(this).data('id');
                    let config = {};
                    config.id = id;
                    let _self = this;
                    addUserToHomeGroupHG(config).then(function (data) {
                        $(_self).text('Добавлен').attr('disabled', true);
                        getHomeGroupStats(ID).then(function (data) {
                            let keys = Object.keys(data);
                            keys.forEach(function (item) {
                                $('#' + item).text(data[item]);
                            })
                        });
                        createHomeGroupUsersTable();
                    });
                });
                $(rows_wrap).addClass('rows-wrap').append(button).append(rows);
                html.push(rows_wrap);
            });
        } else {
            let rows_wrap = document.createElement('div');
            let rows = document.createElement('div');
            let col_1 = document.createElement('div');
            $(col_1).text('Пользователь не найден');
            $(rows).addClass('rows').append(col_1);
            $(rows_wrap).addClass('rows-wrap').append(rows);
            html.push(rows_wrap);
        }
        $('#searchedUsers').html(html);
        $('.choose-user-wrap .splash-screen').addClass('active');
    })
}

function getUsersTOHomeGroup(config, id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.church.potential_users_group(id), config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

function getHomeGroupStats(id) {
    let resData = {
        url: URLS.home_group.stats(id)
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data);
            }
        };
        newAjaxRequest(resData, codes, reject);
    });
}

export function editHomeGroups(el, id) {
    let data = {
        leader: $($(el).closest('form').find('#homeGroupLeader')).val(),
        phone_number: $($(el).closest('form').find('#phone_number')).val(),
        website: ($(el).closest('form').find('#web_site')).val(),
        opening_date: $($(el).closest('form').find('#opening_date')).val().split('.').reverse().join('-') || null,
        city: $($(el).closest('form').find('#city')).val(),
        address: $($(el).closest('form').find('#address')).val()
    };

    saveHomeGroupsData(data, id).then(function () {
        let $input = $(el).closest('form').find('input:not(.select2-search__field), select');
        $input.each(function (i, elem) {
            $(this).attr('disabled', true);
            $(this).attr('readonly', true);
            if ($(elem).is('select')) {
                if ($(this).is(':not([multiple])')) {
                    if (!$(this).is('.no_select')) {
                        $(this).select2('destroy');
                    }
                }
            }
        });
        $(el).removeClass('active');
        $(el).closest('form').find('.edit').removeClass('active');
        let success = $($(el).closest('form').find('.success__block'));
        $(success).text('Сохранено');
        setTimeout(function () {
            $(success).text('');
        }, 3000);
    }).catch(function (res) {
        let error = JSON.parse(res.responseText);
        let errKey = Object.keys(error);
        let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
        showAlert(html);
    });
}

export function reRenderTable(config) {
    addUserToHomeGroupHG(config).then(() => createHomeGroupUsersTable());
}