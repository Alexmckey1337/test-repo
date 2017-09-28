'use strict';
import {CONFIG} from '../config';
import URLS from '../Urls/index';
import getData, {postData} from '../Ajax/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getFilterParam} from '../Filter/index';
import OrderTable, {getOrderingData} from '../Ordering/index';
import {makePastorList, makeDepartmentList} from '../MakeList/index';
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import {showAlert} from "../ShowNotifications/index";
import {hidePopup} from "../Popup/popup";
import DeleteChurchUser from '../User/deleteChurchUser';
import {addUser2Church} from "../User/addUser";

export function createChurchesTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getData(URLS.church.list(), config).then(function (data) {
        let count = data.count;
        let page = config['page'] || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
        let text = `Показано ${showCount} из ${count}`;
        let tmpl = $('#databaseUsers').html();
        let filterData = {};
        filterData.user_table = data.table_columns;
        filterData.results = data.results;
        let rendered = _.template(tmpl)(filterData);
        $('#tableChurches').html(rendered);
        $('.quick-edit').on('click', function () {
            let id = $(this).closest('.edit').find('a').attr('data-id');
            getData(URLS.church.detail(id)).then((data) => {
                let quickEditCartTmpl, rendered;
                quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                rendered = _.template(quickEditCartTmpl)(data);
                $('#quickEditCartPopup').find('.popup_body').html(rendered);
                $('#openingDate').datepicker({
                    dateFormat: 'yyyy-mm-dd',
                    autoClose: true
                });
                makePastorList(data.department, '#editPastorSelect', data.pastor);
                makeDepartmentList('#editDepartmentSelect', data.department).then(function () {
                    $('#editDepartmentSelect').on('change', function () {
                        let id = parseInt($(this).val());
                        makePastorList(id, '#editPastorSelect');
                    })
                });
                setTimeout(function () {
                    $('#quickEditCartPopup').css('display', 'block');
                }, 100)
            })
        });

        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createChurchesTable
        };
        makePagination(paginationConfig);
        fixedTableHead();
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createChurchesTable, ".table-wrap th");
    });
}

export function clearAddChurchData() {
    $('#added_churches_date').val('');
    $('#added_churches_is_open').prop('checked', false);
    $('#added_churches_title').val('');
    $('#added_churches_country').val('');
    $('#added_churches_city').val('');
    $('#added_churches_address').val('');
    $('#added_churches_phone').val('');
    $('#added_churches_site').val('');
}

export function saveChurches(el) {
    let $input, $select, phone_number, opening_date, data, id;
    id = parseInt($($(el).closest('.pop_cont').find('#churchID')).val());
    opening_date = $($(el).closest('.pop_cont').find('#openingDate')).val();
    if (!opening_date && opening_date.split('-').length !== 3) {
        $($(el).closest('.pop_cont').find('#openingDate')).css('border-color', 'red');
        return
    }
    data = {
        title: $($(el).closest('.pop_cont').find('#church_title')).val(),
        pastor: $($(el).closest('.pop_cont').find('#editPastorSelect')).val(),
        department: $($(el).closest('.pop_cont').find('#editDepartmentSelect')).val(),
        phone_number: $($(el).closest('.pop_cont').find('#phone_number')).val(),
        website: ($(el).closest('.pop_cont').find('#web_site')).val(),
        opening_date: $($(el).closest('.pop_cont').find('#openingDate')).val() || null,
        is_open: $('#is_open_church').is(':checked'),
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        region: $($(el).closest('.pop_cont').find('#region')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val(),
        report_currency: $($(el).closest('.pop_cont').find('#EditReport_currency')).val(),
    };
    saveChurchData(data, id).then(function () {
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
        })
    }).catch(function (res) {
        let error = JSON.parse(res.responseText);
        let errKey = Object.keys(error);
        let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
        showAlert(html);
    });
}

function saveChurchData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        return new Promise(function (resolve, reject) {
            let data = {
                url: URLS.church.detail(id),
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
        });
    }
}

export function addChurch(e, el, callback) {
    e.preventDefault();
    let data = getAddChurchData();
    postData(URLS.church.list(), data).then(function (data) {
        hidePopup(el);
        clearAddChurchData();
        callback();
        showAlert(`Церковь ${data.get_title} добавлена в базу`);
    }).catch(function (data) {
        hidePopup(el);
        showAlert('Ошибка при создании церкви');
    });
}

