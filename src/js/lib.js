/* global $ */
function getOrderingData() {
    let revers, order, savePath;
    let path = window.location.pathname;
    revers = window.sessionStorage.getItem('revers');
    order = window.sessionStorage.getItem('order');
    savePath = window.sessionStorage.getItem('path');
    if (savePath != path) {
        return
    }
    if (revers && order) {
        revers = (revers == "+") ? "" : revers;
        return {
            ordering: revers + order
        }
    }
}

function getChurches(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        };
        let status = {
            200: function (req) {
                resolve(req);
            },
            403: function () {
                reject('Вы должны авторизоватся');
            }

        };
        newAjaxRequest(data, status, reject)
    });
}

function predeliteAnket(id) {
    let config = {
        url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/summit_ankets/${id}/predelete/`,
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

function deleteSummitProfile(id) {
    let config = {
        url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/summit_ankets/${id}/`,
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

function addUserToChurch(user_id, id, exist = false) {
    let url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/${id}/add_user/`;
    let config = {
        url: url,
        method: "POST",
        data: {
            user_id: user_id
        }
    };
    if (exist) {
        config.method = "PUT";
    }
    return new Promise(function (resolve, reject) {
        let codes = {
            201: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}

function addUserToHomeGroup(user_id, hg_id, exist = false) {
    let url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${hg_id}/add_user/`;
    let config = {
        url: url,
        method: "POST",
        data: {
            user_id: user_id
        }
    };
    if (exist) {
        config.method = "PUT";
    }
    return new Promise(function (resolve, reject) {
        let codes = {
            201: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}

function createHomeGroupsTable(config = {}) {
    config.search_title = $('input[name="fullsearch"]').val();
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
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
            ajaxRequest(`${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${id}/`, null, function (data) {
                let quickEditCartTmpl, rendered;
                quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                rendered = _.template(quickEditCartTmpl)(data);
                $('#quickEditCartPopup').find('.popup_body').html(rendered);
                getResponsibleBYHomeGroup()
                    .then(res => {
                        return res.map(leader => `<option value="${leader.id}" ${(data.leader === leader.id) ? 'selected' : ''}>${leader.fullname}</option>`);
                    })
                    .then(data => {
                        $('#homeGroupLeader').html(data).select2();
                    })
                ;
                setTimeout(function () {
                    $('.date').datepicker({
                        dateFormat: 'yyyy-mm-dd',
                        autoClose: true
                    });
                    $('#quickEditCartPopup').css('display', 'block');
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        orderTable.sort(createHomeGroupsTable);
    });
}
function makePastorListWithMasterTree(config, selector, active = null) {
    getShortUsers(config).then(data => {
        let options = '<option selected>ВСЕ</option>';
        data.forEach(function (item) {
            options += `<option value="${item.id}"`;
            if (active == item.id) {
                options += 'selected';
            }
            options += `>${item.fullname}</option>`;
        });
        selector.forEach(item => {
            $(item).html(options).prop('disabled', false).select2();
        })
    })
}
function makePastorListNew(id, selector = [], active = null) {
    getResponsible(id, 2).then(function (data) {
        let options = '<option selected>ВСЕ</option>';
        data.forEach(function (item) {
            options += `<option value="${item.id}"`;
            if (active == item.id) {
                options += 'selected';
            }
            options += `>${item.fullname}</option>`;
        });
        selector.forEach(item => {
            $(item).html(options).prop('disabled', false).select2();
        })
    });
}
function makePastorList(id, selector, active = null) {
    console.log(id);
    getResponsible(id, 2).then(function (data) {
        let options = [];
        data.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.fullname);
            if (active == item.id) {
                $(option).attr('selected', true);
            }
            options.push(option);
        });
        $(selector).html(options).prop('disabled', false).select2();
    });
}

function makeLeaderList(id, selector, active = null) {
    getResponsible(id, 1).then(function (data) {
        let options = [];
        data.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.fullname);
            if (active == item.id) {
                $(option).attr('selected', true);
            }
            options.push(option);
        });
        $(selector).html(options).prop('disabled', false).select2();
    });
}

function getPartners(config) {
    config.search_fio = $('input[name=fullsearch]').val();
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getPartnersList(config).then(function (response) {
        let page = config['page'] || 1;
        let count = response.count;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let data = {};
        let id = "partnersList";
        let text = `Показано ${CONFIG.pagination_count} из ${count}`;
        let common_table = Object.keys(response.common_table);
        data.user_table = response.user_table;
        common_table.forEach(function (item) {
            data.user_table[item] = response.common_table[item];
        });
        data.results = response.results.map(function (item) {
            let result = item.user;
            common_table.forEach(function (key) {
                result[key] = item[key];
            });
            return result;
        });
        data.count = response.count;
        makeDataTable(data, id);

        $('.preloader').css('display', 'none');

        let paginationConfig = {
            container: ".partners__pagination",
            currentPage: page,
            pages: pages,
            callback: getPartners
        };
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(response.user_table);
        orderTable.sort(getPartners);
    });
}

function makeDepartmentList(selector, active = null) {
    return getDepartments().then(function (data) {
        let options = [];
        let department = data.results;
        department.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.title);
            if (active == item.id) {
                $(option).attr('selected', true);
            }
            options.push(option);
        });
        $(selector).html(options).prop('disabled', false).select2();
    });
}
function getChurchesListINDepartament(department_ids) {
    return new Promise(function (resolve, reject) {
        let url;
        if (department_ids instanceof Array) {
            url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/for_select/?`;
            let i = 0;
            department_ids.forEach(function (department_id) {
                i++;
                url += `department=${department_id}`;
                if (department_ids.length != i) {
                    url += '&';
                }
            })
        }
        let data = {
            url: url,
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
function getHomeGroupsINChurches(id) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/for_select/?church_id=${id}`,
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

function getHomeGroups(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/`,
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

function createCSV(data) {
    let filename = "";
    let disposition = data.getResponseHeader('Content-Disposition');
    if (disposition && disposition.indexOf('attachment') !== -1) {
        let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        let matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
    }
    let type = data.getResponseHeader('Content-Type') + ';charset=UTF-8';
    return {
        file: new Blob(["\ufeff" + data.responseText], {type: type, endings: 'native'}),
        filename: filename
    };
}

function exportTableData(el) {
    let _self = el;
    return new Promise(function (resolve, reject) {
        let url, filter, filterKeys, items, count;
        url = $(_self).attr('data-export-url');
        filter = getFilterParam();
        filterKeys = Object.keys(filter);
        if (filterKeys && filterKeys.length) {
            url += '?';
            items = filterKeys.length;
            count = 0;
            filterKeys.forEach(function (key) {
                count++;
                url += key + '=' + filter[key];
                if (count != items) {
                    url += '&';
                }
            })
        }
        let data = {
            url: url,
            method: 'POST',
            data: {
                fields: getDataTOExport().join(',')
            }
        };
        let status = {
            200: function (data, statusText, req) {
                // check for a filename
                let file = createCSV(req);
                if (typeof window.navigator.msSaveBlob !== 'undefined') {
                    // IE workaround for "HTML7007"
                    window.navigator.msSaveBlob(file.file, file.filename);
                } else {
                    let URL = window.URL || window.webkitURL;
                    let downloadUrl = URL.createObjectURL(file.file);

                    if (file.filename) {
                        // use HTML5 a[download] attribute to specify filename
                        let a = document.createElement("a");
                        // safari doesn't support this yet
                        if (typeof a.download === 'undefined') {
                            window.location = downloadUrl;
                        } else {
                            a.href = downloadUrl;
                            a.download = file.filename;
                            document.body.appendChild(a);
                            a.click();
                        }
                    } else {
                        window.location = downloadUrl;
                    }

                    setTimeout(function () {
                        URL.revokeObjectURL(downloadUrl);
                    }, 100); // cleanup
                    resolve(req);
                }
            }
        };
        newAjaxRequest(data, status, reject);
    });
}

function newAjaxRequest(data, codes, fail) {
    let resData = {
        method: 'GET'
    };
    Object.assign(resData, data);
    $.ajax(resData)
        .statusCode(codes)
        .fail(fail);
}

function getUsers(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
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

function getShortUsers(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/short_users/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
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

function getSummitUsers(summit_id, config = {}) {
    Object.assign(config, getFilterParam());
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/summits/${summit_id}/users/`,
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

function getPotencialSammitUsers(config) {
    console.log(config);
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_search/', config, function (data) {
            resolve(data);
        });
    });
}

function registerUserToSummit(config) {
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/post_anket/', config, function (JSONobj) {
        if (JSONobj.status) {
            showPopup(JSONobj.message);
            createSummitUsersTable();
            // getUnregisteredUsers();
            $("#send_email").prop("checked", false);
        } else {
            showPopup(JSONobj.message);
            $("#send_email").prop("checked", false);
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function getChurchUsers(id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${id}/users/`, null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}

function getChurchDetails(id, link, config) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${id}/${link}/`, config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}

function getHomeGroupUsers(config, id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/home_groups/${id}/users`, config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}

function saveUserData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.1/users/${id}/`, json, function (data) {
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
}

function saveChurchData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${id}/`, json, function (data) {
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
}

function saveHomeGroupsData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/home_groups/${id}/`, json, function (data) {
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
}

function saveHomeGroupsDataNew(data, id) {
    if (id) {
        let data = JSON.stringify(data);
        let options = {
        method: 'PATCH',
        credentials: "same-origin",
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
         body:  data

    };
        return fetch(`${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${id}/`, options)
            .then(res => res.json());

        // ajaxRequest(, json, function (data) {
        // }, 'PATCH', false, {
        //     'Content-Type': 'application/json'
        // });
    }
}

function deleteUserINHomeGroup(id, user_id) {
    return new Promise(function (resolve, reject) {
        let json = JSON.stringify({
            "user_id": user_id
        });
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/home_groups/${id}/del_user/`, json, function () {
            resolve();
        }, 'POST', false, {
            'Content-Type': 'application/json'
        });
    })
}

function deleteUserINChurch(id, user_id) {
    return new Promise(function (resolve, reject) {
        let json = JSON.stringify({
            "user_id": user_id
        });
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${id}/del_user/`, json, function () {
            resolve();
        }, 'POST', false, {
            'Content-Type': 'application/json'
        });
    })
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
    })
}

function createChurchesDetailsTable(config = {}, id, link) {
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
        console.log(id);
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
        $('.quick-edit').on('click', function () {
            let user_id = $(this).closest('.edit').find('a').data('id');
            deleteUserINChurch(id, user_id).then(function () {
                createChurchesDetailsTable(config, id, link);
            })
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        orderTable.sort(createChurchesDetailsTable);
    })
}

function createHomeGroupUsersTable(config = {}, id) {
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
        $('#tableUserINHomeGroups').html(rendered);
        $('.quick-edit').on('click', function () {
            let user_id = $(this).closest('.edit').find('a').data('id');
            deleteUserINHomeGroup(id, user_id).then(function () {
                createHomeGroupUsersTable(config, id);
            })
        });
        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createHomeGroupUsersTable
        };
        makePagination(paginationConfig);
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        orderTable.sort(createHomeGroupUsersTable);
    })
}

