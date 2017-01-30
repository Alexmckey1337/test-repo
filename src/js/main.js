const CONFIG = {
    // 'DOCUMENT_ROOT': 'http://vocrm.org/',
    'DOCUMENT_ROOT': '/',
    'pagination_count': 30, //Количество записей при пагинации
    'pagination_patrnership_count': 30, //Количество записей при пагинации for patrnership
    'column_table': null
};

var VOCRM = {};

counterNotifications();

// Sorting
    var orderTable = (function () {
        function addListener(callback) {
            $(".table-wrap th").on('click', function () {
                let dataOrder;
                let data_order = this.getAttribute('data-order');
                let page = $('.pagination__input').val();
                let revers = (sessionStorage.getItem('revers')) ? sessionStorage.getItem('revers') : "+";
                let order = (sessionStorage.getItem('order')) ? sessionStorage.getItem('order') : '';
                if (order != '') {
                    dataOrder = (order == data_order && revers == "+") ? '-' + data_order : data_order;
                } else {
                    dataOrder = '-' + data_order;
                }
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
                $('.preloader').css('display', 'block');
                callback(data);
            });
        }

        return {
            sort: addListener
        }
    })();

function makeDataTable(data, id) {
    var tmpl = document.getElementById('databaseUsers').innerHTML;
    var rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        makeQuickEditCart(this);
    })
}

function makeSortForm(data) {
    let sortFormTmpl, obj, rendered;
    sortFormTmpl = document.getElementById("sortForm").innerHTML;
    obj = {};
    obj.user = [];
    obj.user.push("Фильтр");
    obj.user.push(data);
    console.log(obj);
    rendered = _.template(sortFormTmpl)(obj);
    document.getElementById('sort-form').innerHTML = rendered;
    }

function makeResponsibleList() {
    let department = $('#departmentSelect').val();
    let hierarchy = $('#hierarchySelect option:selected').attr('data-level');
    getResponsible(department, hierarchy).then(function (data) {
        let id = $('#master_hierarchy option:selected').attr('data-id');
        if(!id) {
            id = $('#master_hierarchy option').attr('data-id');
        }
        var selected = false;
        var html = "";
        data.forEach(function (el) {
            if (id == el.id) {
                selected = true;
                html += "<option data-id='" + el.id + "' selected>" + el.fullname + "</option>";
            } else {
                html += "<option data-id='" + el.id + "'>" + el.fullname + "</option>";
            }
        });
        if (!selected) {
            html += "<option selected disabled>Выберите ответственного</option>";
        }
        html += "";
        $("#master_hierarchy").html(html).select2();
    });
}

var makeChooseDivision = getDivisions().then(function (data) {
            data = data.results;
            let html = '';
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
            return html
        });