function getAddChurchData() {
    return {
        "opening_date": $('#added_churches_date').val(),
        "is_open": $('#added_churches_is_open').prop('checked'),
        "title": $('#added_churches_title').val(),
        "department": $('#department_select').val(),
        "pastor": $('#pastor_select').val(),
        "country": $('#added_churches_country').val(),
        "city": $('#added_churches_city').val(),
        "address": $('#added_churches_address').val(),
        "phone_number": $('#added_churches_phone').val(),
        "website": $('#added_churches_site').val()
    }
}

function addChurchTODataBase(config) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.church.list(),
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

export function createChurchesDetailsTable(config = {}, id, link) {
    if (config.id === undefined) {
        id = $('#church').attr('data-id');
    } else {
        id = config.id;
    }
    if (link === undefined) {
        link = $('.get_info .active').data('link');
    }
    Object.assign(config, getOrderingData());
    getChurchDetails(id, link, config).then(function (data) {
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
        $('#tableUserINChurches').html(rendered).on('click', '.delete_btn', function () {
            let ID = $(this).closest('td').find('a').data('id'),
                userName = $(this).closest('td').find('a').text(),
                DelUser = new DeleteChurchUser(ID, $('#church').data('id'), createChurchesDetailsTable, userName, 'церкви');
            DelUser.popup();

        });
        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            id: id,
            callback: createChurchesDetailsTable
        };
        makePagination(paginationConfig);
        fixedTableHead();
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createChurchesDetailsTable, ".table-wrap th");
    })
}

function getChurchDetails(id, link, config) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(`${URLS.church.detail(id)}${link}/`, config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        })
    });
}

export function setOptionsToPotentialLeadersSelect(churchId) {
    let config = {
        church: churchId,
    };
    getPotentialLeadersForHG(config).then(function (data) {
        let options = data.map((item) => {
            let option = document.createElement('option');
            return $(option).val(item.id).text(item.fullname);
        });
        $('#added_home_group_pastor').html(options).prop('disabled', false).select2();
    });
}

function getPotentialLeadersForHG(config) {
    return new Promise(function (resolve, reject) {
        let url = URLS.home_group.potential_leaders();
        ajaxRequest(url, config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

export function makeUsersFromDatabaseList(config = {}) {
    getUsersTOChurch(config).then(function (data) {
        const CHURCH_ID = $('#church').data('id');
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
                    let _self = this;
                    let config = {};
                    config.id = id;
                    addUser2Church(config).then(function (data) {
                        $(_self).text('Добавлен').attr('disabled', true);
                        getChurchStats(CHURCH_ID).then(function (data) {
                            let keys = Object.keys(data);
                            keys.forEach(function (item) {
                                $('#' + item).text(data[item]);
                            })
                        });
                        createChurchesUsersTable(CHURCH_ID);
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

function getUsersTOChurch(config) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.church.potential_users_church(), config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

function addUserToChurch(user_id, id, exist = false) {
    let url = URLS.user.set_church(user_id);
    let config = {
        url: url,
        method: "POST",
        data: {
            church_id: id
        }
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}

function getChurchStats(id) {
    let resData = {
        url: URLS.church.stats(id)
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

function createChurchesUsersTable(id, config = {}) {
    Object.assign(config, getFilterParam());
    getChurchUsers(id).then(function (data) {
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
        $('#tableUserINChurches').html(rendered);
        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            id: id,
            callback: createChurchesUsersTable
        };
        makePagination(paginationConfig);
        fixedTableHead();
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
    })
}

function getChurchUsers(id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.church.users(id), null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}

export function reRenderTable(config) {
    const CHURCH_ID = $('#church').data('id');
    addUser2Church(config).then(() => createChurchesUsersTable(CHURCH_ID));
}

export function editChurches(el, id) {
    let data = {
        pastor: $($(el).closest('form').find('#editPastorSelect')).val(),
        department: $($(el).closest('form').find('#editDepartmentSelect')).val(),
        phone_number: $($(el).closest('form').find('#phone_number')).val(),
        website: ($(el).closest('form').find('#web_site')).val(),
        opening_date: $($(el).closest('form').find('#opening_date')).val().split('.').reverse().join('-') || null,
        is_open: $('#is_open_church').is(':checked'),
        country: $($(el).closest('form').find('#country')).val(),
        city: $($(el).closest('form').find('#city')).val(),
        address: $($(el).closest('form').find('#address')).val(),
        report_currency: $($(el).closest('form').find('#report_currency')).val()
    };
    saveChurchData(data, id).then(function (data) {
        $(el).closest('form').find('.edit').removeClass('active');
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