function addHomeGroupToDataBase(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/`,
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
        "church": {
            "id": parseInt($('#added_home_group_church').data('id'))
        },
        "leader": $('#added_home_group_pastor').val(),
        "city": $('#added_home_group_city').val(),
        "address": $('#added_home_group_address').val(),
        "phone_number": $('#added_home_group_phone').val(),
        "website": $('#added_home_group_site').val()
    }
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

function clearAddNewUser() {
    let form = $('#createUser');
    let flag = $('#addNewUserPopup').attr('data-flagdepart');
    form.find('#partner').attr('checked', false);
    form.find('.hidden-partner').hide();
    form.find('#edit-photo').attr('data-source', '').find('img').attr('src', '/static/img/no-usr.jpg');
    form.find('.anketa-photo').unbind('click');
    form.find('select:not(#payment_currency, #spir_level, #chooseDepartment).select2-hidden-accessible')
        .select2('destroy').find('option').remove();
    if (flag) {
        initAddNewUser({
            getDepartments: false,
        });
    } else {
        form.find('select#chooseDepartment').select2('destroy').find('option').remove();
        initAddNewUser();
    }
    form.find('#chooseResponsible, #chooseRegion, #chooseCity').attr('disabled', true);
    form.find('input').each(function () {
        $(this).val('');
    });
    form.find('#spir_level').select2('destroy').find('option').attr('selected', false)
                            .find('option:first-child').attr('selected', true);
}

function clearAddChurchData() {
    $('#added_churches_date').val(''),
        $('#added_churches_is_open').prop('checked', false),
        $('#added_churches_title').val(''),
        $('#added_churches_country').val(''),
        $('#added_churches_city').val(''),
        $('#added_churches_address').val(''),
        $('#added_churches_phone').val(''),
        $('#added_churches_site').val('')
}

function clearAddHomeGroupData() {
    $('#added_home_group_date').val(''),
        $('#added_home_group_title').val(''),
        $('#added_home_group_city').val(''),
        $('#added_home_group_address').val(''),
        $('#added_home_group_phone').val(''),
        $('#added_home_group_site').val('')
}

function createChurchesTable(config = {}) {
    config.search_title = $('input[name="fullsearch"]').val();
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getChurches(config).then(function (data) {
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
            ajaxRequest(`${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/${id}/`, null, function (data) {
                let quickEditCartTmpl, rendered;
                quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                rendered = _.template(quickEditCartTmpl)(data);
                $('#quickEditCartPopup .popup_body').html(rendered);
                $('#opening_date').datepicker({
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        orderTable.sort(createChurchesTable);
    });
}

function addChurchTODataBase(config) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/`,
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

function addChurch(e, el, callback) {
    e.preventDefault();
    let data = getAddChurchData();
    let json = JSON.stringify(data);
    addChurchTODataBase(json).then(function (data) {
        hidePopup(el);
        clearAddChurchData();
        callback();
        showPopup(`Церковь ${data.get_title} добавлена в базу`);
    }).catch(function (data) {
        hidePopup(el);
        showPopup('Ошибка при создании домашней группы');
    });
}

function getCountryCodes() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/countries/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    })
}

