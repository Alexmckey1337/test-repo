'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getData, {postData} from "../Ajax/index";
import {showAlert} from "../ShowNotifications/index";
import {hidePopup} from "../Popup/popup";
import {getOrderingData} from "../Ordering/index";
import DeleteHomeGroupUser from '../User/deleteHomeGroupUser';
import {addUserToHomeGroupHG} from "../User/addUser";
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {getPotentialLeadersForHG} from "../GetList/index";
import updateHistoryUrl from '../History/index';

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
    Object.assign(config, getSearch('search'));
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
    console.log(config);
    let $homeGroup = $('#home_group'),
        param = {
            search: $('#searchUserFromDatabase').val(),
            department: $('#home_group').attr('data-departament_id'),
        };
        const CH_ID = $homeGroup.attr('data-church-id'),
          ID = $homeGroup.attr('data-id');
    Object.assign(config, param);
    getData(URLS.church.potential_users_group(CH_ID), config).then(data => {
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
                                <th>Действие</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
            return `<tr>
                        <td><a target="_blank" href="/account/${item.id}">
                            ${item.full_name}
                        </a></td>
                        <td>${item.country}/${item.city}</td>
                        <td>
                            <button data-id="${item.id}"
                                    ${(!item.can_add) && 'disabled'}>
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
                    callback: makeUsersFromDatabaseList
                };
            $('#searchedUsers').html(pagination).find('.table__count').text(text);
            makePagination(paginationConfig);
            $('#potentialUsersList').html(table);
            $('.preloader').css('display', 'none');
        } else {
            $('#searchedUsers').html('<div class="rows-wrap"><div class="rows"><p>По запросу учасников не найдено</p></div></div>');
        }
        $('.choose-user-wrap .splash-screen').addClass('active');
        let btn = $('#searchedUsers').find('table').find('button');
        btn.on('click', function () {
            let id = $(this).data('id'),
                config = {
                user_id: id
            },
                _self = this;
            postData(URLS.home_group.add_user(ID), config).then(() => {
                $(_self).attr('disabled', true);
                getData(URLS.home_group.stats(ID)).then(data => {
                    let keys = Object.keys(data);
                    keys.forEach(function (item) {
                        $('#' + item).text(data[item]);
                    })
                });
                createHomeGroupUsersTable();
            });
        });
    })
}

// function getUsersTOHomeGroup(config, id) {
//     return new Promise(function (resolve, reject) {
//         ajaxRequest(URLS.church.potential_users_group(id), config, function (data) {
//             if (data) {
//                 resolve(data);
//             } else {
//                 reject("Ошибка");
//             }
//         });
//     });
// }
//
// function getHomeGroupStats(id) {
//     let resData = {
//         url: URLS.home_group.stats(id)
//     };
//     return new Promise(function (resolve, reject) {
//         let codes = {
//             200: function (data) {
//                 resolve(data);
//             },
//             400: function (data) {
//                 reject(data);
//             }
//         };
//         newAjaxRequest(resData, codes, reject);
//     });
// }

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

export function createHomeGroupsTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    updateHistoryUrl(config);
    getHomeGroups(config).then(function (data) {
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
        $('#tableHomeGroup').html(rendered);
        $('.quick-edit').on('click', function () {
            let id = $(this).closest('.edit').find('a').attr('data-id');
            ajaxRequest(URLS.home_group.detail(id), null, function (data) {
                let quickEditCartTmpl, rendered;
                quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                rendered = _.template(quickEditCartTmpl)(data);
                $('#quickEditCartPopup').find('.popup_body').html(rendered);
                getPotentialLeadersForHG({church: data.church.id}).then(function (res) {
                    return res.map(leader => `<option value="${leader.id}" ${(data.leader.id == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`);
                }).then(data => {
                    $('#homeGroupLeader').html(data).select2();
                });
                // getResponsibleBYHomeGroupSupeMegaNew({departmentId: data.department})
                //     .then(res => {
                //         return res.map(leader => `<option value="${leader.id}" ${(data.leader.id == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`);
                //     })
                //     .then(data => {
                //         $('#homeGroupLeader').html(data).select2();
                //     });
                setTimeout(function () {
                    $('.date').datepicker({
                        dateFormat: 'yyyy-mm-dd',
                        autoClose: true
                    });
                    //$('#quickEditCartPopup').css('display', 'block');
                    $('#quickEditCartPopup').addClass('active');
                    $('.bg').addClass('active');
                }, 100)
            })
        });
        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createHomeGroupsTable
        };
        makePagination(paginationConfig);
        fixedTableHead();
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createHomeGroupsTable, ".table-wrap th");
    });
}

function getHomeGroups(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.home_group.list(),
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

export function reRenderTable(config) {
    addUserToHomeGroupHG(config).then(() => createHomeGroupUsersTable());
}