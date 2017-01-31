function getChurches(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/churches/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}
function getHomeGroups(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/home_groups/', config, function (data) {
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка")
            }
        })
    });
}
function getUsers(config = {}) {
    return new Promise(function (resolve, reject) {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/users/', config, function (data) {
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
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/users/' + id + '/', data, function (data) {
            console.log(data);
        }, 'PATCH', false, {
            'Content-Type': 'application/x-www-form-urlencoded'
        });
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
function addChurch(e, el) {
    e.preventDefault();
    let data = getAddChurchData();
    let json = JSON.stringify(data);
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/churches/', json, function (data) {
        console.log(data);
        console.log('added');
    }, 'POST', false, {
        'Content-Type': 'application/json'
    });
    hidePopup(el)
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
        config.callback({
            page: val
        });
    });

    $(config.container).html(container);

}

function deleteCookie(name) {
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

//реализация jquery live event
function live(eventType, elementQuerySelector, cb) {
    document.addEventListener(eventType, function (event) {
        var el, index;
        let qs = document.querySelectorAll(elementQuerySelector);
        if (qs) {
            el = event.target,
                index = -1;
            while (el && ((index = Array.prototype.indexOf.call(qs, el)) === -1)) {
                el = el.parentElement;
            }
            if (index > -1) {
                cb.call(el, event);
            }
        }
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
    title = title || 'Информационное сообщение';
    text = text || '';
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
