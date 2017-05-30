const CONFIG = {
    // 'DOCUMENT_ROOT': 'http://vocrm.org/',
    'DOCUMENT_ROOT': '/',
    'pagination_count': 30, //Количество записей при пагинации
    'pagination_patrnership_count': 30, //Количество записей при пагинации for patrnership
    'column_table': null
};

const VOCRM = {};

counterNotifications();

$(window).on('hashchange', function () {
    location.reload();
});

// Sorting

// let orderTable = (function () {
//     let savePath = sessionStorage.getItem('path');
//     let path = window.location.pathname;
//     if(savePath != path) {
//         sessionStorage.setItem('path', path);
//         sessionStorage.setItem('revers', '');
//         sessionStorage.setItem('order', '');
//     }
//     function addListener(callback) {
//         $(".table-wrap th").on('click', function () {
//             let dataOrder;
//             let data_order = this.getAttribute('data-order');
//             if(data_order == "no_ordering") {
//                 return
//             }
//             let page = $('.pagination__input').val();
//             let revers = (sessionStorage.getItem('revers')) ? sessionStorage.getItem('revers') : "+";
//             let order = (sessionStorage.getItem('order')) ? sessionStorage.getItem('order') : '';
//             if (order != '') {
//                 dataOrder = (order == data_order && revers == "+") ? '-' + data_order : data_order;
//             } else {
//                 dataOrder = '-' + data_order;
//             }
//             let data = {
//                 'ordering': dataOrder,
//                 'page': page
//             };
//             if (order == data_order) {
//                 revers = (revers == '+') ? '-' : '+';
//             } else {
//                 revers = "+"
//             }
//             sessionStorage.setItem('revers', revers);
//             sessionStorage.setItem('order', data_order);
//             $('.preloader').css('display', 'block');
//             callback(data);
//         });
//     }
//
//     return {
//         sort: addListener
//     }
// })();

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
    let $body = $('body');
    if($body.hasClass('no_scroll')) {
        $body.removeClass('no_scroll');
    }
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
    //console.log(  $(this).index()   )
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

    // $('#container').on('click', function () {
    //     let $sidebar = $("#sidebar");
    //     let $moveSidebar = $('#move-sidebar');
    //     setTimeout(function () {
    //         $sidebar.addClass('toggle-sidebar');
    //         document.documentElement.style.setProperty('--lsb_width', '90px');
    //         $moveSidebar.addClass('active');
    //         document.cookie = 'state=active;path=/';
    //     }, 100);
    //     $sidebar.find('li').removeClass('sb-menu_link__active').find('.sidebar-submenu:visible').slideUp(300);
    // })

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

function deleteCookie(name) {
    document.cookie = name + '=active;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
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

function accordionInfo() {
    $('.info-title').on('click', function () {
        $(this).next('.info').slideToggle().siblings('.info:visible').slideUp();
        $(this).toggleClass('info-title_active').siblings('.info-title').removeClass('info-title_active');
    });
}

(function ($) {
    let $createUser = $('#createUser');
    $createUser.on('submit', function (e) {
        e.preventDefault();
    });
    $().dblclick(() => false);
    $("#turn_aside").on('click', function (e) {
        e.preventDefault();
        setSidebarPosition()
    });

})(jQuery);