function getRegions(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/regions/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    })
}

function getCities(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/cities/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    })
}

function getPartnersList(data) {
    let config = {
        search: "",
        page: 1
    };
    Object.assign(config, data);
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/partnerships/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    })
}

function getCountries() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/countries/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

function getCountriesList() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/countries/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject('Ошибка');
            }
        })
    })
}

function getDepartments() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/departments/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject('Ошибка');
            }
        });
    });
}

function getStatuses() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/hierarchy/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

function getCurrentUser(id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/users/' + id + '/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        })
    })
}
function getResponsibleBYHomeGroup(userID = null) {
    let masterTree = (userID) ? userID : $('body').data('user');
    return new Promise(function (resolve, reject) {
        let url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/short_users/?master_tree=${masterTree}`;
        ajaxRequest(url, null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

function getResponsibleBYHomeGroupNew(config) {
    return new Promise(function (resolve, reject) {
        let url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/get_leaders_by_church/`;
        ajaxRequest(url, config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

function getResponsible(ids, level, search = "") {
    let responsibleLevel;
    if (level === 0 || level === 1) {
        responsibleLevel = level + 1;
    } else {
        responsibleLevel = level;
    }
    return new Promise(function (resolve, reject) {
        let url = CONFIG.DOCUMENT_ROOT + 'api/v1.0/short_users/?level_gte=' + responsibleLevel + '&search=' + search;
        if (ids instanceof Array) {
            ids.forEach(function (id) {
                url += '&department=' + id;
            });
        } else {
            url += '&department=' + ids;
        }
        ajaxRequest(url, null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

function getResponsibleStatuses() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/hierarchy/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

function getUsersFromDatabase(config) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/users/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

function getUsersTOChurch(config) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/churches/potential_users_church/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

function getUsersTOHomeGroup(config, id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${id}/potential_users_group/`, config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}

function getDivisions() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/divisions/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}

function getManagers() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/partnerships/simple/', null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject();
            }
        });
    });
}

function getIncompleteDeals(data) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/?done=false', data, function (response) {
            if (response) {
                resolve(response);
            } else {
                reject();
            }
        })
    })
}

function getFinishedDeals(data) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/?done=true', data, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject();
            }
        })
    })
}

function getOverdueDeals(data) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/?expired=true', data, function (response) {
            if (response) {
                resolve(response);
            } else {
                reject();
            }
        })
    })
}

function getPayment(id) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/deals/${id}/payments/`, null, function (data) {
            resolve(data);
        }, 'GET', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                reject();
                showPopup(data.detail)
            }
        })
    })
}

function getPaymentsDeals(config) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/payments/deal/`,
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

function makePayments(config = {}) {
    config.search_purpose_fio = $('input[name=fullsearch]').val();
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    return getPaymentsDeals(config).then(function (response) {
            console.log(config);
            let page = config['page'] || 1;
            let count = response.count;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let data = {};
            let id = "paymentsList";
            let text = `Показано ${CONFIG.pagination_count} из ${count}`;

            data.count = response.count;
            data.table_columns = {};
            data.table_columns.sent_date = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'sent_date',
                title: 'Дата отправки'
            };
            data.table_columns.sum_str = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'sum',
                title: 'Сумма'
            };
            data.table_columns.manager = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'manager__last_name',
                title: 'Менеджер'
            };
            data.table_columns.description = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'no_ordering',
                title: 'Примечание'
            };
            data.table_columns.purpose_fio = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'no_ordering',
                title: 'Плательщик'
            };
            data.table_columns.purpose_date = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'no_ordering',
                title: 'Дата сделки'
            };
            data.table_columns.purpose_manager_fio = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'no_ordering',
                title: 'Ответственный'
            };
            data.table_columns.created_at = {
                active: true,
                editable: true,
                id: '',
                number: '',
                ordering_title: 'created_at',
                title: 'Дата создания'
            };
            data.results = response.results;
            makePaymentsTable(data, id);

            let paginationConfig = {
                container: ".payments__pagination",
                currentPage: page,
                pages: pages,
                callback: makePayments
            };
            makePagination(paginationConfig);
            $('.table__count').text(text);
            // makeSortForm(response.user_table);
            orderTable.sort(makePayments);
            $('.preloader').hide();
            return data;
        }
    )
        ;
}
function homeStatistics() {
    getData('/api/v1.0/events/home_meetings/statistics/', getFilterParam()).then(data => {
        let tmpl = document.getElementById('statisticsTmp').innerHTML;
        let rendered = _.template(tmpl)(data);
        document.getElementById('statisticsContainer').innerHTML = rendered;
    })
}

function makePagination(config) {
    let container = document.createElement('div'),
        input = document.createElement('input'),
        text = document.createElement('span'),
        doubleLeft = document.createElement('a'),
        doubleRight = document.createElement('a'),
        left = document.createElement('a'),
        right = document.createElement('a');
    $(input).attr({
        "type": "number",
        "max": config.pages,
        "min": 1
    });
    $(doubleLeft).addClass('double__left').append('<i class="fa fa-angle-double-left" aria-hidden="true"></i>');
    $(doubleLeft).on('click', function () {
        $(this).closest('.pagination').find('.pagination__input').val(1).trigger('change');
    });
    $(left).addClass('left').append('<i class="fa fa-angle-left" aria-hidden="true"></i>');
    $(left).on('click', function () {
        let val = parseInt($(this).closest('.pagination').find('.pagination__input').val());
        if (!!(val - 1)) {
            $(this).closest('.pagination').find('.pagination__input').val(val - 1).trigger('change');
        }
    });
    $(doubleRight).addClass('double__right').append('<i class="fa fa-angle-double-right" aria-hidden="true"></i>');
    $(doubleRight).on('click', function () {
        $(this).closest('.pagination').find('.pagination__input').val(config.pages).trigger('change');
    });
    $(right).addClass('right').append('<i class="fa fa-angle-right" aria-hidden="true"></i>');
    $(right).on('click', function () {
        let val = parseInt($(this).closest('.pagination').find('.pagination__input').val());
        if (!(val + 1 > config.pages)) {
            $(this).closest('.pagination').find('.pagination__input').val(val + 1).trigger('change');
        }
    });

    $(input).addClass('pagination__input').val(config.currentPage);
    $(text).addClass('text').text(`из ${config.pages}`);
    $(container).append(doubleLeft).append(left).append(input).append(text).append(right).append(doubleRight);

    $(container).find('.pagination__input').change(function () {
        let val = parseInt($(this).val());
        if (val <= 0) {
            $(container).find('.pagination__input').val(1).trigger('change');
            return
        }
        if (val > config.pages) {
            $(container).find('.pagination__input').val(config.pages).trigger('change');
            return
        }
        if (config.hasOwnProperty('id')) {
            config.callback({
                page: val
            }, config.id);
        } else {
            config.callback({
                page: val
            });
        }

    });
    $(config.container).html(container);
}

function delCookie(name) {
    setCookie(name, "", {
        expires: -1
    })
}

function isElementExists(element) {
    if (typeof(element) != 'undefined' && element != null) {
        return true;
    }
}

function getLastId(url) {
    if (!url) {
        url = document.location.href
    }
    let id = url.split('/');
    if (id[id.length - 1]) {
        return id[id.length - 1]
    }
    return id[id.length - 2]
}

function getCookie(cookieName) {
    let cookieValue = document.cookie;
    let cookieStart = cookieValue.indexOf(" " + cookieName + "=");
    if (cookieStart == -1) {
        cookieStart = cookieValue.indexOf(cookieName + "=");
    }
    if (cookieStart == -1) {
        cookieValue = null;
    } else {
        cookieStart = cookieValue.indexOf("=", cookieStart) + 1;
        let cookieEnd = cookieValue.indexOf(";", cookieStart);
        if (cookieEnd == -1) {
            cookieEnd = cookieValue.length;
        }
        cookieValue = unescape(cookieValue.substring(cookieStart, cookieEnd));
    }
    return cookieValue;
}

Array.prototype.unique = function () {
    let a = this.concat();
    for (let i = 0; i < a.length; ++i) {
        for (let j = i + 1; j < a.length; ++j) {
            if (a[i] === a[j])
                a.splice(j--, 1);
        }
    }
    return a;
};

let delay = (function () {
    let timer = 0;
    return function (callback, ms) {
        clearTimeout(timer);
        timer = setTimeout(callback, ms);
    };
})();

// jquery alternative
function indexInParent(node) {
    let children = node.parentNode.childNodes;
    let num = 0;
    for (let i = 0; i < children.length; i++) {
        if (children[i] == node) return num;
        if (children[i].nodeType == 1) num++;
    }
    return -1;
}

function getRussianMonth(index) {
    let month = new Array(12);
    month[0] = "Январь";
    month[1] = "Февраль";
    month[2] = "Март";
    month[3] = "Апрель";
    month[4] = "Май";
    month[5] = "Июнь";
    month[6] = "Июль";
    month[7] = "Август";
    month[8] = "Сентябрь";
    month[9] = "Октябрь";
    month[10] = "Ноябрь";
    month[11] = "Декабрь";

    return month[index] || ''
}

//tab plugin v_1
function tab_plugin() {
    let el = document.getElementById('tab_plugin');
    if (!el) {
        return;
    }

    Array.prototype.forEach.call(document.querySelectorAll("#tab_plugin li"), function (el) {
        el.addEventListener('click', function (e) {
            e.preventDefault();
            let index = indexInParent(el);
            Array.prototype.forEach.call(document.querySelectorAll("#tab_plugin li"), function (el) {
                el.classList.remove('current')
            });
            Array.prototype.forEach.call(document.querySelectorAll("[data-tab-body]"), function (el) {
                el.style.display = 'none'
            });

            this.classList.add('current');

            let tab = document.querySelectorAll("[data-tab-body]")[index];
            if (tab) {
                tab.style.display = 'block';
            }
        });
    });
}

// Counter counterNotifications
function counterNotifications() {
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/notifications/today/', null, function (data) {
        $('.sms').attr('data-count', data.count);
    });
}

function ajaxRequest(url, data, callback, method, withCredentials, headers, statusCode) {
    withCredentials = withCredentials !== false;
    method = method || 'GET';
    data = data || {};
    headers = headers || {};
    statusCode = statusCode || {};
    $.ajax({
        url: url,
        data: data,
        type: method,
        success: callback,
        xhrFields: {
            withCredentials: withCredentials
        },
        statusCode: statusCode,
        headers: headers
    });
}

function showPopup(text, title) {
    text = text || '';
    title = title || 'Информационное сообщение';
    let popup = document.getElementById('create_pop');
    if (popup) {
        popup.parentElement.removeChild(popup)
    }
    let div = document.createElement('div');

    let html = '<div class="pop_cont" >' +
        '<div class="top-text"><h3>' + title + '</h3><span id="close_pop">×</span></div>' +
        '<div class="main-text"><p>' + text + '</p></div>' +
        '</div>';
    div.className = "pop-up-universal";
    div.innerHTML = html;
    div.id = "create_pop";

    document.body.appendChild(div);

    $('#close_pop').on('click', function () {
        $('.pop-up-universal').css('display', 'none').remove();
    });
}

function showPopupAddUser(data) {

    let tmpl = document.getElementById('addUserSuccessPopup').innerHTML;
    let rendered = _.template(tmpl)(data);
    $('body').append(rendered);

    $('#addPopup').find('.close').on('click', function () {
        $('#addPopup').css('display', 'none').remove();
    });
    $('#addPopup').find('.addMore').on('click', function () {
        $('#addPopup').css('display', 'none').remove();
        $('body').addClass('no_scroll');
        $('#addNewUserPopup').find('form').css("transform","translate3d(0px, 0px, 0px)");
        $('#addNewUserPopup').css('display', 'block');
        clearAddNewUser();
    });
}

function showPopupHTML(block) {
    let popup = document.createElement('div');
    popup.className = "pop-up-universal";
    $(popup).append(block);
    $('body').append(popup);

    $('#close_pop').on('click', function () {
        $(popup).hide().remove();
    });
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    url = url.toLowerCase(); // This is just to avoid case sensitiveness
    name = name.replace(/[\[\]]/g, "\\$&").toLowerCase();// This is just to avoid case sensitiveness for query parameter name
    let regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function getCorrectValue(value) {
    if (value === null) {
        return '';
    } else {
        if (value instanceof Array) {
            let str_value = [];
            value.forEach(function (v) {
                str_value = str_value.concat(getCorrectValue(v))
            });
            return str_value.join(', ')
        } else if (value instanceof Object) {
            let id = '';
            let new_value = '';
            for (let k in value) {
                if (k === 'id') {
                    id = value['id'];
                } else {
                    new_value = value[k]
                }
            }
            return '<span data-id="' + id + '">' + new_value + '</span>'
        }
    }
    return value
}

function ajaxSendFormData(data = {}) {
    let sendData = {
        method: 'POST'
    };
    Object.assign(sendData, data);
    return new Promise(function (resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open(sendData.method, sendData.url, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    let response = JSON.parse(xhr.responseText);
                    resolve(response);
                } else if (xhr.status == 201) {
                    let response = JSON.parse(xhr.responseText);
                    resolve(response);
                } else if (xhr.status == 400) {
                    let response = JSON.parse(xhr.responseText);
                    reject(response);
                } else if (xhr.status == 404) {
                    reject("У вас нет прав для редактирования");
                } else {
                    reject(xhr.responseText);
                }
            }
        };
        xhr.send(sendData.data);
    });
}

function dataURLtoBlob(dataurl) {
    let arr = dataurl.split(',');
    let mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type: mime});
}

function ucFirst(str) {
    // только пустая строка в логическом контексте даст false
    if (!str) return str;

    return str[0].toUpperCase() + str.slice(1);
}

function makeCountriesList(data, selectCountry) {
    let rendered = [];
    let option = document.createElement('option');
    $(option).val('').text('Выберите страну').attr('disabled', true).attr('selected', true);
    rendered.push(option);
    data.forEach(function (item) {
        let option = document.createElement('option');
        $(option).val(item.title).text(item.title).attr('data-id', item.id);
        if (item.title == selectCountry) {
            $(option).attr('selected', true);
        }
        rendered.push(option);
    });
    return rendered
}

function makeRegionsList(data, selectRegion) {
    let rendered = [];
    let option = document.createElement('option');
    $(option).val('').text('Выберите регион').attr('disabled', true).attr('selected', true);
    rendered.push(option);
    data.forEach(function (item) {
        let option = document.createElement('option');
        $(option).val(item.title).text(item.title).attr('data-id', item.id);
        if (item.title == selectRegion) {
            $(option).attr('selected', true);
        }
        rendered.push(option);
    });
    return rendered
}

function makeCityList(data, selectCity) {
    let rendered = [];
    let option = document.createElement('option');
    $(option).val('').text('Выберите город').attr('disabled', true).attr('selected', true);
    rendered.push(option);
    data.forEach(function (item) {
        let option = document.createElement('option');
        $(option).val(item.title).text(item.title).attr('data-id', item.id);
        if (item.title == selectCity) {
            $(option).attr('selected', true);
        }
        rendered.push(option);
    });
    return rendered
}

function initLocationSelect(config) {
    let $countrySelector = $('#' + config.country);
    let $regionSelector = $('#' + config.region);
    let $citySelector = $('#' + config.city);
    let selectCountry = $countrySelector.val();
    let selectRegion = $regionSelector.val();
    let selectCity = $citySelector.val();
    getCountries().then(function (data) {
        if (typeof data == "object") {
            let list = makeCountriesList(data, selectCountry);
            $countrySelector.html(list);
        }
        return $countrySelector.find(':selected').data('id');
    }).then(function (id) {
        if (!selectCountry || !id) return null;
        let config = {};
        config.country = id;
        getRegions(config).then(function (data) {
            if (typeof data == "object") {
                let list = makeRegionsList(data, selectRegion);
                $regionSelector.html(list);
            }
            return $regionSelector.find(':selected').data('id')
        }).then(function (id) {
            if (!selectRegion || !id) return null;
            let config = {};
            config.region = id;
            getCities(config).then(function (data) {
                if (typeof data == "object") {
                    let list = makeCityList(data, selectCity);
                    $citySelector.html(list);
                }
            });
        })
    });
    $countrySelector.on('change', function () {
        let config = {};
        config.country = $countrySelector.find(':selected').data('id');
        selectCountry = $countrySelector.find(':selected').val();
        getRegions(config).then(function (data) {
            let list = makeRegionsList(data, selectRegion);
            $regionSelector.html(list);
        }).then(function () {
            $citySelector.html('');
        })
    });
    $regionSelector.on('change', function () {
        let config = {};
        config.region = $regionSelector.find(':selected').data('id');
        selectRegion = $regionSelector.find(':selected').val();
        getCities(config).then(function (data) {
            let list = makeCityList(data, selectCity);
            $citySelector.html(list);
        })
    });
}

function createSummitUsersTable(data = {}) {
    let page = data.page || $('.pagination__input').val();
    let summitId = data.summit || $('#summitsTypes').find('.active').data('id');
    let config = {
        page: page,
        search_fio: $('input[name="fullsearch"]').val()
    };
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
        orderTable.sort(createSummitUsersTable);
    });
}

function makeDataTable(data, id) {
    let tmpl = document.getElementById('databaseUsers').innerHTML;
    let rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        makeQuickEditCart(this);
    })
}

function makePaymentsTable(data, id) {
    let tmpl = document.getElementById('databasePayments').innerHTML;
    let rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        // makeQuickEditPayments(this);
    })
}

function makeSammitsDataTable(data, id) {
    var tmpl = document.getElementById('databaseUsers').innerHTML;
    var rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        makeQuickEditSammitCart(this);
    })
}

function makeSortForm(data) {
    let sortFormTmpl, obj, rendered;
    sortFormTmpl = document.getElementById("sortForm").innerHTML;
    obj = {};
    obj.user = [];
    obj.user.push("");
    obj.user.push(data);
    rendered = _.template(sortFormTmpl)(obj);
    document.getElementById('sort-form').innerHTML = rendered;
    $("#sort-form").sortable({revert: true, items: "li:not([disable])", scroll: false});
}

function makeResponsibleList() {
    let department = $('#departmentSelect').val();
    console.log(department);
    let hierarchy = $('#hierarchySelect option:selected').attr('data-level');
    getResponsible(department, hierarchy).then(function (data) {
        let id = $('#master_hierarchy option:selected').attr('data-id');
        if (!id) {
            id = $('#master_hierarchy option').attr('data-id');
        }
        let selected = false;
        let html = "";
        data.forEach(function (el) {
            if (id == el.id) {
                selected = true;
                html += "<option value='" + el.id + "' data-id='" + el.id + "' selected>" + el.fullname + "</option>";
            } else {
                html += "<option value='" + el.id + "' data-id='" + el.id + "'>" + el.fullname + "</option>";
            }
        });
        if (!selected) {
            html += "<option selected disabled value=''>Выберите ответственного</option>";
        }
        html += "";
        $("#master_hierarchy").html(html).select2();
    });
}

function makeChooseDivision() {
    return getDivisions().then(function (data) {
        data = data.results;
        let html = '';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        return html
    });
}

function initAddNewUser(config = {}) {
    let configDefault = {
        getCountries: true,
        getDepartments: true,
        getStatuses: true,
        getDivisions: true,
        getCountryCodes: true,
        getManagers: true,
    };
    let $form = $('#createUser'),
        $input = $form.find('input');
    $input.each(function () {
        $(this).val('');
    });
    Object.assign(configDefault, config);
    if (configDefault.getCountries) {
        getCountries().then(function (data) {
            let rendered = [];
            let option = document.createElement('option');
            $(option).val('').text('Выберите страну').attr('disabled', true).attr('selected', true);
            rendered.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.title).text(item.title).attr('data-id', item.id);
                rendered.push(option);
            });
            $('#chooseCountry').html(rendered).on('change', function () {
                let config = {};
                config.country = $(this).find(':selected').data('id');
                getRegions(config).then(function (data) {
                    let rendered = [];
                    let option = document.createElement('option');
                    $(option).val('').text('Выберите регион');
                    rendered.push(option);
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.title).text(item.title).attr('data-id', item.id);
                        rendered.push(option);
                    });
                    $('#chooseRegion').html(rendered).attr('disabled', false).on('change', function () {
                        let config = {};
                        config.region = $(this).find(':selected').data('id');
                        getCities(config).then(function (data) {
                            let rendered = [];
                            let option = document.createElement('option');
                            $(option).val('').text('Выберите город');
                            rendered.push(option);
                            data.forEach(function (item) {
                                let option = document.createElement('option');
                                $(option).val(item.title).text(item.title).attr('data-id', item.id);
                                rendered.push(option);
                            });
                            $('#chooseCity').html(rendered).attr('disabled', false).select2();
                        })
                    }).select2();
                })
            }).select2();
        });
    }
    if (configDefault.getDepartments) {
        getDepartments().then(function (data) {
            let departments = data.results;
            let rendered = [];
            let option = document.createElement('option');
            // $(option).text('Выберите департамент').attr('disabled', true).attr('selected', true);
            // rendered.push(option);
            departments.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.title);
                rendered.push(option);
            });
            $('#chooseDepartment').html(rendered).select2().removeAttr('disabled').on('change', function () {
                let status = $('#chooseStatus').find('option').filter(':selected').data('level');
                let department = $(this).val();
                getResponsible(department, status).then(function (data) {
                    let rendered = [];
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        rendered.push(option);
                    });
                    $('#chooseResponsible').html(rendered).attr('disabled', false).select2();
                })
            });
        });
    } else {
        $('#addNewUserPopup').attr('data-flagdepart', true);
    }
    if (configDefault.getStatuses) {
        getStatuses().then(function (data) {
            let statuses = data;
            let rendered = [];
            let option = document.createElement('option');
            $(option).text('Выберите статус').attr('disabled', true).attr('selected', true);
            rendered.push(option);
            statuses.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).attr('data-level', item.level).text(item.title);
                rendered.push(option);
            });
            return rendered;
        }).then(function (rendered) {
            $('#chooseStatus').html(rendered).select2().on('change', function () {
                let status = $(this).find('option').filter(':selected').data('level');
                let department = $('#chooseDepartment').val();
                getResponsible(department, status).then(function (data) {
                    let rendered = [];
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        rendered.push(option);
                    });
                    $('#chooseResponsible').html(rendered).attr('disabled', false).select2();
                })
            });
        });
    }
    if (configDefault.getDivisions) {
        getDivisions().then(function (data) {
            let divisions = data.results;
            let rendered = [];
            divisions.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.title);
                rendered.push(option);
            });
            $('#chooseDivision').html(rendered).select2();
        });
    }
    if (configDefault.getCountryCodes) {
        getCountryCodes().then(function (data) {
            let codes = data;
            let rendered = [];
            codes.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.phone_code).text(item.title + ' ' + item.phone_code);
                if (item.phone_code == '+38') {
                    $(option).attr('selected', true);
                }
                rendered.push(option);
            });
            $('#chooseCountryCode').html(rendered).on('change', function () {
                let code = $(this).val();
                $('#phoneNumberCode').val(code);
            }).trigger('change');
        });
    }
    if (configDefault.getManagers) {
        getManagers().then(function (data) {
            let rendered = [];
            let option = document.createElement('option');
            $(option).val('').text('Выберите менеджера').attr('disabled', true).attr('selected', true);
            rendered.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                rendered.push(option);
            });
            $('#chooseManager').html(rendered).select2();
        });
    }

    $('#spir_level').select2();

    $('#repentance_date').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#partnerFrom').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#bornDate').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#chooseCountryCode').select2();

    $('#partner').on('change', function () {
        let partner = $(this).is(':checked');
        if (partner) {
            $('.hidden-partner').css('display', 'block');
        } else {
            $('.hidden-partner').css('display', 'none');
        }
    });
}

function saveUser(el) {
    let $input, $select, fullName, first_name, last_name, middle_name, departments, hierarchy, phone_number, data, id;
    let send = true;
    let $department = $($(el).closest('.pop_cont').find('#departmentSelect'));
    departments = $department.val();
    let $hierarchy = $($(el).closest('.pop_cont').find('#hierarchySelect'));
    hierarchy = $hierarchy.val();
    let $master = $('#master_hierarchy');
    let master_id = $master.val() || "";
    let $fullname = $($(el).closest('.pop_cont').find('input.fullname'));
    fullName = $fullname.val().split(' ');
    let $phone_number = $($(el).closest('.pop_cont').find('#phone_number'));
    phone_number = $phone_number.val();
    if (!$fullname.val()) {
        $fullname.css('border-color', 'red');
        send = false;
    } else {
        $fullname.removeAttr('style');
    }
    if (!master_id) {
        $('label[for="master_hierarchy"]').css('color', 'red');
        send = false;
    } else {
        $('label[for="master_hierarchy"]').removeAttr('style');
    }
    if (!phone_number) {
        $phone_number.css('border-color', 'red');
        send = false;
    } else {
        $phone_number.removeAttr('style');
    }
    if (!send) {
        return
    }
    first_name = fullName[1];
    last_name = fullName[0];
    middle_name = fullName[2] || "";
    data = {
        email: $($(el).closest('.pop_cont').find('#email')).val(),
        first_name: first_name,
        last_name: last_name,
        middle_name: middle_name,
        hierarchy: hierarchy,
        departments: departments,
        master: master_id,
        skype: $($(el).closest('.pop_cont').find('#skype')).val(),
        phone_number: phone_number,
        extra_phone_numbers: _.filter(_.map($($(el).closest('.pop_cont').find('#extra_phone_numbers')).val().split(","), x => x.trim()), x => !!x),
        repentance_date: $($(el).closest('.pop_cont').find('#repentance_date')).val() || null,
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        region: $($(el).closest('.pop_cont').find('#region')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val()
    };
    id = $(el).closest('.pop_cont').find('img').attr('alt');
    saveUserData(data, id);
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
}

function saveChurches(el) {
    let $input, $select, phone_number, opening_date, data, id;
    id = parseInt($($(el).closest('.pop_cont').find('#churchID')).val());
    opening_date = $($(el).closest('.pop_cont').find('#opening_date')).val();
    if (!opening_date && opening_date.split('-').length !== 3) {
        $($(el).closest('.pop_cont').find('#opening_date')).css('border-color', 'red');
        return
    }
    data = {
        title: $($(el).closest('.pop_cont').find('#church_title')).val(),
        pastor: $($(el).closest('.pop_cont').find('#editPastorSelect')).val(),
        department: $($(el).closest('.pop_cont').find('#editDepartmentSelect')).val(),
        phone_number: $($(el).closest('.pop_cont').find('#phone_number')).val(),
        website: ($(el).closest('.pop_cont').find('#web_site')).val(),
        opening_date: $($(el).closest('.pop_cont').find('#opening_date')).val() || null,
        is_open: $('#is_open_church').is(':checked'),
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        region: $($(el).closest('.pop_cont').find('#region')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val()
    };
    saveChurchData(data, id);
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
}

function saveHomeGroups(el) {
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

    saveHomeGroupsData(data, id);
    saveHomeGroupsDataNew(data, id);

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
}

function makeQuickEditSammitCart(el) {
    let anketID, id, link, url;
    anketID = $(el).closest('td').find('a').data('ankets');
    id = $(el).closest('td').find('a').data('id');
    link = $(el).closest('td').find('a').data('link');
    url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/summit_ankets/${anketID}/`;
    ajaxRequest(url, null, function (data) {
        $('#fullNameCard').text(data.full_name);
        $('#userDescription').val(data.description);
        $('#summit-valueDelete').val(data.total_sum);
        $('#member').prop("checked", data.is_member);
        $('#userID').val(data.user_id);
        $('#preDeleteAnket').attr('data-id', data.user_id).attr('data-anket', data.id);
        $('#popupParticipantInfo').css('display', 'block');
    }, 'GET', true, {
        'Content-Type': 'application/json'
    });
}

function makeQuickEditCart(el) {
    let id, link, url;
    id = $(el).closest('td').find('a').attr('data-id');
    link = $(el).closest('td').find('a').attr('data-link');
    url = `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/${id}/`;
    ajaxRequest(url, null, function (data) {
        let quickEditCartTmpl, rendered;
        quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
        rendered = _.template(quickEditCartTmpl)(data);
        $('.save-user').attr('disabled', false);
        $('#quickEditCartPopup').find('.popup_body').html(rendered);
        $('#quickEditCartPopup').css('display', 'block');
        makeResponsibleList();
        getStatuses().then(function (data) {
            data = data.results;
            let hierarchySelect = $('#hierarchySelect').val();
            let html = "";
            for (let i = 0; i < data.length; i++) {
                if (hierarchySelect === data[i].title || hierarchySelect == data[i].id) {
                    html += '<option value="' + data[i].id + '"' + 'selected' + ' data-level="' + data[i].level + '">' + data[i].title + '</option>';
                } else {
                    html += '<option value="' + data[i].id + '" data-level="' + data[i].level + '" >' + data[i].title + '</option>';
                }
            }
            $('#hierarchySelect').html(html);
        });
        getDepartments().then(function (data) {
            data = data.results;
            let departmentSelect = $('#departmentSelect').val();
            let html = "";
            for (let i = 0; i < data.length; i++) {
                if (departmentSelect.indexOf("" + data[i].title) != -1 || departmentSelect.indexOf("" + data[i].id) != -1) {
                    html += '<option value="' + data[i].id + '"' + 'selected' + '>' + data[i].title + '</option>';
                } else {
                    html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
                }
            }
            $('#departmentSelect').html(html);
        });

        $('#departmentSelect').on('change', makeResponsibleList);
        $('#hierarchySelect').on('change', makeResponsibleList);

        $("#repentance_date").datepicker({
            dateFormat: "yyyy-mm-dd"
        })
    }, 'GET', true, {
        'Content-Type': 'application/json'
    });
}

function setCookie(name, value, options) {
    options = options || {};
    let expires = options.expires;
    if (typeof expires == "number" && expires) {
        let d = new Date();
        d.setTime(d.getTime() + expires * 1000);
        expires = options.expires = d;
    }
    if (expires && expires.toUTCString) {
        options.expires = expires.toUTCString();
    }

    value = encodeURIComponent(value);

    let updatedCookie = name + "=" + value;

    for (let propName in options) {
        updatedCookie += "; " + propName;
        let propValue = options[propName];
        if (propValue !== true) {
            updatedCookie += "=" + propValue;
        }
    }
    document.cookie = updatedCookie;
}

function createUsersTable(config) {
    config["search_fio"] = $('input[name=fullsearch]').val();
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getUsers(config).then(function (data) {
        let count = data.count;
        let page = config['page'] || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
        let id = "database_users";
        let text = `Показано ${showCount} из ${count}`;
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createUsersTable
        };
        makeDataTable(data, id);
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.user_table);
        $('.preloader').css('display', 'none');
        orderTable.sort(createUsersTable);
    }).catch(function (err) {
        console.log(err);
    });
}

