$(document).ready(function () {

    //partnerlist 
    //getPartnersList();

    $('input[name="fullsearch"]').keyup(function () {

        delay(function () {
            getPartnersList()
        }, 1500);
    });

    document.getElementById('sort_save').addEventListener('click', function () {
        updateSettings(getPartnersList);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });

    $.datepicker.setDefaults($.datepicker.regional["ru"]);

    $("#done_datepicker_from").datepicker({
        dateFormat: "yy-mm-dd",
        maxDate: new Date(),
        onSelect: function (date) {
            window.done_from_date = date;
            sortDoneDeals(done_from_date, done_to_date);
        }
    }).datepicker("setDate", '-1m');

    $("#done_datepicker_to").datepicker({
        dateFormat: "yy-mm-dd",
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
        var attr = this.getAttribute('data-id'),
            value = document.getElementById('deal-value').value;
        var reg = /^\d{1,5} ?₴?$/gi;
        if (!reg.test(value)) {
            showPopup('Введите правильное значение суммы');
            return;
        }
        updateDeals(attr, parseInt(value));
        document.getElementById('deal-value').setAttribute('readonly', 'readonly');
    });

    document.getElementById('changeSum').addEventListener('click', function () {
        document.getElementById('deal-value').removeAttribute('readonly');
        document.getElementById('deal-value').focus();
    });

    /*add parnership*/
    document.querySelector(".add").addEventListener('click', function () {
        document.querySelector('.add-user-wrap').style.display = 'block';
    });


    document.querySelector(".add-user-wrap .top-text span").addEventListener('click', function () {
        document.querySelector('.add-user-wrap').style.display = 'none';
    });


    document.getElementById('choose').addEventListener('click', function () {
        document.querySelector('.choose-user-wrap').style.display = 'block';
        document.querySelector('.add-user-wrap').style.display = 'none';
    });


    /*
     document.querySelector('.choose-user-wrap h3 span').addEventListener('click', function() {
     document.getElementById('searchUsers').value = '';
     document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
     document.querySelector('.choose-user-wrap').style.display = 'none';
     document.querySelector('.add-user-wrap').style.display = 'block';
     })
     */

    document.querySelector(".choose-user-wrap .top-text > span").addEventListener('click', function () {
        document.getElementById('searchUsers').value = '';
        document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
        document.querySelector('.choose-user-wrap').style.display = '';
    });


    $('#searchUsers').keyup(function () {
        getUnregisteredUsers();
    });


});

var done_from_date = '',
    done_to_date = '',
    expired_from_date = '',
    expired_to_date = '';

init();


function getUnregisteredUsers(parameters) {
    var param = parameters || {};
    var search = document.getElementById('searchUsers').value;
    if (search) {
        param['search'] = search;
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/partnerships_unregister_search/', param, function (data) {
        var html = '';
        for (var i = 0; i < data.length; i++) {
            html += '<div class="rows-wrap"><button data-id=' + data[i].id + '>Выбрать</button><div class="rows"><div class="col"><p><span><a href="/account/' + data[i].id + '">' + data[i].fullname + '</a></span></p></div><div class="col"></div></div></div>';
        }
        if (data.length > 0) {
            document.getElementById('searchedUsers').innerHTML = html;
        } else {
            document.getElementById('searchedUsers').innerHTML = '<div class="rows-wrap"><div class="rows"><p>По запросу не найдено учасников</p></div></div>';
        }
        document.querySelector('.choose-user-wrap .splash-screen').classList.add('active');
        var but = document.querySelectorAll('.rows-wrap button');
        for (var j = 0; j < but.length; j++) {
            but[j].addEventListener('click', function () {
                var id = this.getAttribute('data-id');
                registerUser(id);
            })
        }
    });
}
function registerUser(id) {
    if (!id) {
        return
    }
    var money = 0;


    var dateObj = new Date();
    var month = dateObj.getUTCMonth() + 1; //months from 1-12
    var day = dateObj.getUTCDate();
    var year = dateObj.getUTCFullYear();

    newdate = year + "-" + month + "-" + day;

    var data = {'date': newdate, 'user': parseInt(id)};
    data.value = money;
    data.responsible = config.user_partnerships_info.responsible;
    if (data.responsible) {
        create_partnerships(data)
    }
}


