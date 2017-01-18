$(document).ready(function () {
    "use strict";
    $('input[name="fullsearch"]').keyup(function () {
        let id = $('#accountable').val();
        console.log(id);
        let obj = {'responsible': id};
        if (id == '0') {
            delay(function () {
                getPartnersList();
                let json = {};
                json["page"] = '1';
                getExpiredDeals(json);
                getDoneDeals(json);
                getUndoneDeals(json);
            }, 1500);
        } else {
            delay(function () {
                getPartnersList(obj);

                let json = {};
                json["page"] = '1';
                getExpiredDeals(json);
                getDoneDeals(json);
                getUndoneDeals(json);
            }, 1500);
        }

    });

    document.getElementById('sort_save').addEventListener('click', function () {
        updateSettings(getPartnersList);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });

    $.datepicker.setDefaults($.datepicker.regional["ru"]);

    $("#done_datepicker_from").datepicker({
        dateFormat: "yyyy-mm-dd",
        maxDate: new Date(),
        onSelect: function (date) {
            window.done_from_date = date;
            sortDoneDeals(done_from_date, done_to_date);
        }
    }).datepicker("setDate", '-1m');

    $("#done_datepicker_to").datepicker({
        dateFormat: "yyyy-mm-dd",
        onSelect: function (date) {
            window.done_to_date = date;
            sortDoneDeals(done_from_date, done_to_date);
        }
    }).datepicker("setDate", new Date());

    $("#expired_datepicker_from").datepicker({
        dateFormat: "yy-mm-dd",
        maxDate: new Date(),
        onSelect: function (date) {
            window.expired_from_date = date;
            sortExpiredDeals(expired_from_date, expired_to_date);
        }
    }).datepicker("setDate", '-1m');

    $("#expired_datepicker_to").datepicker({
        dateFormat: "yy-mm-dd",
        onSelect: function (date) {
            window.expired_to_date = date;
            sortExpiredDeals(expired_from_date, expired_to_date);
        }
    }).datepicker("setDate", new Date());

    makeTabs();

    document.getElementById('show-all-expired').addEventListener('click', function () {
        window.expired_from_date = '';
        window.expired_to_date = '';
        sortExpiredDeals(expired_from_date, expired_to_date);
    });

    document.getElementById('show-all-done').addEventListener('click', function () {
        window.done_from_date = '';
        window.done_to_date = '';
        sortDoneDeals(done_from_date, done_to_date);
    });

    document.getElementById('close').addEventListener('click', function () {
        document.getElementById('popup').style.display = '';
    });

    document.getElementById('complete').addEventListener('click', function () {
        let attr = this.getAttribute('data-id'),
            value = document.getElementById('deal-value').value,
            description = document.getElementById('deal-description').value;
        let reg = /^\d{1,5} ?₴?$/gi;
        if (!reg.test(value)) {
            showPopup('Введите правильное значение суммы');
            return;
        }
        updateDeals(attr, parseInt(value), description);
        document.getElementById('deal-value').setAttribute('readonly', 'readonly');
    });

    document.getElementById('changeSum').addEventListener('click', function () {
        document.getElementById('deal-value').removeAttribute('readonly');
        document.getElementById('deal-value').focus();
    });

    /*add parnership*/
    // document.querySelector(".add").addEventListener('click', function () {
    //     document.querySelector('.add-user-wrap').style.display = 'block';
    // });

    document.querySelector(".add-user-wrap .top-text span").addEventListener('click', function () {
        document.querySelector('.add-user-wrap').style.display = 'none';
    });

    document.querySelector(".choose-user-wrap .top-text > span").addEventListener('click', function () {
        document.getElementById('searchUsers').value = '';
        document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
        document.querySelector('.choose-user-wrap').style.display = '';
    });


    $('#searchUsers').keyup(function () {
        getUnregisteredUsers();
    });


});

let done_from_date = '',
    done_to_date = '',
    expired_from_date = '',
    expired_to_date = '',
    ordering = {};

init();

$('#accountable').on('change', function () {
    let id = this.value;
    let obj = {'responsible': id};
    if (id == '0') {
        getPartnersList();
    } else {
        getPartnersList(obj);
    }
});

(function createPartnershipsList() {
    if ($('#accountable')) {
        $('#accountable').select2();
    }
})();

