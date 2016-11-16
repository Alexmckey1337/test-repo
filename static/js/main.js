//Создать метод вызова init()

var config = {
    // 'DOCUMENT_ROOT': 'http://vocrm.org/',
    'DOCUMENT_ROOT': '/',
    'pagination_count': 30, //Количество записей при пагинации
    'pagination_patrnership_count': 30, //Количество записей при пагинации for patrnership

    // 'pagination_mini_count': 10,
    'column_table': null
};

function setCookie(name, value, options) {
    options = options || {};

    var expires = options.expires;

    if (typeof expires == "number" && expires) {
        var d = new Date();
        d.setTime(d.getTime() + expires * 1000);
        expires = options.expires = d;
    }
    if (expires && expires.toUTCString) {
        options.expires = expires.toUTCString();
    }

    value = encodeURIComponent(value);

    var updatedCookie = name + "=" + value;

    for (var propName in options) {
        updatedCookie += "; " + propName;
        var propValue = options[propName];
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
    // $('.filter').show();
});

function hideFilter() {
    //$('.top input').blur(function() {
    if (!$('.top input').val().length) {
        $('.top .search').animate({width: "50%"});
        // $('.filter').hide();
    }
    //});
}

if (document.getElementById('filter')) {
    $('#filter').select2();
}

if (document.getElementById('sort_save')) {
    document.getElementById('sort_save').addEventListener('click', function () {
        // updateSettings(getCurrentSetting);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    })
}

function getNotifications() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/notifications/today/', null, function (data) {
        var count = data.count;
        data = data.results;
        var html = "";
        if (count > 0) {
            document.querySelector('.sms span:first-child').innerHTML = count;
            document.querySelector('.sms span:first-child').style.display = 'block';
            for (var i = 0; i < data.length; i++) {
                if (data[i].common) {
                    html += '<li><a href="/account/' + data[i].uid + '">' + data[i].fullname + '</a></li>';
                }
            }
            document.querySelector('.massage-hover .bottom-box ul').innerHTML = html;
        } else {
            document.querySelector('.sms span:first-child').style.display = 'none';
            document.querySelector('.massage-hover .bottom-box').innerHTML = '<p>На сегодня нет уведомлений</p>'
        }
    })
}

/*function showWindow () {
 var wind = document.querySelector('.massage-hover');
 document.querySelector(".photo-hover").style.display = 'none';
 wind.classList.toggle('active-window');

 }*/

/* Написать модуль   пагинации и перенести обработчики туда */

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
        var hint = '<div id="hint">' + $(this).attr('data-title') + '</hint>';
        $('body').append(hint);
        var a = ($(this).offset().top - $(window).scrollTop()) + ($(this).outerHeight() / 2) - $('#hint').outerHeight() / 2;
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
    /*$('.toggle-sidebar a').hover(
     function() {
     console.log($(this).attr('title'))
     },
     function() {
     console.log($(this).html())
     });*/
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
        /*$("#sidebar").toggleClass("toggle-sidebar");*/
        if (!$("#sidebar").hasClass('toggle-sidebar')) {
            $("#sidebar").addClass('toggle-sidebar');
            document.cookie = 'state=active;path=/';
        } else {
            $("#sidebar").removeClass('toggle-sidebar')
            deleteCookie('state');
        }
    });

    var loc = window.location.pathname;
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


//Перенести в файл
    if (document.getElementById('edit_profile')) {
        document.getElementById('edit_profile').addEventListener('click', function () {
            window.location.href = '/account/' + config.user_id + '/'
        })
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

if (document.querySelector('.sms')) {
    getNotifications();
}

function opened(name) {
    var matches = document.cookie.match(new RegExp(
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
        var user_id = data.id;
        config.user_id = data.id;
        config.user_partnerships_info = data.partnerships_info;
        config.column_table = data.column_table;
        var hierarchy_chain = data['hierarchy_chain'];


        if (typeof init === "function") {
            //Не потрібно в DOMReady
            //init(user_id)
        }


        if (document.getElementById('database_users')) {
            createUser();
            // getCurrentSetting();
        }

        if (document.getElementById('partnersips_list')) {
            getPartnersList();
            // getCurrentSetting();
        }

        if (document.getElementById('users_list')) {
            var dat = {};
            delay(function () {
                dat['summit'] = document.querySelectorAll('#carousel li span')[0].getAttribute('data-id');
                window.summit_id = dat['summit'];
                getUsersList(path, dat);
                getCurrentSetting();
            }, 250);
        }


        if (document.getElementById('event_wrap')) {
            getCurrentSetting();
            init(user_id);
            //createSubordinateList(user_id);
        }


        if (document.querySelector(".userimg")) {
            var img = "<img src='" + data.image + "' alt='userphoto' />";
            if (data.image == null) {
                img = "<img src='" + '/static/img/no-usr.jpg' + "' alt='userphoto' />";
            }
            document.querySelector(".userimg").innerHTML = img;
        }

        if (document.getElementById("add_new")) {
            document.getElementById("add_new").setAttribute('data-id', data.id);
        }

        /*if(document.getElementById('edit-photo')){
         document.getElementById('edit-photo').setAttribute('data-source', data.image_source);
         }*/

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

    var titles = config['column_table'];
    var html = '';
    for (var p in titles) {
        if (!titles.hasOwnProperty(p)) continue;
        var ischeck = titles[p]['active'] ? 'check' : '';
        var isdraggable = titles[p]['editable'] ? 'draggable' : 'disable';
        html += '<li ' + isdraggable + ' >' +
            '<input id="' + titles[p]['ordering_title'] + '" type="checkbox">' +
            '<label for="' + titles[p]['ordering_title'] + '"  class="' + ischeck + '" id= "' + titles[p]['id'] + '">' + titles[p]['title'] + '</label>';
        if (isdraggable == 'disable') {
            html += '<div class="disable-opacity"></div>'
        }
        html += '</li>'
    }


    document.getElementById('sort-form').innerHTML = html;

    /*var cols = document.querySelectorAll('[draggable]');
     Array.prototype.forEach.call(cols, function(col) {
     col.addEventListener('drop', handleDrop, false);
     col.addEventListener('dragstart', handleDragStart, false);
     col.addEventListener('dragenter', handleDragEnter, false);
     col.addEventListener('dragover', handleDragOver, false);
     col.addEventListener('dragleave', handleDragLeave, false);
     });*/


    live('click', "#sort-form label", function (el) {
        if (!this.parentElement.hasAttribute('disable')) {
            this.classList.contains('check') ? this.classList.remove('check') : this.classList.add('check');
        }
    })

}


function updateSettings(callback, param) {


    var data = [];
    var iteration = 1;
    Array.prototype.forEach.call(document.querySelectorAll("#sort-form label"), function (el) {
        var item = {};
        item['id'] = parseInt(el.getAttribute('id'));
        item['number'] = iteration++;
        item['active'] = !!el.classList.contains('check');
        data.push(item);
    });

    var json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/update_columns/', json, function (JSONobj) {
        $(".bgsort").remove();
        config['column_table'] = JSONobj['column_table'];
        if (callback) {
            if (param !== undefined) {
                callback(param);
            } else {
                callback();
            }
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}