function create_partnerships(data) {


    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/create_partnership', json, function (JSONobj) {

        if (JSONobj.status) {
            $(".choose-user-wrap").hide();
            showPopup(JSONobj.message);
            //partners_initialize();
        } else {
            showPopup(JSONobj.message);
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });

}


function getExpiredDeals(time) {
    var json = time || null;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/deals/?expired=2', json, function (data) {
        var count = data.count;
        data = data.results;
        var page = time['page'] || 1,
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
        var container = ".expired-pagination",
            target = ".expired-pagination .pag li",
            arrow = ".expired-pagination .arrow",
            active = ".expired-pagination .pag li.active",
            dblArrow = ".expired-pagination .double_arrow";
        makePagination(page, container, target, arrow, active, dblArrow, pages, data.length, count, getExpiredDeals);
        for (var i = 0; i < data.length; i++) {
            var fields = data[i].fields;
            if (!fields) {
                continue
            }
            names = Object.keys(fields);
            html += '<div class="rows-wrap"><button data-id=' + fields[names[0]].value + '>Завершить</button><div class="rows"><div class="col"><p><span>' + fields[names[1]].value + '</span></p></div><div class="col"><p>Последняя сделка:<span> ' + fields[names[3]].value + '</span></p><p>Ответственный:<span> ' + fields[names[2]].value + '</span></p><p>Сумма:<span> ' + fields[names[4]].value + ' ₴</span></p></div></div></div>';
        }
        document.getElementById('overdue').innerHTML = html;
        var but = document.querySelectorAll(".rows-wrap button");
        for (var j = 0; j < but.length; j++) {
            but[j].addEventListener('click', function () {
                getDataForPopup(this.getAttribute('data-id'), this.getAttribute('data-name'), this.getAttribute('data-date'), this.getAttribute('data-responsible'), this.getAttribute('data-value') + ' ₴')
            })
        }
    });
}

function getDoneDeals(time) {
    var json = time || null;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/deals/?done=2', json, function (data) {
        var count = data.count;
        data = data.results;
        var page = time['page'] || 1,
            pages = Math.ceil(count / config.pagination_count),
            html = '';
        if (data.length == 0) {
            document.getElementById('completed').innerHTML = '<p class="info">Сделок нету</p>';
            document.getElementById('completed-count').innerHTML = '0';
            Array.prototype.forEach.call(document.querySelectorAll('.done-pagination'), function (el) {
                el.innerHTML = '';
                el.style.display = 'none';
            });
            return;
        }
        document.getElementById('completed-count').innerHTML = count;

        var container = ".done-pagination",
            target = ".done-pagination .pag li",
            arrow = ".done-pagination .arrow",
            active = ".done-pagination .pag li.active",
            dblArrow = ".done-pagination .double_arrow";
        makePagination(page, container, target, arrow, active, dblArrow, pages, data.length, count, getDoneDeals);
        for (var i = 0; i < data.length; i++) {
            var fields = data[i].fields;
            if (!fields) {
                continue
            }
            names = Object.keys(fields);
            html += '<div class="rows-wrap"><div class="rows"><div class="col"><p><span>' + fields[names[1]].value + '</span></p></div><div class="col"><p>Последняя сделка:<span> ' + fields[names[3]].value + '</span></p><p>Ответственный:<span> ' + fields[names[2]].value + '</span></p><p>Сумма:<span> ' + fields[names[4]].value + ' ₴</span></p></div></div></div>';

        }
        document.getElementById('completed').innerHTML = html;
    });
}