function getUnregisteredUsers(param = {}) {
    let search = $('#searchUsers').val();
    if (search && search.length > 2) {
        param['search'] = search;
        ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/partnerships_unregister_search/', param, function (data) {
            data = data.results;
            let html = '';
            for (let i = 0; i < data.length; i++) {
                html += '<div class="rows-wrap"><button data-id=' + data[i].id + '>Выбрать</button><div class="rows"><div class="col"><p><span><a href="/account/' + data[i].id + '/">' + data[i].fullname + '</a></span></p></div><div class="col"></div></div></div>';
            }
            if (data.length > 0) {
                document.getElementById('searchedUsers').innerHTML = html;
            } else {
                document.getElementById('searchedUsers').innerHTML = '<div class="rows-wrap"><div class="rows"><p>По запросу не найдено учасников</p></div></div>';
            }
            document.querySelector('.choose-user-wrap .splash-screen').classList.add('active');
            let but = document.querySelectorAll('.rows-wrap button');
            for (let j = 0; j < but.length; j++) {
                but[j].addEventListener('click', function () {
                    let id = this.getAttribute('data-id');
                    registerUser(id);
                })
            }
        });
    } else {
        document.getElementById('searchedUsers').innerHTML = '<div class="rows-wrap"><div class="rows"><p>Для поиска введите более 2-х символов</p></div></div>';
    }
}

function registerUser(id) {
    if (!id) {
        return
    }
    let money = 0,
        dateObj = new Date(),
        month = dateObj.getUTCMonth() + 1, //months from 1-12
        day = dateObj.getUTCDate(),
        year = dateObj.getUTCFullYear(),
        newdate = year + "-" + month + "-" + day,
        data = {'date': newdate, 'user': parseInt(id)};

    data.value = money;
    data.responsible = config.user_partnerships_info.responsible;
    if (data.responsible) {
        create_partnerships(data)
    } else {
        showPopup("Для добавления партнера вы должны быть партнером.");
    }
    console.log('end reg');
}

function create_partnerships(data) {

    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/create_partnership/', json, function (JSONobj) {

        if (JSONobj.status) {
            $(".choose-user-wrap").hide();
            showPopup(JSONobj.message);
            //partners_initialize();
        } else {
            showPopup(JSONobj.message);
        }
        console.log('end partner');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });

}

function getExpiredDeals(time) {
    let json = time || null;
    let search = document.getElementsByName('fullsearch')[0].value;
    if (search) {
        search = '&search=' + search;
    } else {
        search = '';
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/deals/?expired=2' + search, json, function (data) {
        let count = data.count;
        data = data.results;
        let page = time['page'] || 1,
            pages = Math.ceil(count / config.pagination_count),
            html = '';
        if (data.length == 0) {
            document.getElementById('overdue').innerHTML = '<p class="info">Сделок нет</p>';
            document.getElementById('overdue-count').innerHTML = '0';
            Array.prototype.forEach.call(document.querySelectorAll('.expired-pagination'), function (el) {
                el.innerHTML = '';
                el.style.display = 'none';
            });
            return;
        }
        document.getElementById('overdue-count').innerHTML = count;
        let container = ".expired-pagination",
            target = ".expired-pagination .pag li",
            arrow = ".expired-pagination .arrow",
            active = ".expired-pagination .pag li.active",
            dblArrow = ".expired-pagination .double_arrow";
        makePagination(page, container, target, arrow, active, dblArrow, pages, data.length, count, getExpiredDeals);
        for (let i = 0; i < data.length; i++) {
            let fields = data[i].fields;
            if (!fields) {
                continue
            }
            let names = Object.keys(fields);
            html += '<div class="rows-wrap"><button data-id=' + fields[names[0]].value + '>Завершить</button><div class="rows"><div class="col"><p><span>' + fields[names[1]].value + '</span></p></div><div class="col"><p>Последняя сделка:<span> ' + fields[names[3]].value + '</span></p><p>Ответственный:<span> ' + fields[names[2]].value + '</span></p><p>Сумма:<span> ' + fields[names[4]].value + ' ₴</span></p></div></div></div>';
        }
        document.getElementById('overdue').innerHTML = html;
        let but = document.querySelectorAll(".rows-wrap button");
        for (let j = 0; j < but.length; j++) {
            but[j].addEventListener('click', function () {
                getDataForPopup(this.getAttribute('data-id'), this.getAttribute('data-name'), this.getAttribute('data-date'), this.getAttribute('data-responsible'), this.getAttribute('data-value') + ' ₴')
            })
        }
    });
}

