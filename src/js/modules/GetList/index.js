'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
import {getOrderingData} from "../Ordering/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';

export function getResponsible(ids, level, search = "") {
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

export function getChurchesListINDepartament(department_ids) {
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
            url = (department_ids != null) ? `${URLS.church.for_select()}?department=${department_ids}` : `${URLS.church.for_select()}`;
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

export function getHomeGroupsINChurches(id) {
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

export function getCountries() {
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

export function getRegions(config = {}) {
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

export function getCities(config = {}) {
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

export function getChurches(config = {}) {
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

export function getDepartmentsOfUser(userId) {
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

export function getDepartments() {
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

export function getPastorsByDepartment(config) {
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

export function getStatuses() {
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

export function getDivisions() {
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

export function getCountryCodes() {
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

export function getManagers() {
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

export function getHGLeaders(config = {}) {
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

export function createHomeGroupsTable(config = {}) {
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

export function getPotentialLeadersForHG(config) {
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

export function updateLeaderSelect() {
    const config = getConfigSuperMega();
    getPotentialLeadersForHG(config).then(function (data) {
        const pastors = data.map((pastor) => `<option value="${pastor.id}">${pastor.fullname}</option>`);
        $('#added_home_group_pastor').html(pastors).prop('disabled', false).select2();
    });
}

function getConfigSuperMega() {
    const churchId = $('#added_home_group_church_select').val() || null;
    const masterId = $('#available_master_tree_id').val() || null;
    let config = {
        church: churchId,
    };
    if (masterId) {
        config.master_tree = masterId;
    }
    return config
}

export function getShortUsers(config = {}) {
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