function getUndoneDeals(dat) {
    var json = dat || null;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/deals/?done=3', json, function (data) {
        var count = data.count;
        data = data.results;
        var page = dat['page'] || 1,
            pages = Math.ceil(count / config.pagination_count),
            html = '';
        if (data.length == 0) {
            document.getElementById('incomplete').innerHTML = '<p class="info">Сделок нету</p>';
            document.getElementById('incomplete-count').innerHTML = '0';
            Array.prototype.forEach.call(document.querySelectorAll('.undone-pagination'), function (el) {
                el.innerHTML = '';
                el.style.display = 'none';
            });
            return;
        }
        document.getElementById('incomplete-count').innerHTML = count;
        var container = ".undone-pagination",
            target = ".undone-pagination .pag li",
            arrow = ".undone-pagination .arrow",
            active = ".undone-pagination .pag li.active",
            dblArrow = ".undone-pagination .double_arrow";
        makePagination(page, container, target, arrow, active, dblArrow, pages, data.length, count, getUndoneDeals);

        for (var i = 0; i < data.length; i++) {
            var fields = data[i].fields;
            if (!fields) {
                continue
            }
            names = Object.keys(fields);
            html += '<div class="rows-wrap"><button data-id=' + fields[names[0]].value + ' data-name="' + fields[names[1]].value + '" data-date=' + fields[names[3]].value + ' data-responsible="' + fields[names[2]].value + '" data-value=' + fields[names[4]].value + '>Завершить</button><div class="rows"><div class="col"><p><span>' + fields[names[1]].value + '</span></p></div><div class="col"><p>Последняя сделка:<span> ' + fields[names[3]].value + '</span></p><p>Ответственный:<span> ' + fields[names[2]].value + '</span></p><p>Сумма:<span> ' + fields[names[4]].value + ' ₴</span></p></div></div></div>';
            document.getElementById('incomplete').innerHTML = html;
        }
        var but = document.querySelectorAll(".rows-wrap button");
        for (var j = 0; j < but.length; j++) {
            but[j].addEventListener('click', function () {
                getDataForPopup(this.getAttribute('data-id'), this.getAttribute('data-name'), this.getAttribute('data-date'), this.getAttribute('data-responsible'), this.getAttribute('data-value') + ' ₴')
            })
        }
    });
}

function makePagination(page, container, target, arrow, active, dblArrow, pages, length, count, callback) {
    var pagination = '<div class="element-select"><p>Показано <span>' + length + '</span> из <span>' + count + '</span></p></div><div class="pag-wrap">';

    if (page > 1) {
        pagination += '<div class="prev"><span class="double_arrow"></span><span class="arrow"></span></div>';
    }

    if (pages > 1) {
        pagination += '<ul class="pag">';

        if (page > 4) {
            pagination += '<li>1</li><li class="no-pagin">&hellip;</li>'
        }

        for (var j = page - 2; j < page + 3; j++) {


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
    var data = {};
    if (parent.parentElement.classList.contains('prev')) {
        data['page'] = 1;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        getDoneDeals(data);
    } else {
        data['page'] = pages;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        getDoneDeals(data);
    }
}

function arrowClick(parent, target, pages, callback) {
    var page;
    var data = {};
    if (parent.parentElement.classList.contains('prev')) {
        page = parseInt(document.querySelector(target).innerHTML) > 1 ? parseInt(document.querySelector(target).innerHTML) - 1 : 1;
        data['page'] = page;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        callback(data);
    } else {
        page = parseInt(document.querySelector(target).innerHTML) != pages ? parseInt(document.querySelector(target).innerHTML) + 1 : pages;
        data["to_date"] = done_to_date;
        data["from_date"] = done_from_date;
        data['page'] = page;
        callback(data);
    }
}

function setClickToPagination(target, callback) {
    var data = {};
    data['page'] = target.innerHTML;
    callback(data);
}

function getDataForPopup(id, name, date, responsible, value) {
    document.getElementById('complete').setAttribute('data-id', id);
    document.getElementById('client-name').innerHTML = name;
    document.getElementById('deal-date').innerHTML = date;
    document.getElementById('responsible-name').innerHTML = responsible;
    document.getElementById('deal-value').value = value;
    document.getElementById('popup').style.display = 'block';
}

function init() {
    var json = {};
    json["page"] = '1';
    getExpiredDeals(json);
    getDoneDeals(json);
    getUndoneDeals(json);
}

function updateDeals(deal, value) {
    var data = {
        "id": deal,
        "done": true,
        "value": value
    };
    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/update_deal', json, function () {
        init();
        document.getElementById('popup').style.display = '';
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });

}