function getDoneDeals(time) {
    let json = time || null;
    let search = document.getElementsByName('fullsearch')[0].value;
    if (search) {
        search = '&search=' + search;
    } else {
        search = '';
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/deals/?done=2' + search, json, function (data) {
        let count = data.count;
        data = data.results;
        let page = time['page'] || 1,
            pages = Math.ceil(count / config.pagination_count),
            html = '';
        if (data.length == 0) {
            $('#completed').html('<p class="info">Сделок нету</p>');
            $('#completed-count').html('0');
            $('.done-pagination').each(function (el) {
                $(el).html('');
                $(el).css('display', 'none');
            });
            return;
        }
        $('#completed-count').html(count);

        let container = ".done-pagination",
            target = ".done-pagination .pag li",
            arrow = ".done-pagination .arrow",
            active = ".done-pagination .pag li.active",
            dblArrow = ".done-pagination .double_arrow";
        makePagination(page, container, target, arrow, active, dblArrow, pages, data.length, count, getDoneDeals);
        for (let i = 0; i < data.length; i++) {
            let fields = data[i].fields;
            if (!fields) {
                continue
            }
            let names = Object.keys(fields);
            html += '<div class="rows-wrap"><div class="rows"><div class="col"><p><span>' + fields[names[1]].value + '</span></p></div><div class="col"><p>Последняя сделка:<span> ' + fields[names[3]].value + '</span></p><p>Ответственный:<span> ' + fields[names[2]].value + '</span></p><p>Сумма:<span> ' + fields[names[4]].value + ' ₴</span></p></div></div></div>';
        }
        $('#completed').html(html);
    });
}

function getUndoneDeals(dat) {
    let json = dat || null;
    let search = document.getElementsByName('fullsearch')[0].value;
    if (search) {
        search = '&search=' + search;
    } else {
        search = '';
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/deals/?done=3' + search, json, function (data) {
        let count = data.count;
        data = data.results;
        let page = dat['page'] || 1,
            pages = Math.ceil(count / config.pagination_count),
            html = '';
        if (data.length == 0) {
            $('#incomplete').html('<p class="info">Сделок нету</p>');
            $('#incomplete-count').html('0');
            $('.undone-pagination').each(function (el) {
                $(el).html('');
                $(el).css('display', 'none');
            });
            return;
        }
        $('#incomplete-count').html(count);
        let container = ".undone-pagination",
            target = ".undone-pagination .pag li",
            arrow = ".undone-pagination .arrow",
            active = ".undone-pagination .pag li.active",
            dblArrow = ".undone-pagination .double_arrow";
        makePagination(page, container, target, arrow, active, dblArrow, pages, data.length, count, getUndoneDeals);

        for (let i = 0; i < data.length; i++) {
            let fields = data[i].fields;
            if (!fields) {
                continue
            }
            let names = Object.keys(fields);
            html += '<div class="rows-wrap"><button data-id=' + fields[names[0]].value + ' data-name="' + fields[names[1]].value + '" data-date=' + fields[names[3]].value + ' data-responsible="' + fields[names[2]].value + '" data-value=' + fields[names[4]].value + '>Завершить</button><div class="rows"><div class="col"><p><span>' + fields[names[1]].value + '</span></p></div><div class="col"><p>Последняя сделка:<span> ' + fields[names[3]].value + '</span></p><p>Ответственный:<span> ' + fields[names[2]].value + '</span></p><p>Сумма:<span> ' + fields[names[4]].value + ' ₴</span></p></div></div></div>';
            document.getElementById('incomplete').innerHTML = html;
        }
        let but = document.querySelectorAll(".rows-wrap button");
        for (let j = 0; j < but.length; j++) {
            but[j].addEventListener('click', function () {
                getDataForPopup(this.getAttribute('data-id'), this.getAttribute('data-name'), this.getAttribute('data-date'), this.getAttribute('data-responsible'), this.getAttribute('data-value') + ' ₴')
            })
        }
    });
}

