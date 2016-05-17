function currentUser(data) {

    arrClassName([{
        className: 'admin_name',
        index: 0,
        dataAtrr: 'fullname'
    }, {
        className: 'status',
        index: 0,
        dataAtrr: 'hierarchy_name'
    }], data);

    //document.getElementsByClassName('news')[0].innerHTML = data.events.length;
    document.getElementsByClassName('admin_name')[0].setAttribute('data-id', data.id);
    document.getElementsByClassName('admin_name')[0].setAttribute('data-hierarchy-level', data.hierarchy_level - 1);
    document.getElementsByClassName('admin_name')[0].setAttribute('data-staff-status', data.is_staff);
}

function createMenu(list) {
    var count, nav, html;
    count = list.length;
    nav = document.getElementsByClassName('navigation')[0].getElementsByTagName('ul')[0];
    html = '';
    for (var i = 0; i < count; i++) {
        html += '<li><a href="' + list[i].url + '">' + list[i].title + '</a></li>'
    }

    html += '<div class="menu-item-notifications"><a href="/notifications"><span>Уведомления <span id="count_notifications"></span></span> </a></div>'
    html += '<a href="/api/logout"  class="red-button-menu">Выйти</a>'
    nav.innerHTML = html;
    var link = window.location.href.split('/');
    var page = link[link.length - 1];
    if (isElementExists(nav.querySelector("li a[href$='" + page + "']"))) {
        nav.querySelector("li a[href$='" + page + "']").classList.add('active');
    }
    counterNotifications();

    document.getElementsByClassName('nav_item')[0].addEventListener('click', function(e) {
        e.preventDefault();
        var id = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
        setTimeout(function() {
            window.location.href = '/account/' + id
        }, 1000);
    })
}