function updateSettings(callback, path) {
    let data = [];
    let iteration = 1;
    $("#sort-form input").each(function () {
        if ($(this).data('editable')) {
            let item = {};
            item['id'] = $(this).val();
            item['number'] = ++iteration;
            item['active'] = $(this).prop('checked');
            data.push(item);
        }
    });
    let json = JSON.stringify(data);

    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/update_columns/', json, function (JSONobj) {
        $(".bgsort").remove();
        VOCRM['column_table'] = JSONobj['column_table'];

        if (callback) {
            let param = {};
            if (path !== undefined) {
                let extendParam = $.extend({}, param, getFilterParam());
                callback(extendParam);
            } else {
                let param = getFilterParam();
                callback(param);
            }
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function getDataTOExport() {
    let $fealds = $('#sort-form').find('input');
    let filter = [];
    $fealds.each(function () {
        if ($(this).is(':checked')) {
            filter.push($(this).prop('id'))
        }
    });
    return filter;
}
function closePopup(el) {
    $(el).closest('.pop-up-splash').hide();
}

function hidePopup(el) {
    if ($(el).closest('.popap').find('.save-user').length) {
        $(el).closest('.popap').find('.save-user').attr('disabled', false);
        $(el).closest('.popap').find('.save-user').text('Сохранить');
    }
    $(el).closest('.popap').css('display', 'none');
}

function refreshFilter(el) {
    let $input = $(el).closest('.popap').find('input');
    $(el).addClass('refresh');
    setTimeout(function () {
        $(el).removeClass('refresh');
    }, 700);
    $input.each(function () {
        $(this).val('')
    })
}

function getFilterParam() {
    let $filterFields, data = {};
    $filterFields = $('#filterPopup select, #filterPopup input');
    $filterFields.each(function () {
        if ($(this).val() == "ВСЕ") {
            return
        }
        let prop = $(this).data('filter');
        if (prop) {
            if ($(this).attr('type') === 'checkbox') {
                data[prop] = ucFirst($(this).is(':checked').toString());
            } else {
                if ($(this).val()) {
                    data[prop] = $(this).val();
                }
            }
        }
    });
    if ('master_tree' in data && ('pastor' in data || 'master' in data || 'leader' in data)) {
        delete data.master_tree;
    }
    return data;
}

function filterParam() {
    let data = getFilterParam();
    return data;
}

function applyFilter(el, callback) {
    let self = el, data;
    data = getFilterParam();
    $('.preloader').css('display', 'block');
    callback(data);
    setTimeout(function () {
        hidePopup(self);
    }, 300);
}

function makeTabs(page = 0) {
    let pos = 0,
        tabs = document.getElementById('tabs'),
        tabsContent = document.getElementsByClassName('tabs-cont');

    for (let i = 0; i < tabs.children.length; i++) {
        tabs.children[i].setAttribute('data-page', pos);
        pos++;
    }

    showPage(page);

    tabs.onclick = function (event) {
        event.preventDefault();
        return showPage(parseInt(event.target.parentElement.getAttribute("data-page")));
    };

    function showPage(i) {
        for (let k = 0; k < tabsContent.length; k++) {
            tabsContent[k].style.display = 'none';
            tabs.children[k].classList.remove('current');
        }
        tabsContent[i].style.display = 'block';
        tabs.children[i].classList.add('current');

        let done = document.getElementById('period_done'),
            expired = document.getElementById('period_expired'),
            unpag = document.querySelectorAll('.undone-pagination'),
            expag = document.querySelectorAll('.expired-pagination'),
            dpag = document.querySelectorAll('.done-pagination');

        if (document.querySelectorAll('a[href="#overdue"]')[0].parentElement.classList.contains('current')) {
            done.style.display = 'none';
            expired.style.display = 'block';
            Array.prototype.forEach.call(expag, function (el) {
                el.style.display = 'block';
            });
            Array.prototype.forEach.call(unpag, function (el) {
                el.style.display = 'none';
            });
            Array.prototype.forEach.call(dpag, function (el) {
                el.style.display = 'none';
            });
        } else if (document.querySelectorAll('a[href="#completed"]')[0].parentElement.classList.contains('current')) {
            done.style.display = 'block';
            expired.style.display = '';
            Array.prototype.forEach.call(expag, function (el) {
                el.style.display = 'none';
            });
            Array.prototype.forEach.call(unpag, function (el) {
                el.style.display = 'none';
            });
            Array.prototype.forEach.call(dpag, function (el) {
                el.style.display = 'block';
            });
        } else if (document.querySelectorAll('a[href="#incomplete"]')[0].parentElement.classList.contains('current')) {
            done.style.display = '';
            expired.style.display = '';
            Array.prototype.forEach.call(expag, function (el) {
                el.style.display = 'none';
            });
            Array.prototype.forEach.call(unpag, function (el) {
                el.style.display = 'block';
            });
            Array.prototype.forEach.call(dpag, function (el) {
                el.style.display = 'none';
            });
        }
    }
}
function homeReportsTable(config = {}) {
    let status = $('#statusTabs').find('.current').find('button').data('status');
    let search = $('.search').find('input[name=fullsearch]').val();
    config.status = status;
    config.search_title = search;
    Object.assign(config, getFilterParam());
    getHomeReports(config).then(data => {
        makeHomeReportsTable(data, config);
    })
}

function makeHomeReportsTable(data, config = {}) {
    console.log(config);
    let tmpl = $('#databaseHomeReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: homeReportsTable
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('.table__count').text(text);
    orderTable.sort(homeReportsTable);
    $('.preloader').hide();
}

function getHomeReports(config = {}) {
    if (!config.status) {
        let status = parseInt($('#statusTabs').find('.current').find('button').data('status'));
        config.status = status || 1;
    }
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/`,
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
function createNewUser(callback) {
    let $createUser = $('#createUser'),
        $phoneNumber = $('#phoneNumber'),
        $extraPhoneNumbers = $('#extra_phone_numbers'),
        $preloader = $('.preloader');

    let oldForm = document.forms.createUser;
    let formData = new FormData(oldForm);
    // if ($('#division_drop').val()) {
    //     formData.append('divisions', JSON.stringify($('#chooseDivision').val()));
    // } else {
    //     formData.append('divisions', JSON.stringify([]));
    // }
    let divisions = $('#chooseDivision').val() || [];
    formData.append('divisions', JSON.stringify(divisions));

    let spirLevel = $('#spir_level').val() || null;
    if (spirLevel !== 'Выберите духовный уровень') {
        formData.append('spiritual_level', spirLevel);
    }

    formData.append('departments', JSON.stringify($('#chooseDepartment').val()));
    if ($phoneNumber.val()) {
        let phoneNumber = $('#phoneNumberCode').val() + $phoneNumber.val();
        formData.append('phone_number', phoneNumber)
    }
    if ($extraPhoneNumbers.val()) {
        formData.append('extra_phone_numbers', JSON.stringify($extraPhoneNumbers.val().split(',').map((item) => item.trim())));
    } else {
        formData.append('extra_phone_numbers', JSON.stringify([]));
    }
    if ($('#partner').is(':checked')) {
        let partner = {};
        partner.value = parseInt($('#val_partnerships').val()) || 0;
        partner.currency = parseInt($('#payment_currency').val());
        partner.date = $('#partnerFrom').val() || null;
        partner.responsible = parseInt($("#chooseManager").val());
        formData.append('partner', JSON.stringify(partner));
    }
    let send_image = $('#file').prop("files").length || false;
    if (send_image) {
        try {
            let blob;
            blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
            formData.append('image', blob, 'logo.jpg');
            formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
        } catch (err) {
            console.log(err);
        }
    }
    let url = `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/`;
    let config = {
        url: url,
        data: formData,
        method: 'POST'
    };
    $preloader.css('display', 'block');
    return ajaxSendFormData(config).then(function (data) {
        $preloader.css('display', 'none');
        // showPopup(`${data.fullname} добален(а) в базу данных`);
        showPopupAddUser(data);
        $createUser.find('input').each(function () {
            $(this).val('').attr('disabled', false);
        });
        //Пересмотреть ф-цию очистки
        $createUser.find('.cleared').each(function () {
            $(this).find('option').eq(0).prop('selected', true).select2()
        });
        $('#addNewUserPopup').css('display', 'none');
        if (callback != null) {
            callback(data);
        }
    }).catch(function (data) {
        $preloader.css('display', 'none');
        showPopup(data.message[0]);
    });

}

function createPayment(data, id) {
    let resData = {
        method: 'POST',
        url: `${CONFIG.DOCUMENT_ROOT}api/v1.1/partnerships/${id}/create_payment/`
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

function getChurchStats(id) {
    let resData = {
        url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/${id}/statistics/`
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

function getHomeGroupStats(id) {
    let resData = {
        url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${id}/statistics/`
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

function getPastorsByDepartment(id) {
    let resData = {};
    if (id) {
        resData.url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/get_pastors_by_department/?department_id=${id}`;
    } else {
        resData.url = `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/get_pastors_by_department/`;
    }
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

function getLeadersByChurch(config = {}) {
    let resData = {
        url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/get_current_leaders/`,
        data: config
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

function getData(url, options = {}) {
    let keys = Object.keys(options);
    if (keys.length) {
        url += '?';
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }
    let defaultOption = {
        method: 'GET',
        credentials: "same-origin",
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };
    if (typeof url === "string") {
        $('.preloader').hide();
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}