function makePagination(page, container, target, arrow, active, dblArrow, pages, length, count, callback) {
    let pagination = '<div class="element-select"><p>Показано <span>' + length + '</span> из <span>' + count + '</span></p></div><div class="pag-wrap">';

    if (page > 1) {
        pagination += '<div class="prev"><span class="double_arrow"></span><span class="arrow"></span></div>';
    }

    if (pages > 1) {
        pagination += '<ul class="pag">';

        if (page > 4) {
            pagination += '<li>1</li><li class="no-pagin">&hellip;</li>'
        }

        for (let j = page - 2; j < page + 3; j++) {


            if (j == page) {
                pagination += '<li class="active">' + j + '</li>'
            } else {
                if (j > 0 && j < pages + 1) {
                    pagination += '<li>' + j + '</li>'
                }
            }

        }
        if (page < pages - 3) {
            pagination += '<li class="no-pagin">&hellip;</li>';

            if (page < pages - 3) {
                pagination += '<li>' + pages + '</li>'
            }


        }
        pagination += '</ul>'
    }

    if (page < pages) {
        pagination += '</ul><div class="next"><span class="arrow"></span></div>'
    }
    Array.prototype.forEach.call(document.querySelectorAll(container), function (el) {
        el.innerHTML = pagination;
        //el.style.display = 'block';
    });

    Array.prototype.forEach.call(document.querySelectorAll(target), function (el) {
        el.addEventListener('click', function () {
            if (this.className == 'no-pagin') {
                return false;
            }
            setClickToPagination(this, callback);
        });
    });
    Array.prototype.forEach.call(document.querySelectorAll(arrow), function (el) {
        el.addEventListener('click', function () {
            arrowClick(this, active, pages, callback);
        })
    });
}

function dblArrowClick(parent, pages) {
    let data = {};
    if ($(parent).parent().hasClass('prev')) {
        console.log($(parent).parent().hasClass('prev'));
        data['page'] = 1;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        getDoneDeals(data);
    } else {
        console.log($(parent).parent().hasClass('prev'));
        data['page'] = pages;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        getDoneDeals(data);
    }
}

function arrowClick(parent, target, pages, callback) {
    let page;
    let data = {};
    if ($(parent).parent().hasClass('prev')) {
        page = parseInt($(target).html() > 1 ? parseInt(document.querySelector(target).html()) - 1 : 1);
        data['page'] = page;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        callback(data);
    } else {
        page = parseInt($(target).html() != pages ? parseInt($(target).html()) + 1 : pages);
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        data['page'] = page;
        callback(data);
    }
}

function setClickToPagination(target, callback) {
    let data = {};
    data['page'] = $(target).html();
    callback(data);
}

function getDataForPopup(id, name, date, responsible, value) {
    $('#complete').attr('data-id', id);
    $('#client-name').html(name);
    $('#deal-date').html(date);
    $('#responsible-name').html(responsible);
    $('#deal-value').val(value);
    $('#popup').css('display', 'block');
}

function init() {
    let json = {};
    json["page"] = '1';
    getExpiredDeals(json);
    getDoneDeals(json);
    getUndoneDeals(json);
}

function updateDeals(deal, value, description) {
    let data = {
        "done": true,
        "value": value,
        "description": description
    };
    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/deals/' + deal + '/', json, function () {
        init();
        document.getElementById('popup').style.display = '';
    }, 'PATCH', true, {
        'Content-Type': 'application/json'
    }, {
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        }
    });

}

function sortDoneDeals(from, to) {
    let json = {};
    json["to_date"] = to;
    json["from_date"] = from;
    getDoneDeals(json);
}

function sortExpiredDeals(from, to) {
    let json = {};
    json["to_date"] = to;
    json["from_date"] = from;
    getExpiredDeals(json);
}

