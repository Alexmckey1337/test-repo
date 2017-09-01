/* global $ */

// Sorting
class OrderTable {
    constructor() {
        this.savePath = sessionStorage.getItem('path');
        this.path = window.location.pathname;
        if (this.savePath != this.path) {
            sessionStorage.setItem('path', this.path);
            sessionStorage.setItem('revers', '');
            sessionStorage.setItem('order', '');
        }
    }

    get sort() {
        return this._addListener;
    }

    _addListener(callback, selector) {
        $(selector).on('click', function () {
            let dataOrder = void 0;
            const data_order = this.getAttribute('data-order');
            if (data_order == "no_ordering") {
                return;
            }
            let page = $('.pagination__input').val();
            let revers = sessionStorage.getItem('revers') ? sessionStorage.getItem('revers') : "+";
            let order = sessionStorage.getItem('order') ? sessionStorage.getItem('order') : '';
            if (order != '') {
                dataOrder = order == data_order && revers == "+" ? '-' + data_order : data_order;
            } else {
                dataOrder = '-' + data_order;
            }
            const data = {
                'ordering': dataOrder,
                'page': page
            };
            if (order == data_order) {
                revers = revers == '+' ? '-' : '+';
            } else {
                revers = "+";
            }
            sessionStorage.setItem('revers', revers);
            sessionStorage.setItem('order', data_order);
            $('.preloader').css('display', 'block');
            callback(data);
        });
    }
}

class DeleteUser {
    constructor(id, userName, title) {
        this.user = id;
        this.user_name = userName;
        this.title = title;
    }

    deleteUser() {
        return this.user
    }

    btn() {
        let btn = document.createElement('button');
        return $(btn).on('click', this.deleteUser.bind(this));
    }

    popup(massage = null, info = null) {
        if (massage) {
            console.log(massage)
        }
        let btn = this.btn();
        let popup = document.getElementById('create_pop');
        let container = document.createElement('div');
        if (popup) {
            popup.parentElement.removeChild(popup)
        }

        let body = `<div class="pop_cont pop-up__confirm" >
            <div class="top-text">
                <h3>Удаление пользователя</h3><span class="close_pop">×</span>
            </div>
                <div class="main-text">
                    <p>${(massage) ? massage : `Вы действительно хотите удалить пользователя ${this.user_name} из ${this.title}?` }</p>
                    ${(info) ? info : ''}
                    <div class="buttons"></div>
                </div>
            </div>`;

        container.className = "pop-up-universal";
        container.innerHTML = body;

        $(container).find('.buttons').html(btn);
        container.id = "create_pop";
        $(container).find('.close_pop').on('click', function () {
            $('.pop-up-universal').css('display', 'none').remove();
        });

        $('body').append(container);
    }
}

class DeleteChurchUser extends DeleteUser {
    constructor(userId, churchId, callback, userName, title) {
        super(userId, userName, title);
        this.church = churchId;
        this.callback = callback;
        this.delAll = false;
        this.show_delete = true;
        this.home_group = [];
    }

    btn() {
        if (!this.show_delete) {
            return
        }
        let container = document.createElement('div');
        let btn = document.createElement('button');
        let cancel = document.createElement('button');
        $(container).addClass('btn_block');
        (this.delAll) ?
            $(btn).text('Удалить из домашних групп').addClass('ok').on('click', this.deleteFromHomeGroup.bind(this)) :
            $(btn).text('Подтвердить').addClass('ok').on('click', this.deleteFromChurch.bind(this));
        $(cancel).text('Отменить').addClass('close_pop');
        $(container).append(cancel).append(btn);
        return container
    }

    deleteFromChurch() {
        let options = {
            method: 'POST',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
                user_id: this.user
            })
        };
        return fetch(URLS.church.del_user(this.church), options)
            .then(res => {
                return (res.status == 204) ? res.status : res.json()
            })
            .then(data => {
                if (data !== 204 && data.home_groups) {
                    let info = data.home_groups.map(item => `<p>Состоит в ${item.name}</p>`);
                    this.home_group = data.home_groups.map(item => item.id);
                    this.delAll = true;
                    this.popup(data.detail, info)
                }
                if (data === 204) {
                    this.show_delete = false;
                    this.popup('Пользователь удален из церкви');
                    this.callback();
                }
            })
            .catch(err => {
                this.show_delete = false;
                this.popup(JSON.parse(err));
            });
    }

    deleteFromHomeGroup() {
        let options = {
            method: 'POST',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
                user_id: this.user
            })
        };
        this.delAll = false;
        let massage = 'Пользователь удален из домашней группы';
        let info = '<p>Подтвердите удаление пользователя из церкви</p>';
        Promise.all(this.home_group.map((item) => {
            fetch(URLS.home_group.del_user(item), options)
        }))
            .then(() => {
                this.home_group = [];
                this.popup(massage, info);
            })
            .catch(err => {
                this.show_delete = false;
                this.popup(JSON.parse(err));
            });
    }
}

