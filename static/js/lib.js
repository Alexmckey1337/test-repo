//Проверка существование элемента на странице
function isElementExists(element) {
    if (typeof(element) != 'undefined' && element != null) {
        return true;
    }
}

function getLastId(url) {
    if (!url) {
        url = document.location.href
    }
    var id = url.split('/');
    if (id[id.length - 1]) {
        return id[id.length - 1]
    }
    return id[id.length - 2]
}

function getCookie(c_name) {
    // From http://www.w3schools.com/js/js_cookies.asp
    var c_value = document.cookie;
    var c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start == -1) {
        c_start = c_value.indexOf(c_name + "=");
    }
    if (c_start == -1) {
        c_value = null;
    } else {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end == -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start, c_end));
    }
    return c_value;
}


Array.prototype.unique = function () {
    var a = this.concat();
    for (var i = 0; i < a.length; ++i) {
        for (var j = i + 1; j < a.length; ++j) {
            if (a[i] === a[j])
                a.splice(j--, 1);
        }
    }

    return a;
};


var delay = (function () {
    var timer = 0;
    return function (callback, ms) {
        clearTimeout(timer);
        timer = setTimeout(callback, ms);
    };
})();

//index() jquery alternative
function indexInParent(node) {
    var children = node.parentNode.childNodes;
    var num = 0;
    for (var i = 0; i < children.length; i++) {
        if (children[i] == node) return num;
        if (children[i].nodeType == 1) num++;
    }
    return -1;
}


function getRussianMonth(index) {
    var month = new Array(12);
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
    var el = document.getElementById('tab_plugin');
    if (!el) {
        return;
    }


    Array.prototype.forEach.call(document.querySelectorAll("#tab_plugin li"), function (el) {

        el.addEventListener('click', function (e) {
            e.preventDefault();
            var index = indexInParent(el);


            Array.prototype.forEach.call(document.querySelectorAll("#tab_plugin li"), function (el) {
                el.classList.remove('current')
            });
            Array.prototype.forEach.call(document.querySelectorAll("[data-tab-body]"), function (el) {
                el.style.display = 'none'
            });

            this.classList.add('current');

            var tab = document.querySelectorAll("[data-tab-body]")[index];
            if (tab) {
                tab.style.display = 'block';
            }


        });


        //  document.querySelector("#tab_plugin li").click();
    });
}
//реализация jquery live event
function live(eventType, elementQuerySelector, cb) {
    document.addEventListener(eventType, function (event) {

        var qs = document.querySelectorAll(elementQuerySelector);
        if (qs) {
            var el = event.target,
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

//Счетчик уведомлений
function counterNotifications() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/notifications/today/', null, function (data) {
        document.getElementById('count_notifications').innerHTML = '(' + data.count + ')';
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

    var popup = document.getElementById('create_pop');
    if (popup) {
        popup.parentElement.removeChild(popup)
    }
    var div = document.createElement('div');

    var html = '<div class="pop_cont" >' +
        '<div class="top-text"><h3>' + title + '</h3><span id="close_pop">×</span></div>' +
        '<div class="main-text"><p>' + text + '</p></div>' +
        '</div>';
    div.className = "pop-up-universal";
    div.innerHTML = html;
    div.id = "create_pop";

    document.body.appendChild(div);

    document.getElementById('close_pop').addEventListener('click', function () {
        document.getElementsByClassName('pop-up-universal')[0].style.display = 'none'
    });
    document.getElementsByClassName('pop-up-universal')[0].style.display = 'block'
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    url = url.toLowerCase(); // This is just to avoid case sensitiveness  
    name = name.replace(/[\[\]]/g, "\\$&").toLowerCase();// This is just to avoid case sensitiveness for query parameter name
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}


function getDepartmentsAll() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/departments/', null, function (data) {
        data = data.results;
        var html = '<option value="0">ВСЕ </option>';
        for (var i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }

        document.getElementById('dep_filter').innerHTML = html;
        // return html
    });

}

function getCorrectValue(value) {
    if (value === null) {
        return '';
    } else {
        if (value instanceof Array) {
            var str_value = [];
            value.forEach(function (v) {
                str_value = str_value.concat(getCorrectValue(v))
            });
            return str_value.join(', ')
        } else if (value instanceof Object) {
            var id = '';
            var new_value = '';
            for (var k in value) {
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
