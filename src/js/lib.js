function getChurches(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            statusCode: {
                200: function (req) {
                    resolve(req);
                },
                403: function () {
                    reject('Вы должны авторизоватся');
                }

            },
            fail: reject
        };

        newAjaxRequest(data)
    });
}

function createHomeGroupsTable(config = {}) {
    config.search_title = $('input[name="fullsearch"]').val();
    getHomeGroups(config).then(function (data) {
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
        $('#tableHomeGroup').html(rendered);
        $('.quick-edit').on('click', function () {
            let id = $(this).closest('.edit').find('a').attr('data-id');
            ajaxRequest(`${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${id}/`, null, function (data) {
                let quickEditCartTmpl, rendered;
                console.log(data);
                quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                rendered = _.template(quickEditCartTmpl)(data);
                $('#quickEditCartPopup .popup_body').html(rendered);
                $('#opening_date').datepicker({
                    dateFormat: 'yyyy-mm-dd'
                });
                makePastorList(data.department, '#editPastorSelect', data.leader);
                makeDepartmentList('#editDepartmentSelect', data.department).then(function () {
                    $('#editDepartmentSelect').on('change', function () {
                        $('#pastor_select').prop('disabled', true);
                        var department_id = parseInt($('#editDepartmentSelect').val());
                        makePastorList(department_id, '#editPastorSelect');
                    });
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
            callback: createHomeGroupsTable
        };
        makePagination(paginationConfig);
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        orderTable.sort(createHomeGroupsTable);
    });
}

function makePastorList(id, selector, active = null) {
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
function getHomeGroups(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            statusCode: {
                200: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }

            },
            fail: reject
        };

        newAjaxRequest(data)
    });
}
function exportTableData(el) {
        let url, filter, filterKeys, items, count;
        url = $(el).data('url');
        filter = getFilterParam() ;
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
        $(el).closest('form').attr('action', url);
        // newAjaxRequest({
        //     url: url,
        //     method: 'POST',
        //     data: {
        //         fields: getDataTOExport().join(',')
        //     },
        //     headers : {"Content-Transfer-Encoding": "binary"},
        //     statusCode: {
        //         200: function (data, textStatus, res) {
        //             console.log(textStatus);
        //             console.log(res);
        //             // check for a filename
        //             let filename = "";
        //             let disposition = res.getResponseHeader('Content-Disposition');
        //             console.log(disposition);
        //             if (disposition && disposition.indexOf('attachment') !== -1) {
        //                 let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        //                 let matches = filenameRegex.exec(disposition);
        //                 if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
        //             }
        //
        //             let type = res.getResponseHeader('Content-Type') + ';charset=charset=utf-8;base64';
        //             console.log(type);
        //             let blob = new Blob([data], {type: type});
        //             if (typeof window.navigator.msSaveBlob !== 'undefined') {
        //                 // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
        //                 window.navigator.msSaveBlob(blob, filename);
        //             } else {
        //                 let URL = window.URL || window.webkitURL;
        //                 let downloadUrl = URL.createObjectURL(blob);
        //
        //                 if (filename) {
        //                     // use HTML5 a[download] attribute to specify filename
        //                     let a = document.createElement("a");
        //                     // safari doesn't support this yet
        //                     if (typeof a.download === 'undefined') {
        //                         window.location = downloadUrl;
        //                     } else {
        //                         a.href = downloadUrl;
        //                         a.download = filename;
        //                         document.body.appendChild(a);
        //                         a.click();
        //                     }
        //                 } else {
        //                     window.location = downloadUrl;
        //                 }
        //
        //                 setTimeout(function () {
        //                     URL.revokeObjectURL(downloadUrl);
        //                 }, 100); // cleanup
        //             }
        //         }
        //     }
        // });

        $('#export_fields').val(getDataTOExport().join(','));
}
function newAjaxRequest(data = {}) {
    let resData = {
        method: 'GET',
        data: {}
    };
    Object.assign(resData, data);
    if (getCookie('key')) {
        resData.headers['Authorization'] = 'Token ' + getCookie('key');
    }
    return $.ajax({
        url: resData.url,
        data: resData.data,
        type: resData.method,
        headers: resData.headers
    })
        .statusCode(data.statusCode)
        .fail(data.fail);
}
function getUsers(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            statusCode: {
                200: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }

            },
            fail: reject
        };

        newAjaxRequest(data)

    });
}


function getSummitUsers(config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/summit_ankets/`,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            statusCode: {
                200: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }

            },
            fail: reject
        };

        newAjaxRequest(data)
    });
}

function getPotencialSammitUsers(config) {
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
            getUnregisteredUsers();
            $("#send_email").prop("checked", false);
        } else {
            showPopup(JSONobj.message);
            $("#send_email").prop("checked", false);
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

// function getUsers(config = {}) {
//     return new Promise(function (resolve, reject) {
//         ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/users/', config, function (data) {
//             if (data) {
//                 resolve(data);
//             } else {
//                 reject("Ошибка")
//             }
//         })
//     });
// }

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
            console.log(data);
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
}

function saveChurchData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${id}/`, json, function (data) {
            console.log(data);
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
}
function saveHomeGroupsData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/home_groups/${id}/`, json, function (data) {
            console.log(data);
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
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
    getChurchUsers(id).then(function (data) {
        console.log(data);
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
    if (id === undefined) {
        id = $('#church').attr('data-id');
    }
    if (link === undefined) {
        link = $('.get_info .active').data('link');
    }
    getChurchDetails(id, link, config).then(function (data) {
        console.log(data);
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
            callback: createChurchesUsersTable
        };
        makePagination(paginationConfig);
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        orderTable.sort(createChurchesDetailsTable);
    })
}

function createHomeGroupUsersTable(config = {}, id) {
    if (id === undefined) {
        id = $('#home_group').data('id');
    }
    getHomeGroupUsers(config, id).then(function (data) {
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
            },
            statusCode: {
                201: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }

            },
            fail: reject
        };

        newAjaxRequest(data)
    });
}

function addHomeGroup(e, el) {
    e.preventDefault();
    let data = getAddHomeGroupData();
    let json = JSON.stringify(data);

    addHomeGroupToDataBase(json).then(function (data) {
        clearAddHomeGroupData();
        hidePopup(el);
        showPopup(`Домашняя группа ${data.get_title} добавлена в базу данных`);
    });
}

function getAddHomeGroupData() {
    return {
        "opening_date": $('#added_home_group_date').val(),
        "title": $('#added_home_group_title').val(),
        "church": $('#added_home_group_church').data('id'),
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
                    dateFormat: 'yyyy-mm-dd'
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
                },
                statusCode: {
                    201: function (req) {
                        resolve(req)
                    },
                    403: function () {
                        reject('Вы должны авторизоватся')
                    }

                },
                fail: reject
            };

            newAjaxRequest(data)
        });
    }

function addChurch(e, el, callback) {
    e.preventDefault();
    let data = getAddChurchData();
    let json = JSON.stringify(data);
    addChurchTODataBase(json).then(function (data) {
        hidePopup(el)
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

function getResponsible(id, level, search = "") {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/short_users/?department=' + id + '&level_gte=' + level + '&search=' + search, null, function (data) {
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
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/?done=3', data, function (response) {
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
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/?done=2', data, function (data) {
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
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/?expired=2', data, function (response) {
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
    if (getCookie('key')) {
        headers['Authorization'] = 'Token ' + getCookie('key');
    }
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
                    showPopup('Данные успешно обновлены');
                    resolve(response);
                } else if (xhr.status == 201) {
                    let response = JSON.parse(xhr.responseText);
                    resolve(response);
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
