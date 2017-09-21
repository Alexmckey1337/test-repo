'use strict';
import 'jquery.scrollbar';
import 'jquery.scrollbar/jquery.scrollbar.css';
import 'select2';
import 'select2/dist/css/select2.css';
import URLS from './modules/Urls/index';
import {deleteCookie} from './modules/Cookie/cookie';
import ajaxRequest from './modules/Ajax/ajaxRequest';
import {hidePopup} from './modules/Popup/popup';
import {counterNotifications, birhtdayNotifications,
        repentanceNotifications, makeBirthdayUsers, makeRepentanceUsers} from './modules/Notifications/notify';
import fixedTableHead from './modules/FixedHeadTable/index';
import {hideFilter} from './modules/Filter/index';

$(window).on('hashchange', function () {
    location.reload();
});

$('.close').on('click', function () {
    if ($(this).closest('.pop-up-splash')) {
        $(this).closest('.pop-up-splash').css('display', 'none');
    }
    if ($(this).closest('.popup')) {
        $(this).closest('.popup').css('display', 'none');
    }
});

$('#logout_button').on('click', function (e) {
    e.preventDefault();
    ajaxRequest(URLS.logout(), null, function (data) {
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
    let $body = $('body');
    if ($body.hasClass('no_scroll')) {
        $body.removeClass('no_scroll');
    }
    $(this).closest('.popap').css('display', 'none');
});

/*search animate width*/
$('.top input').click(function () {
    $('.top .search').animate({width: "80%"});
});

if (document.getElementById('filter')) {
    $('#filter').select2();
}

function sortSave() {
    $('sort_save').on('click', function () {
        $(".table-sorting").toggleClass('active');
    })
}

$("#pag li ").click(function (e) {
    e.preventDefault();
    $("#pag li").removeClass('active');
    $(this).addClass('active');
});

$('body').on('click', '#pag li', function (e) {
    e.preventDefault();
    $("#pag li").removeClass('active');
    $(this).addClass('active');
});

/*DND columns*/
$("#sort-on").click(function () {
    $(".table-sorting").toggleClass('active');
    let sortBG = document.createElement('div');
    $(sortBG).addClass('bg_sort').on('click', function () {
        $(".table-sorting").toggleClass('active');
        $(this).remove();
    });
    $("body").append(sortBG);
});

$("#sort-off").click(function () {
    $(".table-sorting").toggleClass('active');
    $(".bg_sort").remove();
});

$("#sort_save").on('click', function () {
    $(".table-sorting").toggleClass('active');
    $(".bg_sort").remove();
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
    console.log($(this).index());
    $('.tabs-nav li').removeClass('current');
    $(this).addClass('current');
    $('.tab-toggle').hide();
    $('.tab-toggle[data-id="' + $(this).index() + '"]').show();
});

$(".tabs-nav li a:first").click();

$(document).ready(function () {
    $('body').on('mouseover', '.toggle-sidebar .menu__item', function (el) {
        if ($(this).parent().is('#move-sidebar')) {
            return
        }
        let hint = '<div id="hint">' + $(this).attr('data-title') + '</hint>';
        $('body').append(hint);
        let position = ($(this).offset().top - $(window).scrollTop()) + ($(this).outerHeight() / 2) - $('#hint').outerHeight() / 2;
        $('#hint').css('top', position).fadeIn();
    });

    $('.editprofile input').keypress(function (el) {
        if (el.charCode == '32' && el.currentTarget.id != 'extra_phone_numbers' && el.currentTarget.id != 'address' && el.currentTarget.id != 'search_name') {
            return false
        }
    });

    $('body').on('mouseout', '.toggle-sidebar .menu__item', function (el) {
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

    $('#nav-sidebar').find('.menu__item').on('click', function (e) {
        e.preventDefault();
        $('#hint').fadeOut();
        let $sidebar = $("#sidebar");
        let $moveSidebar = $('#move-sidebar');
        if ($sidebar.hasClass('toggle-sidebar')) {
            setTimeout(function () {
                $sidebar.removeClass('toggle-sidebar');
                document.documentElement.style.setProperty('--lsb_width', '240px');
                $moveSidebar.removeClass('active');
                // deleteCookie('state');
            }, 100)
        }
        $(this).parent().siblings('li').removeClass('sb-menu_link__active').find('.sidebar-submenu:visible').slideUp(300);
        $(this).next('ul').slideToggle(400).parent().toggleClass('sb-menu_link__active');
    });

});

window.onload = function () {
    if (opened('state')) {
        $("#sidebar").addClass('toggle-sidebar');
        $('#move-sidebar').addClass('active');
        document.documentElement.style.setProperty('--lsb_width', '90px');
    } else {
        $("#sidebar").removeClass('toggle-sidebar');
        $('#move-sidebar').removeClass('active');
        document.documentElement.style.setProperty('--lsb_width', '240px');
    }
    $('body').show();
};

function opened(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? true : false;
}

$('.close-popup').on('click', function (e) {
    e.preventDefault();
    hidePopup(this);
});

function setSidebarPosition() {
    let $sidebar = $("#sidebar");
    let $moveSidebar = $('#move-sidebar');
    if (!$sidebar.hasClass('toggle-sidebar')) {
        setTimeout(function () {
            $sidebar.addClass('toggle-sidebar');
            document.documentElement.style.setProperty('--lsb_width', '90px');
            $moveSidebar.addClass('active');
            document.cookie = 'state=active;path=/';
        }, 100)
    } else {
        setTimeout(function () {
            $sidebar.removeClass('toggle-sidebar');
            document.documentElement.style.setProperty('--lsb_width', '240px');
            $moveSidebar.removeClass('active');
            deleteCookie('state');
        }, 100)
    }
}

$(document).ready(function () {
    // //Hide element after click in another area display
    document.body.addEventListener('click', function (el) {
        let photoHover = document.querySelector(".photo-hover"),
            messageHover = document.querySelector('.massage-hover');
        if (el.target == document.querySelector(".userImgWrap") || el.target == document.querySelector(".userImgWrap img")) {
            photoHover.style.display == 'block' ? photoHover.style.display = 'none' : photoHover.style.display = 'block';
            messageHover.style.display = 'none';
        } else if (el.target == document.querySelector('.sms') || el.target == document.querySelector('.sms span:last-child')) {
            messageHover.style.display == 'block' ? messageHover.style.display = 'none' : messageHover.style.display = 'block';
            photoHover.style.display = 'none';
        } else if (el.target == document.querySelector('.top input') || el.target == document.querySelector('#select2-filter-container')) {
            return
        } else {
            messageHover.style.display = 'none';
            photoHover.style.display = 'none';
            hideFilter();
        }
    });

    let $createUser = $('#createUser');
    $createUser.on('submit', function (e) {
        e.preventDefault();
    });
    $().dblclick(() => false);
    $("#turn_aside").on('click', function (e) {
        e.preventDefault();
        setSidebarPosition()
    });

    $('#check-all').on('change', function () {
        let $input = $("#sort-form input");
        if ($(this).is(":checked")) {
            $input.each(function () {
                $(this).prop("checked", true);
            });
        } else {
            $input.each(function () {
                $(this).prop("checked", false);
            });
        }
    });

    $('.pop-up_special__table').find('.close_pop').on('click', function () {
        $('.pop-up_special__table').css('display', 'none');
    });

    $('.pop-up__table').on('click', function () {
        $(this).css('display', 'none');
    });

    $('.pop-up__table').find('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });

    let count = true,
        config = {};
    if ($('#sms_notification').length > 0) {
        Promise.all([counterNotifications(), birhtdayNotifications(config, count), repentanceNotifications(config, count)]).then(values => {
            let data = {},
                box = $('.massage-hover').find('.hover-wrapper');
            for (let i = 0; i < values.length; i++) {
                Object.assign(data, values[i]);
            }
            let count = Object.values(data).reduce((prev, current) => prev + current);
            $('.sms').attr('data-count', count);
            if (count > 0) {
                $("#without_notifications").remove();
                if (data.birthdays_count > 0) {
                    let birthdayNote = `<div class="notification_row notification_row__birth" data-type="birthdays"><p>Дни рождения: <span>${data.birthdays_count}</span></p></div>`;
                    box.append(birthdayNote);
                }
                if (data.repentance_count > 0) {
                    let repentanceNote = `<div class="notification_row notification_row__rep" data-type="repentance"><p>Дата покаяния: <span>${data.repentance_count}</span></p></div>`;
                    box.append(repentanceNote);
                }
                box.on('click', '.notification_row', function () {
                    let type = $(this).attr('data-type');
                    (type == 'birthdays') && makeBirthdayUsers();
                    (type == 'repentance') && makeRepentanceUsers();
                })
            }
        });
    }

    $(window).on('resize', function () {
        if ($("#header-fixed").length) {
            $("#header-fixed").empty();
            fixedTableHead();
        } else {
            return false;
        }
    });

});
