var config = {
    // 'DOCUMENT_ROOT': 'http://vocrm.org/',
    'DOCUMENT_ROOT': '/',
    'pagination_count': 30, //Количество записей при пагинации
    'pagination_patrnership_count': 30, //Количество записей при пагинации for patrnership
    'column_table': null
};


function makeQuickEditCart() {
    e.preventDefault();
    let id, link;
    id = $(this).attr('data-id');
    link = $(this).attr('data-link');
    let url = "/api/v1.0/users/" + id + '/';
    ajaxRequest(url, null, function (data) {
        let quickEditCartTmpl, rendered, obj = Object.create(null);
        obj.fields =  data.fields;
        console.log(data);
        quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
        rendered = _.template(quickEditCartTmpl)(obj);
        console.log(rendered);
        $('#quickEditCartPopup').find('.popup_body').html(rendered);
        $('#quickEditCartPopup').css('display', 'block');
    }, 'GET', true, {
        'Content-Type': 'application/json'
    });
}
function goToUser(e) {
    e.preventDefault();
    let link;
    link = $(this).attr('data-link');
    window.location.href = link;
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

function deleteCookie(name) {
    setCookie(name, "", {
        expires: -1
    })
}

$('#logout_button').on('click', function (e) {
    e.preventDefault();
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/logout/', null, function (data) {
        deleteCookie('key');
        window.location.href = '/entry';
    }, 'POST', true, {
        'Content-Type': 'application/json'
    })
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
    $(".table-sorting").animate({right: '0px'}, 10, 'linear');
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
        if (el.charCode == '32' && el.currentTarget.id != 'additional_phone' && el.currentTarget.id != 'address') {
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

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/users/current/', null, function (data) {
        let user_id = data.id;
        config.user_id = data.id;
        config.user_partnerships_info = data.partnerships_info;
        config.column_table = data.column_table;
        let hierarchy_chain = data['hierarchy_chain'];

        if (document.getElementById('database_users')) {
            createUser();
        }

        if (document.getElementById('partnersips_list')) {
            getPartnersList();
        }

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

        if (config.user_partnerships_info && config.user_partnerships_info.is_responsible && document.querySelector('.manager_view')) {
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

    let titles = config['column_table'];
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

function updateSettings(callback, param) {
    let data = [];
    let iteration = 1;
    $("#sort-form input").each(function (el) {
        let item = {};
        item['id'] = $(this).val();
        item['number'] = iteration++;
        item['active'] = $(this).prop('checked');
        data.push(item);
    });
    let json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/update_columns/', json, function (JSONobj) {
        $(".bgsort").remove();
        config['column_table'] = JSONobj['column_table'];

        if (callback) {
            if (param !== undefined) {
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

function applyFilter(el) {
    let self = el, data;
    data = filterParam();
    createUser(data);
    setTimeout(function () {
        hidePopup(self);
    }, 300);
}