class DeleteHomeGroupUser extends DeleteUser {
    constructor(groupId, userId, callback, userName, title) {
        super(userId, userName, title);
        this.home_group = groupId;
        this.callback = callback;
        this.show_delete = true;
    }

    btn() {
        if (!this.show_delete) {
            return
        }
        let container = document.createElement('div');
        let btn = document.createElement('button');
        let cancel = document.createElement('button');
        $(container).addClass('btn_block');
        $(btn).text('Подтвердить').addClass('ok').on('click', this.deleteFromHomeGroup.bind(this));
        $(cancel).text('Отменить').addClass('close_pop');
        $(container).append(cancel).append(btn);
        return container
    }

    deleteFromHomeGroup() {
        let options = {
            method: 'POST',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
                user_id: this.user
            })
        };
        return fetch(URLS.home_group.del_user(this.home_group), options)
            .then(res => {
                return (res.status == 204) ? res.status : res.json()
            })
            .then(data => {
                if (data === 204) {
                    this.show_delete = false;
                    this.popup('Пользователь удален из домашней группы');
                    this.callback();
                }
            })
            .catch(err => {
                this.show_delete = false;
                this.popup(JSON.parse(err));
            });
    }
}

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
            url: URLS.church.list(),
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

function deleteSummitProfile(id) {
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

function addUserToHomeGroup(user_id, hg_id, exist = false) {
    let url = URLS.user.set_home_group(user_id);
    let config = {
        url: url,
        method: "POST",
        data: {
            home_group_id: hg_id
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

function createHomeGroupsTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
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
        new OrderTable().sort(createHomeGroupsTable, ".table-wrap th");
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

function makePastorList(departmentId, selector, active = null) {
    getResponsible(departmentId, 2).then(function (data) {
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
    Object.assign(config, getSearch('search_fio'));
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
        new OrderTable().sort(getPartners, ".table-wrap th");
    });
}

function makeDepartmentList(selector, active = null) {
    return getDepartmentsOfUser($("body").data("user")).then(function (data) {
        let options = [];
        let department = data;
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
            url = `${URLS.church.for_select()}?`;
            let i = 0;
            department_ids.forEach(function (department_id) {
                i++;
                url += `department=${department_id}`;
                if (department_ids.length != i) {
                    url += '&';
                }
            })
        } else {
            url = `${URLS.church.for_select()}?department=${department_ids}`;
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
            url: `${URLS.home_group.for_select()}?church_id=${id}`,
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

function exportNewTableData(el) {
    let _self = el;
    return new Promise(function (resolve, reject) {
        let url, filter, filterKeys, items, count;
        let summitId = $('#summitsTypes').find('.active').data('id');
        url = $(_self).attr('data-export-url');
        url = url.replace('<id>', summitId);
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

function exportTableData(el, additionalFilter = {}) {
    let _self = el;
    return new Promise(function (resolve, reject) {
        let url, filter, filterKeys, items, count;
        url = $(_self).attr('data-export-url');
        filter = Object.assign(getFilterParam(), getSearch('search_fio'), additionalFilter);
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
            url: URLS.user.list(),
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
            url: URLS.user.short(),
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

function getPotencialSammitUsers(config) {
    console.log(config);
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.summit_search(), config, function (data) {
            resolve(data);
        });
    });
}

function registerUserToSummit(config) {
    ajaxRequest(URLS.summit_profile.list(), config, function (data) {
        showPopup("Пользователь добавлен в саммит.");
        createSummitUsersTable();
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        },
        404: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        },
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        }
    });
}

function updateSummitProfile(profileID, config) {
    ajaxRequest(URLS.summit_profile.detail(profileID), config, function (data) {
        showPopup("Данные участника саммита изменены.");
        createSummitUsersTable();
    }, 'PATCH', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        },
        404: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        },
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        },
        405: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        }
    });
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

function getChurchDetails(id, link, config) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(`${URLS.church.detail(id)}${link}/`, config, function (data) {
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
        ajaxRequest(URLS.home_group.users(id), config, function (data) {
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
        ajaxRequest(URLS.user.detail(id), json, function (data) {
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
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

function deleteUserINHomeGroup(homeGroupId, user_id) {
    return new Promise(function (resolve, reject) {
        let json = JSON.stringify({
            "user_id": user_id
        });
        ajaxRequest(URLS.home_group.del_user(homeGroupId), json, function () {
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createChurchesDetailsTable, ".table-wrap th");
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createHomeGroupUsersTable, ".table-wrap th");
    })
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
    $('#added_churches_date').val('');
        $('#added_churches_is_open').prop('checked', false);
        $('#added_churches_title').val('');
        $('#added_churches_country').val('');
        $('#added_churches_city').val('');
        $('#added_churches_address').val('');
        $('#added_churches_phone').val('');
        $('#added_churches_site').val('');
}

function clearAddHomeGroupData() {
    $('#added_home_group_date').val('');
    $('#added_home_group_title').val('');
    $('#added_home_group_city').val('');
    $('#added_home_group_address').val('');
    $('#added_home_group_phone').val('');
    $('#added_home_group_site').val('');
}

function createChurchesTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
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
            ajaxRequest(URLS.church.detail(id), null, function (data) {
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
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createChurchesTable, ".table-wrap th");
    });
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

function addHomeGroup(e, el, callback) {
    e.preventDefault();
    let data = getAddHomeGroupData();
    let json = JSON.stringify(data);

    addHomeGroupToDataBase(json).then(function (data) {
        clearAddHomeGroupData();
        hidePopup(el);
        callback();
        showPopup(`Домашняя группа ${data.get_title} добавлена в базу данных`);
    }).catch(function (data) {
        hidePopup(el);
        showPopup('Ошибка при создании домашней группы');
    });
}

function getCountryCodes() {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.country(), null, function (data) {
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
        ajaxRequest(URLS.region(), config, function (data) {
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
        ajaxRequest(URLS.city(), config, function (data) {
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
        ajaxRequest(URLS.partner.list(), config, function (data) {
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
        ajaxRequest(URLS.country(), null, function (data) {
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
        ajaxRequest(URLS.country(), null, function (data) {
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
        ajaxRequest(URLS.department(), null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject('Ошибка');
            }
        });
    });
}

function getDepartmentsOfUser(userId) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(URLS.user.departments(userId), null, function (data) {
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
        ajaxRequest(URLS.hierarchy(), null, function (data) {
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
        ajaxRequest(URLS.user.detail(id), null, function (data) {
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
        let url = `${URLS.user.short()}?master_tree=${masterTree}`;
        ajaxRequest(url, null, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
}
function getResponsibleBYHomeGroupSupeMegaNew(config) {
    let masterTree = (config.userId) ? config.userId : $('body').data('user');
    return new Promise(function (resolve, reject) {
        let url = URLS.home_group.potential_leaders();
        ajaxRequest(url, {master_tree: masterTree, department: config.departmentId}, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    })
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

function getResponsible(ids, level, search = "") {
    let responsibleLevel;
    if (level === 0 || level === 1) {
        responsibleLevel = level + 1;
    } else {
        responsibleLevel = level;
    }
    return new Promise(function (resolve, reject) {
        let url = `${URLS.user.short()}?level_gte=${responsibleLevel}&search=${search}`;
        if (ids instanceof Array) {
            ids.forEach(function (id) {
                url += '&department=' + id;
            });
        } else {
            (ids !== null) && (url += '&department=' + ids);
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
        ajaxRequest(URLS.hierarchy(), null, function (data) {
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
        ajaxRequest(URLS.user.list(), config, function (data) {
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
        ajaxRequest(URLS.church.potential_users_church(), config, function (data) {
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
        ajaxRequest(URLS.church.potential_users_group(id), config, function (data) {
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
        ajaxRequest(URLS.division(), null, function (data) {
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
        ajaxRequest(URLS.partner.simple(), null, function (data) {
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
        ajaxRequest(`${URLS.deal.list()}?done=False`, data, function (response) {
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
        ajaxRequest(`${URLS.deal.list()}?done=True`, data, function (data) {
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
        ajaxRequest(`${URLS.deal.list()}?expired=True`, data, function (response) {
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
        ajaxRequest(URLS.deal.payments(id), null, function (data) {
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

function createPaymentsTable(config) {
    Object.assign(config, getSearch('search_purpose_fio'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getPaymentsDeals(config).then(function (data) {
        let count = data.count;
        let page = config['page'] || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
        let id = "paymentsList";
        let text = `Показано ${showCount} из ${count}`;
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

function homeStatistics() {
    let data = {};
        Object.assign(data, getFilterParam());
        Object.assign(data, getTabsFilterParam());
    getData(URLS.event.home_meeting.stats(), data).then(data => {
        let tmpl = document.getElementById('statisticsTmp').innerHTML;
        let rendered = _.template(tmpl)(data);
        document.getElementById('statisticsContainer').innerHTML = rendered;
    })
}

function churchStatistics() {
    let data = {};
        Object.assign(data, getFilterParam());
        Object.assign(data, getTabsFilterParam());
    getData(URLS.event.church_report.stats(), data).then(data => {
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
// function counterNotifications() {
//     ajaxRequest(URLS.notification(), null, function (data) {
//         $('.sms').attr('data-count', data.count);
//     });
// }

function counterNotifications() {
    let url = URLS.notification_tickets();
    let defaultOption = {
        method: 'GET',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };

    return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
}

function birhtdayNotifications(options = {}, count = false) {
    let keys = Object.keys(options),
        today = moment().format('YYYY-MM-DD'),
        url = (count) ? `${URLS.users_birthdays(today)}&only_count=true&` : `${URLS.users_birthdays(today)}&`,
        defaultOption = {
        method: 'GET',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };
    if (keys.length) {
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }

    return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
}

function repentanceNotifications(options = {}, count = false) {
    let keys = Object.keys(options),
        today = moment().format('YYYY-MM-DD'),
        url = (count) ? `${URLS.users_repentance_days(today)}&only_count=true&` : `${URLS.users_repentance_days(today)}`,
        defaultOption = {
        method: 'GET',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };
    if (keys.length) {
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }

    return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
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

function showPopup(text, title, callback) {
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

function showStatPopup(body, title, callback) {
    title = title || 'Информационное сообщение';
    let popup = document.getElementById('create_pop');
    if (popup) {
        popup.parentElement.removeChild(popup)
    }
    let div = document.createElement('div');

    let html = `<div class="pop_cont" >
        <div class="top-text">
            <h3>${title}</h3><span id="close_pop">×</span></div>
            <div class="main-text">${body}</div>
            <div><button class="make">СФОРМИРОВАТЬ</button></div>
        </div>`;
    $(div)
        .html(html)
        .attr({
            id: "create_pop"
        })
        .addClass('pop-up__stats')
        .find('.date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $(div).find('select').select2();
    $(div).find('.make').on('click', function (e) {
        e.stopPropagation();
        let data = {
            id: $(div).find('.master').val(),
            attended: $(div).find('.attended').val(),
            date: $(div).find('.date').val()
        };
        callback(data);
    });
    $('body').append(div);

    $('#close_pop').on('click', function () {
        $('.pop-up__stats').css('display', 'none').remove();
    });
}

function showPopupAddUser(data) {
    let tmpl = document.getElementById('addUserSuccessPopup').innerHTML;
    let rendered = _.template(tmpl)(data);
    $('body').append(rendered);

    $('#addPopup').find('.close, .rewrite').on('click', function (e) {
        e.preventDefault();
        $('#addPopup').css('display', 'none').remove();
        $('#addNewUserPopup').find('form').css("transform", "translate3d(0px, 0px, 0px)");
        clearAddNewUser();
        $('#addNewUserPopup').find('.body').scrollTop(0);
        if ($(this).is('a')) {
            let url = $(this).attr('href');
            setTimeout(function () {
                window.open(url);
            }, 1000);
        }
    });
    $('#addPopup').find('.addMore').on('click', function () {
        $('#addPopup').css('display', 'none').remove();
        $('body').addClass('no_scroll');
        $('#addNewUserPopup').find('form').css("transform", "translate3d(0px, 0px, 0px)");
        $('#addNewUserPopup').css('display', 'block');
        clearAddNewUser();
        $('#addNewUserPopup').find('.body').scrollTop(0);
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
                if (!status) {
                    return;
                }
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
                    if (status > 60) {
                        let option = document.createElement('option');
                        $(option).val('').text('Нет ответственного');
                        rendered.push(option);
                    }
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
        address: $($(el).closest('.pop_cont').find('#address')).val()
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
        showPopup(html);
    });
}

function editChurches(el, id) {
    let data = {
        pastor: $($(el).closest('form').find('#editPastorSelect')).val(),
        department: $($(el).closest('form').find('#editDepartmentSelect')).val(),
        phone_number: $($(el).closest('form').find('#phone_number')).val(),
        website: ($(el).closest('form').find('#web_site')).val(),
        opening_date: $($(el).closest('form').find('#opening_date')).val().split('.').reverse().join('-') || null,
        is_open: $('#is_open_church').is(':checked'),
        country: $($(el).closest('form').find('#country')).val(),
        city: $($(el).closest('form').find('#city')).val(),
        address: $($(el).closest('form').find('#address')).val()
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
        showPopup(html);
    });
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
        })
    }).catch(function (res) {
        let error = JSON.parse(res.responseText);
        let errKey = Object.keys(error);
        let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
        showPopup(html);
    });
}

function editHomeGroups(el, id) {
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
        showPopup(html);
    });
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

function makeQuickEditCart(el) {
    let id, link, url;
    id = $(el).closest('td').find('a').attr('data-id');
    link = $(el).closest('td').find('a').attr('data-link');
    url = URLS.user.detail(id);
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
        });
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
    Object.assign(config, getSearch('search_fio'));
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
        new OrderTable().sort(createUsersTable, ".table-wrap th");
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
    ajaxRequest(URLS.update_columns(), json, function (JSONobj) {
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
    let $input = $(el).closest('.popap').find('input'),
        $select = $(el).closest('.popap').find('select'),
        $selectCustom = $(el).closest('.popap').find('select.select__custom');
    $(el).addClass('refresh');
    setTimeout(function () {
        $(el).removeClass('refresh');
    }, 700);
    $input.each(function () {
        $(this).val('')
    });
    $select.each(function () {
        $(this).val(null).trigger("change");
    });
    $selectCustom.each(function () {
        $(this).val('ВСЕ').trigger("change");
    });
}

function getSearch(title) {
    let search = $('input[name="fullsearch"]').val();
    if (!search) return {};
    return {
        [title]: search
    }
}
function getTabsFilter() {
    const $tabsFilter = $('.tabs-filter');
    let data = {};
    const $button = $tabsFilter.find('.active').find('button[data-filter]');
    const $input = $tabsFilter.find('input[data-filter]');

    $button.each(function () {
        let field = $(this).data('filter');
        let value = $(this).data('filter-value');
        console.log(field, value);
        data[field] = value;
    });

    $input.each(function () {
        let field = $(this).data('filter');
        let value = $(this).val();
        data[field] = value;
    });
    return data
}
function getTabsFilterParam() {
    let data = {},
        dataTabs = {},
        dataRange = {},
        type = $('#tabs').find('li.active').find('button').attr('data-id');
    if (type > "0") {
        dataTabs.type = type;
        Object.assign(data, dataTabs);
    }
    let rangeDate = $('.tab-home-stats').find('.set-date').find('input').val();
    if (rangeDate) {
        let dateArr = rangeDate.split('-');
        dataRange.from_date = dateArr[0].split('.').reverse().join('-');
        dataRange.to_date = dateArr[1].split('.').reverse().join('-');
        Object.assign(data, dataRange);
    }
    return data
}
function getFilterParam() {
    let $filterFields,
        data = {};
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

    let url = '',
        filterKeys = Object.keys(data);
    if (filterKeys && filterKeys.length) {
        let items = filterKeys.length,
            count = 0;
        filterKeys.forEach(function (key) {
            count++;
            url += key + '=' + data[key];
            if (count != items) {
                url += '&';
            }
        });
        history.replaceState(null, null, `?${url}`);
    }
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

    let count = getCountFilter();
    $('#filter_button').attr('data-count', count);
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
    config.status = status;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    getHomeReports(config).then(data => {
        makeHomeReportsTable(data, config);
    })
}

function homeLiderReportsTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    getHomeLiderReports(config).then(data => {
        makeHomeLiderReportsTable(data, config);
    })
}

function churchReportsTable(config = {}) {
    let status = $('#statusTabs').find('.current').find('button').data('status');
    config.status = status;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    getChurchReports(config).then(data => {
        makeChurchReportsTable(data, config);
    })
}

function churchPastorReportsTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    getChurchPastorReports(config).then(data => {
        makeChurchPastorReportsTable(data, config);
    })
}

function makeHomeReportsTable(data, config = {}) {
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
    new OrderTable().sort(homeReportsTable, ".table-wrap th");
    $('.preloader').hide();
}

function makeHomeLiderReportsTable(data, config = {}) {
    let tmpl = $('#databaseHomeLiderReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeLiderReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: homeLiderReportsTable
    };
    $('.table__count').text(data.count);
    $('#homeLiderReports').find('table').on('click', (e) => {
        if (e.target.className != 'url') return;
        let url = e.target.getAttribute('data-url'),
            type = e.target.getAttribute('data-type'),
            nameId = e.target.getAttribute('data-id');
        window.location = `${url}?type=${type}&owner=${nameId}`;
    });
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('.table__count').text(text);
    new OrderTable().sort(homeLiderReportsTable, ".table-wrap th");
    $('.preloader').hide();
}

function makeChurchReportsTable(data, config = {}) {
    let tmpl = $('#databaseChurchReports').html();
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
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('.table__count').text(text);
    new OrderTable().sort(churchReportsTable, ".table-wrap th");
    $('.preloader').hide();
}

function makeChurchPastorReportsTable(data, config = {}) {
    let tmpl = $('#databaseChurchPastorReports').html();
    let rendered = _.template(tmpl)(data);
    $('#churchPastorReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: churchPastorReportsTable
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('#churchPastorReports').find('table').on('click', (e) => {
        if (e.target.className != 'url') return;
        let url = e.target.getAttribute('data-url'),
            type = e.target.getAttribute('data-type'),
            nameId = e.target.getAttribute('data-id');
        window.location = `${url}?type=${type}&nameId=${nameId}`;
    });
    $('.table__count').text(text);
    new OrderTable().sort(churchPastorReportsTable, ".table-wrap th");
    $('.preloader').hide();
}

function getHomeReports(config = {}) {
    if (!config.status) {
        let status = parseInt($('#statusTabs').find('.current').find('button').data('status'));
        config.status = status || 1;
    }
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.list(),
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
function getHomeLiderReports(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.summary(),
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
function getChurchReports(config = {}) {
    if (!config.status) {
        let status = parseInt($('#statusTabs').find('.current').find('button').data('status'));
        config.status = status || 1;
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
function getChurchPastorReports(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.church_report.summary(),
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
    let url = URLS.user.list();
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
        if (data.phone_number) {
            showPopup(data.phone_number.message);
            $('#createUser').css("transform","translate3d(0px, 0px, 0px)");
        }
        if (data.detail) {
            showPopup(data.detail[0]);
        }
    });

}

function createPayment(data, id) {
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

function getPastorsByDepartment(config) {
    let data = {
        url: URLS.church.available_pastors(),
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
        newAjaxRequest(data, codes, reject);
    });
}

function getHGLeaders(config = {}) {
    let data = {
        url: URLS.home_group.leaders(),
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
        newAjaxRequest(data, codes, reject);
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
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };
    if (typeof url === "string") {
        $('.preloader').hide();
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}

function pasteLink(el, link) {
    $(el).closest('.input').find('a').attr('href', link);
}

function getCountFilter() {
    let $filterFields,
        count = 0;
    $filterFields = $('#filterPopup select, #filterPopup input');
    $filterFields.each(function () {
        if ($(this).val() == "ВСЕ") {
            return
        }
         if ($(this).val()) {
             count++;
         }
    });

    return count;
}

function btnDeals() {
    $("button.pay").on('click', function () {
        let id = $(this).data('id');
        let value = $(this).data('value');
        let total_sum = $(this).data('total_sum');
        let diff = numeral(value).value() - numeral(total_sum).value();
        let currencyName = $(this).data('currency-name');
        let currencyID = $(this).data('currency-id');
        diff = diff > 0 ? diff : 0;
        $('#new_payment_sum').val(diff);
        $('#complete-payment').attr('data-id', id);
        $('#purpose-id').val(id);
        $('#popup-create_payment').css('display', 'block');
        sumChangeListener(currencyName, currencyID);
    });

    $("button.complete").on('click', function () {
        let client_name = $(this).attr('data-name'),
            deal_date = $(this).attr('data-date'),
            responsible_name = $(this).attr('data-responsible');
        $('#complete').attr('data-id', $(this).data('id'));
        $('#client-name').val(client_name);
        $('#deal-date').val(deal_date);
        $('#responsible-name').val(responsible_name);
        $('#popup').css('display', 'block');
    });
}

function createIncompleteDealsTable(config={}) {
    Object.assign(config, {done: 3});
    Object.assign(config, getSearch('search'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getDeals(config).then(function (data) {
        let count = data.count,
            page = config['page'] || 1,
            pages = Math.ceil(count / CONFIG.pagination_count),
            showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
            id = 'incompleteList',
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
            container: '.undone__pagination',
            currentPage: page,
            pages: pages,
            callback: createIncompleteDealsTable
        };
        makeDealsDataTable(data, id);
        makePagination(paginationConfig);
        $('#incomplete').find('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createIncompleteDealsTable, ".table-wrap th");
        btnDeals();
    });
}

function createExpiredDealsTable(config={}) {
    Object.assign(config, {expired: 2});
    Object.assign(config, getSearch('search'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getDeals(config).then(function (data) {
        let count = data.count,
            page = config['page'] || 1,
            pages = Math.ceil(count / CONFIG.pagination_count),
            showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
            id = 'overdueList',
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
            container: '.expired__pagination',
            currentPage: page,
            pages: pages,
            callback: createExpiredDealsTable
        };
        makeDealsDataTable(data, id);
        makePagination(paginationConfig);
        $('#overdue').find('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createExpiredDealsTable, ".table-wrap th");
        btnDeals();
    });
}

function createDoneDealsTable(config={}) {
    Object.assign(config, {done: 2});
    Object.assign(config, getSearch('search'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getDeals(config).then(function (data) {
        let count = data.count,
            page = config['page'] || 1,
            pages = Math.ceil(count / CONFIG.pagination_count),
            showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
            id = 'completedList',
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
            container: '.done__pagination',
            currentPage: page,
            pages: pages,
            callback: createDoneDealsTable
        };
        makeDealsDataTable(data, id);
        makePagination(paginationConfig);
        $('#completed').find('.table__count').text(text);
        makeSortForm(data.table_columns);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createDoneDealsTable, ".table-wrap th");
    });
}

function makeDealsDataTable(data, id) {
    let tmpl = document.getElementById('databaseDeals').innerHTML,
        rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.show_payments').on('click', function () {
        let id = $(this).data('id');
        showPayments(id);
    });
}

function showPayments(id) {
    getPayment(id).then(function (data) {
        let payments_table = '';
        let sum, date_time, manager;
        data.forEach(function (payment) {
            sum = payment.effective_sum_str.replace('.000', '');
            date_time = payment.sent_date;
            manager = `${payment.manager.last_name} ${payment.manager.first_name} ${payment.manager.middle_name}`;
            payments_table += `<tr><td>${sum}</td><td>${date_time}</td><td>${manager}</td></tr>`
        });
        $('#popup-payments table').html(payments_table);
        // let detail_url = $('#popup-payments .detail').data('detail-url').replace('0', id);
        // console.log(detail_url);
        // $('#popup-payments .detail').attr('data-detail-url', detail_url);
        $('#popup-payments').css('display', 'block');
    })
}

function getDeals(options = {}) {
    let keys = Object.keys(options),
        url = URLS.deal.list();
    if (keys.length) {
        url += '?';
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }
    let defaultOption = {
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

let sumChangeListener = (function () {
    let $form = $('#payment-form');
    let currencyID, currencyName, new_payment_sum, new_payment_rate, operation;
    let $currencies = $form.find('#new_payment_currency');
    let $currencyOptions = $currencies.find('option');
    let $operation = $form.find('#operation');
    let $operationLabel = $form.find('label[for="operation"]');
    let $newPaymentSumEl = $form.find('#new_payment_sum');
    let $newPaymentRateEl = $form.find('#new_payment_rate');
    let $inUserCurrencyEl = $form.find('#in_user_currency');

    $operationLabel.on('click', function () {
        let operation = $operation.val();
        let newOperation = (operation == '*') ? '/' : '*';
        $operation.val(newOperation);
        operation = newOperation;
        new_payment_rate = $newPaymentRateEl.val();
        new_payment_sum = $newPaymentSumEl.val();
        sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
    });
    $currencies.on('change', function () {
        if ($(this).val() != currencyID) {
            $('#new_payment_rate').prop('readonly', false);
        } else {
            $('#new_payment_rate').prop('readonly', true).val('1.000').trigger('change');
        }
    });
    $form.on('keypress', function (e) {
        return e.keyCode != 13;
    });

    $newPaymentSumEl.on('change', function () {
        new_payment_sum = $newPaymentSumEl.val();
        operation = $operation.val();
        sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
    });

    $newPaymentSumEl.on('keypress', function (e) {
        if (e.keyCode == 13) {
            new_payment_sum = $newPaymentSumEl.val();
            operation = $operation.val();
            sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        }
    });
    $newPaymentRateEl.on('change', function () {
        new_payment_rate = $newPaymentRateEl.val();
        sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
    });
    $newPaymentRateEl.on('keypress', function (e) {
        if (e.keyCode == 13) {
            new_payment_rate = $newPaymentRateEl.val();
            operation = $operation.val();
            sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        }
    });
    // $operation.on('change', function () {
    //     operation = $operation.val();
    //     new_payment_rate = $newPaymentRateEl.val();
    //     new_payment_sum = $newPaymentSumEl.val();
    //     sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
    // });
    return function (currency_name, currency_id) {
        $('#new_payment_rate').prop('readonly', true);
        currencyID = currency_id;
        currencyName = currency_name;
        $newPaymentRateEl.val('1.000');
        new_payment_sum = $newPaymentSumEl.val();
        new_payment_rate = $newPaymentRateEl.val();
        $operation.val('*');
        operation = '*';

        $currencyOptions.each(function () {
            $(this).prop('selected', false);
            if ($(this).val() == currencyID) {
                $(this).prop('selected', true);
            }
        });

        sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
    }

})();

function sumCurrency(sum, operation, rate, currencyEl, currencyName) {
    let userPay;
    if (operation == "*") {
        userPay = parseFloat(sum) * parseFloat(rate);
    } else if (operation == "/") {
        userPay = parseFloat(sum) * (1 / parseFloat(rate));
    }
    currencyEl.text(parseInt(userPay) + currencyName);
}

function createDealsPayment(id, sum, description) {
    return new Promise(function (resolve, reject) {
        let data = {
            "sum": sum,
            "description": description,
            "rate": $('#new_payment_rate').val(),
            "currency": $('#new_payment_currency').val(),
            "sent_date": $('#sent_date').val(),
            "operation": $('#operation').val()
        };
        let json = JSON.stringify(data);
        ajaxRequest(URLS.deal.create_payment(id), json, function (JSONobj) {
            updateDealsTable();
            showPopup('Оплата прошла успешно.');
            setTimeout(function () {
                resolve()
            }, 1500);
        }, 'POST', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showPopup(data.detail);
                reject();
            }
        });
    })
}

function updateDealsTable() {
    $('.preloader').css('display', 'block');
    let pageIncompleteDeals = $('#incomplete').find('.pagination__input').val(),
        pageExpiredDeals = $('#overdue').find('.pagination__input').val(),
        pageDoneDeals = $('#completed').find('.pagination__input').val();
    createIncompleteDealsTable({page: pageIncompleteDeals});
    // createExpiredDealsTable({page: pageExpiredDeals});
    createDoneDealsTable({page: pageDoneDeals});
}

function getPreSummitFilterParam() {
    let $filterFields,
        data = {};
    $filterFields = $('.charts_head select');
    $filterFields.each(function () {
        if ($(this).val() == "ВСЕ") {
            return
        }
        let prop = $(this).data('filter');
        if (prop) {
            if ($(this).val()) {
                data[prop] = $(this).val();
            }
        }
    });

    return data;
}

function getSummitStats(url, config = {}) {
    // Object.assign(config, getFilterParam());
    Object.assign(config, getPreSummitFilterParam());
    return new Promise(function (resolve, reject) {
        let data = {
            url: url,
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

function getSummitStatsForMaster(summitId, masterId, config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.summit.stats_by_master(summitId, masterId),
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

function getResponsibleForSelect(config={}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.user.list_user(),
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

function makeResponsibleSummitStats(config, selector = [], active = null) {
    getResponsibleForSelect(config).then(function (data) {
        let options = '<option selected>ВСЕ</option>';
        data.forEach(function (item) {
            options += `<option value="${item.id}"`;
            if (active == item.id) {
                options += 'selected';
            }
            options += `>${item.title}</option>`;
        });
        selector.forEach(item => {
            $(item).html(options).prop('disabled', false).select2();
        })
    });
}

function getDuplicates(options = {}) {
    let keys = Object.keys(options),
        url = URLS.user.find_duplicates();
    if (keys.length) {
        url += '?';
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }
    let defaultOption = {
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

function parseUrlQuery() {
    let data = {};
    if(location.search) {
        let pair = (location.search.substr(1)).split('&');
        for(let i = 0; i < pair.length; i ++) {
            let param = pair[i].split('=');
            data[param[0]] = param[1];
        }
    }
    return data;
}