function saveUser(el) {
    let $input, $select, fullName, first_name, last_name, middle_name, data, id;
    let master_id = $('#master_hierarchy option:selected').attr('data-id') || "";
    fullName = $($(el).closest('.pop_cont').find('input.fullname')).val().split(' ');
    first_name = fullName[1];
    last_name = fullName[0];
    middle_name = fullName[2] || "";
    data = {
        email: $($(el).closest('.pop_cont').find('#email')).val(),
        first_name: first_name,
        last_name: last_name,
        middle_name: middle_name,
        hierarchy: $($(el).closest('.pop_cont').find('#hierarchySelect')).val(),
        department: $($(el).closest('.pop_cont').find('#departmentSelect')).val(),
        master: master_id,
        skype: $($(el).closest('.pop_cont').find('#skype')).val(),
        phone_number: $($(el).closest('.pop_cont').find('#phone_number')).val(),
        additional_phones: $($(el).closest('.pop_cont').find('#additional_phones')).val(),
        repentance_date: $($(el).closest('.pop_cont').find('#repentance_date')).val(),
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        region: $($(el).closest('.pop_cont').find('#region')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val()
    };
    id = $(el).closest('.pop_cont').find('img').attr('alt');
    saveUserData(data, id);
    $(el).text("Сохранено");
    $(el).closest('.popap').find('.close-popup').text('Закрыть');
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

function makeQuickEditCart(el) {
    let id, link;
    id = $(el).closest('td').find('a').attr('data-id');
    link = $(el).closest('td').find('a').attr('data-link');
    let url = "/api/v1.1/users/" + id + '/';
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
                if (departmentSelect == data[i].title || departmentSelect == data[i].id) {
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
$('.close').on('click', function () {
    $(this).closest('.pop-up-splash').css('display', 'none');
});
$('#logout_button').on('click', function (e) {
    e.preventDefault();
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/logout/', null, function (data) {
        deleteCookie('key');
        window.location.href = '/entry';
    }, 'POST', true, {
        'Content-Type': 'application/json'
    })
});
$('.reset_hard_user').on('click', function (e) {
    deleteCookie('hard_user_id');
    window.location.reload();
});

$('.close_popup').on('click', function () {
    $(this).closest('.popap').css('display', 'none');
});

/*search animate width*/
$('.top input').click(function () {
    $('.top .search').animate({width: "80%"});
});

function hideFilter() {
    if ($('.top input').length && !$('.top input').val().length) {
        $('.top .search').animate({width: "50%"});
    }
}

if (document.getElementById('filter')) {
    $('#filter').select2();
}

if (document.getElementById('sort_save')) {
    document.getElementById('sort_save').addEventListener('click', function () {
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    })
}

function sortSave() {
    document.getElementById('sort_save').addEventListener('click', function () {
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    })
}

$("#pag li ").click(function (e) {
    e.preventDefault();
    $("#pag li").removeClass('active');
    $(this).addClass('active');
});

$("body").on('click', '#pag li', function (e) {
    e.preventDefault();
    $("#pag li").removeClass('active');
    $(this).addClass('active');
});

/*DND columns*/

$("#sort-on").click(function () {
    $(".table-sorting").animate({right: '0'}, 10, 'linear');
    $(".page-width").append(" <div class='bgsort'></div>");
});

$("#sort-off").click(function () {
    $(".table-sorting").animate({right: '-300px'}, 10, 'linear');
    $(".bgsort").remove();
});

$("#sort_save").click(function () {
    $(".table-sorting").animate({right: '-300px'}, 10, 'linear');
    $(".bgsort").remove();
});

$('body').on('click', ".bgsort", function () {
    $(".table-sorting").animate({right: '-300px'}, 10, 'linear');
    $(this).remove();
});

//WTF???
$('#popup').click(function (el) {
    if (el.target !== this) {
        return;
    }
    $(this).hide();
});

//Переписати на нові таби
$('.tabs-nav li').click(function (e) {
    e.preventDefault();
    //console.log(  $(this).index()   )
    $('.tabs-nav li').removeClass('current');
    $(this).addClass('current');
    $('.tab-toggle').hide();
    $('.tab-toggle[data-id="' + $(this).index() + '"]').show();
});

$(".tabs-nav li a:first").click();

$(document).ready(function () {
    $('body').on('mouseover', '.toggle-sidebar a', function (el) {
        //if (el.target.className == '#move-sidebar a') {return};
        if ($(this).parent().is('#move-sidebar')) {
            return
        }
        let hint = '<div id="hint">' + $(this).attr('data-title') + '</hint>';
        $('body').append(hint);
        let a = ($(this).offset().top - $(window).scrollTop()) + ($(this).outerHeight() / 2) - $('#hint').outerHeight() / 2;
        $('#hint').css('top', a).fadeIn();
    });


    $('.editprofile input').keypress(function (el) {
        if (el.charCode == '32' && el.currentTarget.id != 'additional_phone' && el.currentTarget.id != 'address' && el.currentTarget.id != 'search_name') {
            return false
        }
    });

    $('body').on('mouseout', '.toggle-sidebar a', function (el) {
        $('#hint').detach();
    });
    if ($('.scrollbar-inner').length || $('.scrollbar-macosx').length) {
        $('.scrollbar-inner').scrollbar();
        $('.scrollbar-macosx').scrollbar();
    }

    $.extend($.datepicker, {
        _checkOffset: function (inst, offset, isFixed) {
            return offset
        }
    });

    $("#move-sidebar").click(function () {
        if (!$("#sidebar").hasClass('toggle-sidebar')) {
            $("#sidebar").addClass('toggle-sidebar');
            document.cookie = 'state=active;path=/';
        } else {
            $("#sidebar").removeClass('toggle-sidebar')
            deleteCookie('state');
        }
    });

    let loc = window.location.pathname;
    if (~loc.indexOf('event_info')) {
        $("#nav-sidebar li").removeClass('active');
        $("#nav-sidebar li a[href='/events/']").parent().addClass('active');
    } else if (~loc.indexOf('summit_info')) {
        $("#nav-sidebar li").removeClass('active');
        $("#nav-sidebar li a[href='/summits/']").parent().addClass('active');
    } else {
        $("#nav-sidebar li").removeClass('active');
        $("#nav-sidebar li a[href='" + loc + "']").parent().addClass('active');
    }
});

window.onload = function () {
    if (opened('state')) {
        $("#sidebar").addClass('toggle-sidebar');
    } else {
        $("#sidebar").removeClass('toggle-sidebar');
    }
    $('body').show();
};

function opened(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? true : false;
}

function deleteCookie(name) {
    document.cookie = name + '=active;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

//Cкрывать элементы когда клик по другой части области экрана
document.body.addEventListener('click', function (el) {
    if (el.target == document.querySelector(".userImgWrap") || el.target == document.querySelector(".userImgWrap img")) {
        document.querySelector(".photo-hover").style.display == 'block' ? document.querySelector(".photo-hover").style.display = 'none' :
            document.querySelector(".photo-hover").style.display = 'block';
        document.querySelector('.massage-hover').style.display = 'none';
    } else if (el.target == document.querySelector('.sms') || el.target == document.querySelector('.sms span:last-child')) {
        document.querySelector('.massage-hover').style.display == 'block' ? document.querySelector('.massage-hover').style.display = 'none' :
            document.querySelector('.massage-hover').style.display = 'block';
        document.querySelector(".photo-hover").style.display = 'none';
    } else if (el.target == document.querySelector('.top input') || el.target == document.querySelector('#select2-filter-container')) {
        return
    } else {
        document.querySelector('.massage-hover').style.display = 'none';
        document.querySelector(".photo-hover").style.display = 'none';
        hideFilter();
    }
});

$(function () {
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/users/current/', null, function (data) {
        let user_id = data.id;
        VOCRM.user_id = data.id;
        VOCRM.user_partnerships_info = data.partnerships_info;
        VOCRM.column_table = data.column_table;
        let hierarchy_chain = data['hierarchy_chain'];

        // if (document.getElementById('database_users')) {
        //     createUser();
        // }

        if (document.getElementById('users_list')) {
            let dat = {};
            dat['summit'] = document.querySelectorAll('#carousel li span')[0].getAttribute('data-id');
            window.summit_id = dat['summit'];
            getUsersList(path, dat);
            getCurrentSetting();
        }

        if (document.getElementById('event_wrap')) {
            getCurrentSetting();
            init(user_id);
        }

        if (document.getElementById("add_new")) {
            document.getElementById("add_new").setAttribute('data-id', data.id);
        }

        if (document.getElementById("report_wrap")) {
            init_report()
        }

        if (VOCRM.user_partnerships_info && VOCRM.user_partnerships_info.is_responsible && document.querySelector('.manager_view')) {
            document.querySelector('.manager_view').style.display = 'block'
        }

    });
    if (document.getElementById('sort-form')) {
        $("#sort-form").sortable({revert: true, items: "li:not([disable])", scroll: false});
        $("#sort-form").disableSelection();
    }
});

jQuery(function ($) {
    if ($.datepicker) {
        $.datepicker.regional['ru'] = {
            monthNames: ['Январь', 'Февраль', 'Март', 'Апрель',
                'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                'Октябрь', 'Ноябрь', 'Декабрь'
            ],
            monthNamesShort: ['Январь', 'Февраль', 'Март', 'Апрель',
                'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                'Октябрь', 'Ноябрь', 'Декабрь'],
            changeMonth: true,
            changeYear: true,
            dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
            firstDay: 1,
            dateFormat: "yy-mm-dd"
        };
        $.datepicker.setDefaults($.datepicker.regional['ru']);
    }
});

//old version
function getCurrentSetting() {
    let titles = VOCRM['column_table'];
    let html = '';
    for (let p in titles) {
        if (!titles.hasOwnProperty(p)) continue;
        let ischeck = titles[p]['active'] ? 'check' : '';
        let isdraggable = titles[p]['editable'] ? 'draggable' : 'disable';
        html += '<li ' + isdraggable + ' >' +
            '<input id="' + titles[p]['ordering_title'] + '" type="checkbox">' +
            '<label for="' + titles[p]['ordering_title'] + '"  class="' + ischeck + '" id= "' + titles[p]['id'] + '">' + titles[p]['title'] + '</label>';
        if (isdraggable == 'disable') {
            html += '<div class="disable-opacity"></div>'
        }
        html += '</li>'
    }

    document.getElementById('sort-form').innerHTML = html;

    $("#sort-form label").on('click', function (el) {
        if (!this.parentElement.hasAttribute('disable')) {
            this.classList.contains('check') ? this.classList.remove('check') : this.classList.add('check');
        }
    })
}

function createUsersTable(config) {
        config["search_fio"] = $('input[name=fullsearch]').val();
        Object.assign(config, filterParam());
        getUsers(config).then(function (data) {
            let count = data.count;
            let page = config['page'] || 1;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
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
        });
    }

function updateSettings(callback, path) {
    let data = [];
    let iteration = 1;
    $("#sort-form input").each(function () {
        let item = {};
        item['id'] = $(this).val();
        item['number'] = iteration++;
        item['active'] = $(this).prop('checked');
        data.push(item);
    });
    let json = JSON.stringify(data);

    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/update_columns/', json, function (JSONobj) {
        $(".bgsort").remove();
        VOCRM['column_table'] = JSONobj['column_table'];

        if (callback) {
            var param = {};
            if (path !== undefined) {
                let extendParam = $.extend({}, param, filterParam());
                callback(extendParam);
            } else {
                let param = filterParam();
                callback(param);
            }
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function hidePopup(el) {
    $(el).closest('.popap').find('.save-user').text('Сохранить');
    $(el).closest('.popap').find('.save-user').attr('disabled', false);
    $(el).closest('.popap').css('display', 'none');
}

function refreshFilter(el) {
    var input = $(el).closest('.popap').find('input');
    $(el).addClass('refresh');
    setTimeout(function () {
        $(el).removeClass('refresh');
    }, 700);
    Array.from(input).forEach(function (item) {
        $(item).val('')
    })
}

function filterParam() {
    let filterPopup, data = {}, department, hierarchy, master, search_email, search_phone_number, search_country, search_city;
    filterPopup = $('#filterPopup');
    department = parseInt($('#departments_filter').val());
    hierarchy = parseInt($('#hierarchies_filter').val());
    master = parseInt($('#masters_filter').val());
    search_email = $('#search_email').val();
    search_phone_number = $('#search_phone_number').val();
    search_country = $('#search_country').val();
    search_city = $('#search_city').val();

    if (department !== 0) {
        data['department'] = department;
    }
    if (hierarchy !== 0) {
        data['hierarchy'] = hierarchy;
    }
    if (master !== 0) {
        data['master'] = master;
    }
    if (search_email != "") {
        data['search_email'] = search_email;
    }
    if (search_phone_number != "") {
        data['search_phone_number'] = search_phone_number;
    }
    if (search_country != "") {
        data['search_country'] = search_country;
    }
    if (search_city != "") {
        data['search_city'] = search_city;
    }
    return data;
}

function applyFilter(el, callback) {
    let self = el, data;
    data = filterParam();
    $('.preloader').css('display', 'block');
    callback(data);
    setTimeout(function () {
        hidePopup(self);
    }, 300);
}

var makeChooseStatus = getStatuses().then(function (data) {
    data = data.results;
    let html = "";
    for (let i = 0; i < data.length; i++) {
        html += '<option value="' + data[i].id + '" data-level="' + data[i].level + '">' + data[i].title + '</option>';
    }
    return html;
});

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