function makeTabs() {
    let pos = 0,
        tabs = document.getElementById('tabs'),
        tabsContent = document.getElementsByClassName('tabs-cont');

    for (let i = 0; i < tabs.children.length; i++) {
        tabs.children[i].setAttribute('data-page', pos);
        pos++;
    }

    showPage(0);

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

// function getCurrentPartnerSetting(data) {
//     let html = '';
//     data.forEach(function (d) {
//         let titles = d[1],
//             ischeck,
//             isdraggable;
//         html += '<h3>' + d[0] + '</h3>';
//         for (let p in titles) {
//             if (!titles.hasOwnProperty(p)) continue;
//             ischeck = titles[p]['active'] ? 'check' : '';
//             isdraggable = titles[p]['editable'] ? 'draggable' : 'disable';
//             html += '<li ' + isdraggable + ' >' +
//                 '<input id="' + titles[p]['ordering_title'] + '" type="checkbox">' +
//                 '<label for="' + titles[p]['ordering_title'] + '"  class="' + ischeck + '" id= "' + titles[p]['id'] + '">' + titles[p]['title'] + '</label>';
//             if (isdraggable == 'disable') {
//                 html += '<div class="disable-opacity"></div>'
//             }
//             html += '</li>'
//         }
//     });
//
//     $('#sort-form').html(html);
//
//     $("#sort-form label").on('click', function () {
//         if (!$(this).parent().attr('disable')) {
//             $(this).hasClass('check') ? $(this).removeClass('check') : $(this).addClass('check');
//         }
//     })
//
// }

function getCurrentPartnerSetting(data) {
    console.log(data);
    let sortFormTmpl, obj, rendered;
    sortFormTmpl = document.getElementById("sortForm").innerHTML;
    obj = {};
    obj.user = data;
    console.log(obj);
    rendered = _.template(sortFormTmpl)(obj);
    document.getElementById('sort-form').innerHTML = rendered;
}


function getPartnersList(param = {}) {

    let path = config.DOCUMENT_ROOT + 'api/v1.1/partnerships/?';
    let search = document.getElementsByName('fullsearch')[0].value;
    let ordering = param.ordering || 'user__last_name';

    if (search) {
        param['search'] = search;
    }

    $('.preloader').css('display', 'block');

    ajaxRequest(path, param, function (data) {

        let results = data.results;

        let k;
        let value;

        let count = data.count;
        let common_fields = data.common_table;
        let user_fields = data.user_table;

        getCurrentPartnerSetting(['Пользователь', user_fields]);

        let thead = '<thead><tr>';
        for (k in user_fields) {
            if (!user_fields.hasOwnProperty(k) || !user_fields[k].active) continue;
            if (ordering.indexOf('user__' + user_fields[k]['ordering_title']) != -1) {
                thead += '<th data-order="' + ordering + '">' + user_fields[k]['title'] + '</th>'
            } else {
                thead += '<th data-order="user__' + user_fields[k]['ordering_title'] + '">' + user_fields[k]['title'] + '</th>'
            }
        }
        for (k in common_fields) {
            if (!common_fields.hasOwnProperty(k) || !common_fields[k].active) continue;
            if (ordering.indexOf(common_fields[k]['ordering_title']) != -1) {
                thead += '<th data-order="' + ordering + '">' + common_fields[k]['title'] + '</th>'
            } else {
                thead += '<th data-order="' + common_fields[k]['ordering_title'] + '">' + common_fields[k]['title'] + '</th>'
            }
        }
        thead += '</tr></thead>';

        let tbody = '<tbody>';
        results.forEach(function (field, i) {
            tbody += '<tr>';

            for (k in user_fields) {
                if (!user_fields.hasOwnProperty(k) || !user_fields[k].active) continue;
                value = getCorrectValue(field['user'][k]);
                if (k === 'fullname') {
                    tbody += '<td>' + '<a href="' + results[i].user.link + '">' + value + '</a></td>'
                } else if (k === 'social') {
                    tbody += '<td>';
                    if (results[i].user.skype) {
                        tbody += '<a href="skype:' + results[i].user.skype + '?chat"><i class="fa fa-skype"></i></a>';
                    }
                    if (results[i].user.vkontakte) {
                        tbody += '<a href="' + results[i].user.vkontakte + '"><i class="fa fa-vk"></i></a>';
                    }
                    if (results[i].user.facebook) {
                        tbody += '<a href="' + results[i].user.facebook + '"><i class="fa fa-facebook"></i></a>';
                    }
                    if (results[i].user.odnoklassniki) {
                        tbody += '<a href="' + results[i].user.odnoklassniki + '"><i class="fa fa-odnoklassniki" aria-hidden="true"></i></a>';
                    }
                    tbody += '</td>';
                } else {
                    tbody += '<td>' + value + '</td>'
                }
            }

            for (k in common_fields) {
                if (!common_fields.hasOwnProperty(k) || !common_fields[k].active) continue;
                if (results[i].is_responsible && (k == 'count' || k == 'result_value')) {
                    value = getCorrectValue(field['disciples_' + k]);
                } else {
                    value = getCorrectValue(field[k]);
                }
                tbody += '<td>' + value + '</td>'
            }
            tbody += '</tr>';
        });
        tbody += '</tbody>';

        let table = '<table>' + thead + tbody + '</table>';


        // debugger

        let page = parseInt(param['page']) || 1;
        let pages = Math.ceil(count / config.pagination_patrnership_count);
        let paginations = '',
            elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
        if (page > 1) {
            paginations += '<div class="prev"></span><span class="arrow"></span></div>';
        }
        if (pages > 1) {
            paginations += '<ul class="pag">';

            if (page > 4) {
                paginations += '<li>1</li><li class="no-pagin">&hellip;</li>'
            }

            for (let j = page - 2; j < page + 3; j++) {


                if (j == page) {
                    paginations += '<li class="active">' + j + '</li>'
                } else {
                    if (j > 0 && j < pages + 1) {
                        paginations += '<li>' + j + '</li>'
                    }
                }

            }
            if (page < pages - 3) {
                paginations += '<li class="no-pagin">&hellip;</li>';

                if (page < pages - 3) {
                    paginations += '<li>' + pages + '</li>'
                }


            }
            paginations += '</ul>'
        }

        if (page < pages) {
            paginations += '</ul><div class="next"><span class="arrow"></span></div>'
        }

        if (results.length) {
            $("#spisok .element-select").html(elementSelect);
            $('#partnersips_list').html(table);
            $(".query-none p").html('');
        } else {
            $('#partnersips_list').html('');
            $(".query-none p").html('По запросу не найдено участников');
            $("#spisok .element-select").html('<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>');
        }
    var orderTable = (function () {
        function addListener() {
            $(".table-wrap th").on('click', function () {
                let dataOrder;
                let data_order = this.getAttribute('data-order');
                var revers = (sessionStorage.getItem('revers')) ? sessionStorage.getItem('revers') : "+";
                var order = (sessionStorage.getItem('order')) ? sessionStorage.getItem('order') : '';
                if (order != '') {
                    dataOrder = (order == data_order && revers == "+") ? '-' + data_order : data_order;
                } else {
                    dataOrder = '-' + data_order;
                }
                ordering = {};
                ordering[data_order] = dataOrder;
                let page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1;
                let data = {
                    'ordering': dataOrder,
                    'page': page
                };
                if (order == data_order) {
                    revers = (revers == '+') ? '-' : '+';
                } else {
                    revers = "+"
                }
                sessionStorage.setItem('revers', revers);
                sessionStorage.setItem('order', data_order);

                getPartnersList(data);
            });
        }

        return {
            addListener: addListener
        }
    })();
    orderTable.addListener();
        $('.preloader').css('display', 'none');
        $("#spisok .pag-wrap").each(function () {
            $(this).html(paginations);
        });
        $("#spisok .pag li").on('click', function () {
            let data = {};
            if ($(this).hasClass('no-pagin')) {
                return false;
            }
            data['page'] = $(this).html();
            getPartnersList(data);
        });


        /* Navigation*/

        $("#spisok .arrow").on('click', function () {
            let page;
            let data = {};
            if ($(this).parent().hasClass('prev')) {
                page = parseInt($(".pag li.active").html()) > 1 ? parseInt($(".pag li.active").html()) - 1 : 1;
                data['page'] = page;
                getPartnersList(data);
            } else {
                page = parseInt($("#spisok .pag li.active").html()) != pages ? parseInt($(".pag li.active").html()) + 1 : pages;
                data['page'] = page;
                getPartnersList(data);
            }
        });

        $("#spisok .double_arrow").on('click', function () {
            let data = {};
            if ($(this).parent().hasClass('prev')) {
                data['page'] = 1;
                getPartnersList(data);
            } else {
                data['page'] = pages;
                getPartnersList(data);
            }
        })
    });

    if (config.user_partnerships_info && config.user_partnerships_info.is_responsible) {
        $('#add_user_parners').css('display', 'block');
    }

}