function sortDoneDeals(from, to) {
    var json = {};
    json["to_date"] = to;
    json["from_date"] = from;
    getDoneDeals(json);
}

function sortExpiredDeals(from, to) {
    var json = {};
    json["to_date"] = to;
    json["from_date"] = from;
    getExpiredDeals(json);
}


function makeTabs() {
    var pos = 0,
        tabs = document.getElementById('tabs'),
        tabsContent = document.getElementsByClassName('tabs-cont');

    for (var i = 0; i < tabs.children.length; i++) {
        tabs.children[i].setAttribute('data-page', pos);
        pos++;
    }

    showPage(0);

    tabs.onclick = function (event) {
        event.preventDefault();
        return showPage(parseInt(event.target.parentElement.getAttribute("data-page")));
    };

    function showPage(i) {
        for (var k = 0; k < tabsContent.length; k++) {
            tabsContent[k].style.display = 'none';
            tabs.children[k].classList.remove('current');
        }
        tabsContent[i].style.display = 'block';
        tabs.children[i].classList.add('current');
        var done = document.getElementById('period_done'),
            expired = document.getElementById('period_expired');
        unpag = document.querySelectorAll('.undone-pagination');
        expag = document.querySelectorAll('.expired-pagination');
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


function getPartnersList(param) {
    param = param || {};

    var lib = {
        "value": "Cумма",
        "responsible": "Ответственный",
        "count": "Количество сделок",
        "result_value": "Итого"
    };
    var path = config.DOCUMENT_ROOT + 'api/partnerships/?';
    var search = document.getElementsByName('fullsearch')[0].value;
    if (search) {
        param['search'] = search;
    }

    document.getElementsByClassName('preloader')[0].style.display = 'block';
    ajaxRequest(path, param, function (data) {

        var results = data.results;

        var count = data.count;
        var common_fields = data.common_table;
        var html = '';
        var thead = '<table><thead><tr>';

        var orders_columns = Object.keys(config['column_table']).concat(Object.keys(common_fields)).unique();

        for (var i = 0; i < results.length; i++) {


            html += '<tr>';
            var field = results[i].fields;

            if (!field) {
                //console.log('run')
                continue
            }


            for (var x = 0; x < orders_columns.length; x++) {

                j = orders_columns[x];

                /*
                 if(  !field   ){
                 console.log('run')
                 continue
                 }
                 */
                var id_ = field['id']['value'];

                if (!common_fields[j] && (!config['column_table'][j] || !config['column_table'][j]['active']   )) continue;
                if (!i) {

                    //console.log(j)
                    if (j == 'responsible' || j == 'value' || j == 'count' || j == 'result_value') {
                        thead += '<th data-order="' + j + '">' + lib[j] + '</th>'
                    } else {

                        thead += '<th data-order="user__' + config['column_table'][j]['ordering_title'] + '">' + config['column_table'][j]['title'] + '</th>'
                    }
                }
                console.log(lib);
                if (j == 'social' && config['column_table']['social'] && config['column_table']['social']['active']) {
                    html += '<td>';
                    for (var p in field[j]) {
                        if (field[j][p] == '') {
                        } else {
                            switch (p) {
                                case 'skype':
                                    html += '<a href="skype:' + field[j].skype + '?chat"><i class="fa fa-skype"></i></a>';
                                    break;
                                case 'vkontakte':
                                    html += '<a href="' + field[j].vkontakte + '"><i class="fa fa-vk"></i></a>';
                                    break;
                                case 'facebook':
                                    html += '<a href="' + field[j].facebook + '"><i class="fa fa-facebook"></i></a>';
                                    break;
                                case 'odnoklassniki':
                                    html += '<a href="' + field[j].odnoklassniki + '"><i class="fa fa-odnoklassniki" aria-hidden="true"></i></a>';
                                    break;
                            }
                        }
                    }
                    html += '</td>';
                } else if (j == 'fullname') {
                    //debugger

                    html += '<td><a href="/account/' + id_ + '">' + field[j]['value'] + '</a></td>'
                } else {
                    html += '<td>' + field[j]['value'] + '</td>';
                }
                //html += '<td data-model="' + j + '">' + field[j].value + '</td>'
                // }
            }
            html += '</tr>';
            thead += '</tr></thead><tbody></tbody></table>';


        }

        // debugger

        var page = parseInt(param['page']) || 1;
        var pages = Math.ceil(count / config.pagination_patrnership_count);
        var paginations = '',
            elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
        if (page > 1) {
            paginations += '<div class="prev"></span><span class="arrow"></span></div>';
        }
        if (pages > 1) {
            paginations += '<ul class="pag">';

            if (page > 4) {
                paginations += '<li>1</li><li class="no-pagin">&hellip;</li>'
            }

            for (var j = page - 2; j < page + 3; j++) {


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

            document.querySelector("#spisok .element-select").innerHTML = elementSelect;
            document.getElementById('partnersips_list').innerHTML = thead;
            document.querySelector("#partnersips_list tbody").innerHTML = html;
            document.querySelector(".query-none p").innerHTML = '';

            //  document.querySelector(".element-select span").innerHTML = results.length;
            //  document.querySelector(".element-select span + span").innerHTML = count;

        } else {
            document.getElementById('partnersips_list').innerHTML = '';
            document.querySelector(".query-none p").innerHTML = 'По запросу не найдено участников';
            document.querySelector("#spisok .element-select").innerHTML = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>'
        }


        document.getElementsByClassName('preloader')[0].style.display = 'none';
        Array.prototype.forEach.call(document.querySelectorAll("#spisok .pag-wrap"), function (el) {
            el.innerHTML = paginations
        });

        Array.prototype.forEach.call(document.querySelectorAll("#spisok .pag li"), function (el) {
            el.addEventListener('click', function () {
                if (this.className == 'no-pagin') {
                    return false;
                }
                var data = {};
                data['page'] = el.innerHTML;
                getPartnersList(data);
            });
        });


        /* Navigation*/

        Array.prototype.forEach.call(document.querySelectorAll("#spisok .arrow"), function (el) {
            el.addEventListener('click', function () {
                var page;
                var data = {};
                if (this.parentElement.classList.contains('prev')) {
                    page = parseInt(document.querySelector(".pag li.active").innerHTML) > 1 ? parseInt(document.querySelector(".pag li.active").innerHTML) - 1 : 1;
                    data['page'] = page;
                    getPartnersList(data);
                } else {

                    page = parseInt(document.querySelector("#spisok .pag li.active").innerHTML) != pages ? parseInt(document.querySelector(".pag li.active").innerHTML) + 1 : pages;
                    data['page'] = page;
                    getPartnersList(data);
                }
            })
        });

        Array.prototype.forEach.call(document.querySelectorAll("#spisok .double_arrow"), function (el) {
            el.addEventListener('click', function () {
                var data = {};
                if (this.parentElement.classList.contains('prev')) {
                    data['page'] = 1;
                    getPartnersList(data);
                } else {
                    data['page'] = pages;
                    getPartnersList(data);
                }
            })
        });


        /*
         Array.prototype.forEach.call(document.querySelectorAll(".table-wrap   th"), function(el) {
         el.addEventListener('click', function() {

         //Переписать модуль order
         var data_order = this.getAttribute('data-order');
         //  var status = ordering[data_order] = ordering[data_order] ? false : true
         var status = false;
         if (ordering[data_order]) {
         status = false;
         } else {
         status = true
         }
         ordering = {};
         ordering[data_order] = status
         data_order = status ? data_order : '-' + data_order;
         var page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1

         var data = {
         'ordering': data_order,
         'page': page
         }
         //Problem
         getPartnersList(data)
         });
         })
         */
        if (config.user_partnerships_info && config.user_partnerships_info.is_responsible) {
            document.getElementById('add_user_parners').style.display = 'block'
        }
    })
}

var ordering = {};
