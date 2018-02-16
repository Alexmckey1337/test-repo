'use strict';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';

export function getResponsible(ids, level, search = "", include_id = '') {
    let responsibleLevel;
    if (level === 0 || level === 1) {
        responsibleLevel = level + 1;
    } else {
        responsibleLevel = level;
    }
    return new Promise(function (resolve, reject) {
        let url = (include_id) ?
            `${URLS.user.short()}?level_gte=${responsibleLevel}&search=${search}&include_user=${include_id}`
            :
            `${URLS.user.short()}?level_gte=${responsibleLevel}&search=${search}`;
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

export function getSummitAuthors(departmentIds, summitId, level, search = "", include_id = '') {
    let responsibleLevel;
    if (level === 0 || level === 1) {
        responsibleLevel = level + 1;
    } else {
        responsibleLevel = level;
    }
    const baseUrl = URLS.summit.authors(summitId);
    return new Promise(function (resolve, reject) {
        let url = (include_id) ?
            `${baseUrl}?level_gte=${responsibleLevel}&search=${search}&include_user=${include_id}`
            :
            `${baseUrl}?level_gte=${responsibleLevel}&search=${search}`;
        if (departmentIds instanceof Array) {
            departmentIds.forEach(function (id) {
                url += '&department=' + id;
            });
        } else {
            (departmentIds !== null) && (url += '&department=' + departmentIds);
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

export function getSummitAuthorsByMasterTree(summitId, config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.summit.authors(summitId),
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

export function getHomeLiderReports(config = {}) {
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

export function getHomeGroups(config = {}) {
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

export function getResponsibleForSelect(config={}) {
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
