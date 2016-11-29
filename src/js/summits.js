$(document).ready(function () {

    if (document.getElementById('summits')) {
        create_summit_buttons('summits');
    }

    $('body').on('click', '#summit_buttons li', function () {
        $(this).addClass('active');
        var summit_id = $(this).attr('data-id');
        createSummits({'summit': summit_id})
        window.summit = summit_id;
    });

    $('input[name="fullsearch"]').keyup(function () {
        delay(function () {
            var data = {};
            data['summit'] = summit_id;
            getUsersList(path, data);
        }, 1500);
    });

    $('input[name="searchDep"]').keyup(function () {
        delay(function () {
            var data = {};
            var path = config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/?';
            data['summit'] = summit_id;
            data['user__department__title'] = $('input[name="searchDep"]').val();
            getUsersList(path, data);
        }, 1500);
    });

    $('#searchUsers').keyup(function () {
        getUnregisteredUsers();
    });

    document.getElementById('dep_filter').addEventListener('change', function () {
        var params = {};
        getUsersList(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/', params)

    });

    getDepartmentsAll();

    $('#summit_type').on('change', function () {
        var val = this.value;
        var path = '/api/v1.0/summit_ankets/';
        var param;
        switch (val) {
            case '0':
                getUsersList(path);
                break;
            case '1':

                param = {
                    is_member: true
                };
                getUsersList(path, param);
                break;
            case '2':
                param = {
                    is_member: false
                };
                getUsersList(path, param);
                break;
        }
    });
    $('body').on('click', '#carousel li span', function () {
        $('#carousel li').removeClass('active');
        $(this).parent().addClass('active')
    });

    document.getElementById('sort_save').addEventListener('click', function () {
        updateSettings(getUsersList, path);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });

    if (document.querySelector('.table-wrap')) {

        document.querySelector("#add").addEventListener('click', function () {
            document.querySelector('.add-user-wrap').style.display = 'block';
        });


        document.querySelector("#popup h3 span").addEventListener('click', function () {
            document.querySelector('#popup').style.display = 'none';
            document.querySelector('.choose-user-wrap').style.display = 'block';
        });

        document.querySelector("#close").addEventListener('click', function () {
            document.querySelector('#popup').style.display = 'none';
            document.querySelector('.choose-user-wrap').style.display = 'block';
        });

        document.querySelector("#closeDelete").addEventListener('click', function () {
            document.querySelector('#popupDelete').style.display = 'none';
        });

        document.querySelector(".add-user-wrap .top-text span").addEventListener('click', function () {
            document.querySelector('.add-user-wrap').style.display = '';
        });

        document.querySelector(".add-user-wrap").addEventListener('click', function (el) {
            if (el.target !== this) {
                return;
            }
            document.querySelector('.add-user-wrap').style.display = '';
        });

        document.querySelector("#popupDelete").addEventListener('click', function (el) {
            if (el.target !== this) {
                return;
            }
            document.querySelector('#popupDelete').style.display = '';
        });

        document.querySelector("#popupDelete .top-text span").addEventListener('click', function (el) {
            document.querySelector('#popupDelete').style.display = '';
        });

        document.querySelector(".choose-user-wrap").addEventListener('click', function (el) {
            if (el.target !== this) {
                return;
            }
            document.querySelector('.choose-user-wrap').style.display = '';
            document.getElementById('searchUsers').value = '';
            document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
        });

        document.querySelector(".choose-user-wrap .top-text > span").addEventListener('click', function () {
            document.getElementById('searchUsers').value = '';
            document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
            document.querySelector('.choose-user-wrap').style.display = '';
        });

        document.getElementById('choose').addEventListener('click', function () {
            document.querySelector('.choose-user-wrap').style.display = 'block';
            document.querySelector('.add-user-wrap').style.display = '';
        });

        document.querySelector('.choose-user-wrap h3 span').addEventListener('click', function () {
            document.getElementById('searchUsers').value = '';
            document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
            document.querySelector('.choose-user-wrap').style.display = '';
            document.querySelector('.add-user-wrap').style.display = 'block';
        });

        document.getElementById('add_new').addEventListener('click', function () {
            document.querySelector('.pop-up-splash-add').style.display = 'block';
        });

        document.getElementById('changeSum').addEventListener('click', function () {
            document.getElementById('summit-value').removeAttribute('readonly');
            document.getElementById('summit-value').focus();
        });

        document.getElementById('changeSumDelete').addEventListener('click', function () {
            document.getElementById('summit-valueDelete').removeAttribute('readonly');
            document.getElementById('summit-valueDelete').focus();
        });

        document.getElementById('deleteAnket').addEventListener('click', function () {
            var summitAnket = this.getAttribute('data-anket');
            document.getElementById('yes').setAttribute('data-anket', summitAnket)
            document.getElementById('deletePopup').style.display = 'block';
            document.querySelector('#popupDelete').style.display = '';
        });

        document.getElementById('yes').addEventListener('click', function () {
            var summitAnket = this.getAttribute('data-anket');
            document.getElementById('deletePopup').style.display = '';
            unsubscribe(summitAnket);
        });

        $('#deletePopup').click(function (el) {
            if (el.target != this) {
                return;
            }
            $(this).hide();
        });

        $('#no').click(function () {
            $('#deletePopup').hide();
        });

        $('#deletePopup .top-text span').click(function () {
            $('#deletePopup').hide();
        });

        document.getElementById('completeDelete').addEventListener('click', function () {
            var id = this.getAttribute('data-id'),
                money = document.getElementById('summit-valueDelete').value,
                description = document.querySelector('#popupDelete textarea').value;
            registerUser(id, summit_id, money, description);
            document.querySelector('#popupDelete').style.display = 'none';
        });

        document.getElementById('complete').addEventListener('click', function () {
            var id = this.getAttribute('data-id'),
                money = document.getElementById('summit-value').value,
                description = document.querySelector('#popup textarea').value;
            registerUser(id, summit_id, money, description);
            document.querySelector('#popup').style.display = 'none';
            document.querySelector('.choose-user-wrap').style.display = 'block';
        });

        addSummitInfo();
    }
});

var summit_id;
var ordering = {};
var order;
var path = config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/?';

function unsubscribe(id) {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/' + id + '/', null, function () {
        var data = {};
        data['summit'] = summit_id;
        getUsersList(path, data);
        document.querySelector('#popupDelete').style.display = 'none';
    }, 'DELETE', true, {
        'Content-Type': 'application/json'
    });
}

function registerUser(id, summit_id, money, description) {
    var member_club = $("#member").prop("checked");
    var send_email = $("#send_email").prop("checked");
    var data = {
        "user_id": id,
        "summit_id": summit_id,
        "value": money,
        "description": description,
        "visited": member_club,
        "send_email": send_email
    };

    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/post_anket/', json, function (JSONobj) {
        if (JSONobj.status) {
            var data = {};
            data['summit'] = summit_id;
            showPopup(JSONobj.message);
            getUsersList(path, data);
            getUnregisteredUsers();
            $("#send_email").prop("checked", false);
        } else {
            showPopup(JSONobj.message);
            $("#send_email").prop("checked", false);
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function getUnregisteredUsers(parameters) {
    var param = parameters || {};
    var search = document.getElementById('searchUsers').value;
    if (search) {
        param['search'] = search;
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_search/?summit_id!=' + summit_id, param, function (data) {
        var html = '';
        data = data.results;
        for (var i = 0; i < data.length; i++) {
            html += '<div class="rows-wrap"><button data-master="' + data[i].master_short_fullname + '" data-name="' + data[i].fullname + '" data-id="' + data[i].id + '">Выбрать</button><div class="rows"><div class="col"><p><span><a href="/account/' + data[i].id + '">' + data[i].fullname + '</a></span></p></div><div class="col"><p><span>' + data[i].country + '</span>,<span> ' + data[i].city + '</span></p></div></div></div>';
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
                var id = this.getAttribute('data-id'),
                    name = this.getAttribute('data-name'),
                    master = this.getAttribute('data-master');
                document.getElementById('summit-value').value = "0";
                document.getElementById('summit-value').setAttribute('readonly', 'readonly');
                document.querySelector('#popup textarea').value = "";
                getDataForPopup(id, name, master);
                document.getElementById('popup').style.display = 'block';
                document.querySelector('.choose-user-wrap').style.display = 'none';
            })
        }
    });
}

function getDataForPopup(id, name, master) {
    document.getElementById('complete').setAttribute('data-id', id);
    document.getElementById('client-name').innerHTML = name;
    document.getElementById('responsible-name').innerHTML = master;
}

function create_summit_buttons(id) {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_types/', null, function (data) {
        var data = data.results;
        var html = '';
        for (var i = 0; i < data.length; i++) {
            html += '<div><img data-id="' + data[i].id + '" src="' + data[i].image + '" alt="" /></div>';
        }
        html += '</ul></div>';
        document.getElementById(id).innerHTML = html;
        var img = document.querySelectorAll('#summits img');
        for (var i = 0; i < img.length; i++) {
            img[i].addEventListener("click", function () {
                location.href = '/summit_info/' + this.getAttribute('data-id');
            });
        }
    });
}

function addSummitInfo() {
    var id = getLastId();
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit/?type=' + id, null, function (data) {
        var data = data.results,
            html = '';
        for (var i = 0; i < data.length; i++) {
            var summit_name = data[i].description ? data[i].description : data[i].start_date;
            if (i == 0) {
                html += '<li class="active"><span data-id=' + data[i].id + '>' + summit_name + '</span></li>';
            } else {
                html += '<li><span data-id=' + data[i].id + '>' + summit_name + '</span></li>';
            }

        }
        document.getElementById('date').innerHTML = html;
        document.getElementById('summit-title').innerHTML = '<a href="/summits">САММИТЫ | </a><span>' + data[0].title + '</span>';
        var width = 150,
            count = 1,
            carousel = document.getElementById('carousel'),
            list = carousel.querySelector('ul'),
            listElems = carousel.querySelectorAll('li'),
            position = 0;
        carousel.querySelector('.arrow-left').onclick = function () {
            position = Math.min(position + width * count, 0)
            list.style.marginLeft = position + 'px';
        };
        carousel.querySelector('.arrow-right').onclick = function () {
            position = Math.max(position - width * count, -width * (listElems.length - 3));
            list.style.marginLeft = position + 'px';
        };
        var butt = document.querySelectorAll('#carousel li span');
        for (var z = 0; z < butt.length; z++) {
            butt[z].addEventListener('click', function () {
                var data = {};
                data['summit'] = this.getAttribute('data-id');
                window.summit_id = data['summit'];
                getUsersList(path, data);
            })
        }
    });
}

function getCurrentSummitSetting(data) {
    var html = '';
    data.forEach(function (d) {
        var titles = d[1];
        html += '<h3>' + d[0] + '</h3>';
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
    });

    document.getElementById('sort-form').innerHTML = html;

    live('click', "#sort-form label", function (el) {
        if (!this.parentElement.hasAttribute('disable')) {
            this.classList.contains('check') ? this.classList.remove('check') : this.classList.add('check');
        }
    })

}

function reversOrder(order) {
    if (order.charAt(0) == '-') {
        order = order.substring(1)
    } else {
        order = '-' + order
    }
    return order
}

function getUsersList(path, param) {
    param = param || {};
    var search = document.getElementsByName('fullsearch')[0].value;
    var el = document.getElementById('dep_filter');
    var value = el.options[el.selectedIndex].value;
    if (parseInt(value)) {
        param['user__department__title'] = el.options[el.selectedIndex].text;
    }
    var ordering = param.ordering || 'user__last_name';
    var filter = document.getElementById('filter').value;
    if (search) {
        if (filter == 'search') {
            param[filter] = search;
        } else {
            param['user__' + filter] = search;
        }

    }
    param['summit'] = summit_id;
    document.getElementsByClassName('preloader')[0].style.display = 'block';
    ajaxRequest(path, param, function (data) {

        var results = data.results;

        var k;
        var value;

        var count = data.count;
        if (results.length == 0) {
            document.getElementById('users_list').innerHTML = '<p>По запросу не найдено учасников</p>';
            document.querySelector(".element-select").innerHTML = elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
            document.getElementsByClassName('preloader')[0].style.display = 'none';
            Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function (el) {
                el.innerHTML = '';
            });
            return;
        }

        var common_fields = data.common_table;
        var user_fields = data.user_table;

        getCurrentSummitSetting([['Пользователь', user_fields]]);

        var thead = '<thead><tr>';
        for (k in user_fields) {
            if (!user_fields.hasOwnProperty(k) || !user_fields[k].active) continue;
            if (ordering.indexOf('user__' + user_fields[k]['ordering_title']) != -1) {
                thead += '<th data-order="' + reversOrder(ordering) + '">' + user_fields[k]['title'] + '</th>'
            } else {
                thead += '<th data-order="user__' + user_fields[k]['ordering_title'] + '">' + user_fields[k]['title'] + '</th>'
            }
        }
        for (k in common_fields) {
            if (!common_fields.hasOwnProperty(k) || !common_fields[k].active) continue;
            if (ordering.indexOf(common_fields[k]['ordering_title']) != -1) {
                thead += '<th data-order="' + reversOrder(ordering) + '">' + common_fields[k]['title'] + '</th>'
            } else {
                thead += '<th data-order="' + common_fields[k]['ordering_title'] + '">' + common_fields[k]['title'] + '</th>'
            }
        }
        thead += '</tr></thead>';

        var tbody = '<tbody>';
        results.forEach(function (field, i) {
            tbody += '<tr>';

            for (k in user_fields) {
                if (!user_fields.hasOwnProperty(k) || !user_fields[k].active) continue;
                value = getCorrectValue(field['user'][k]);
                if (k === 'fullname') {
                    // results[i].is_member
                    tbody += '<td';
                    var classes = [];
                    if(results[i].is_member) {
                        classes = classes.concat('member_user')
                    }
                    if (results[i].emails.length > 0) {
                        classes = classes.concat('email_is_send')
                    }
                    if (classes.length > 0) {
                        tbody += ' class="' + classes.join(' ') + '"';
                    }
                    tbody +=   '>' + '<a href="' + results[i].user.link + '">' + value + '</a><span title="Удалить анкету" data-fullname="' + results[i].user.fullname + '" data-user-id="' + results[i].user.id + '" data-anketId="' + results[i].id + '"" data-value="' + results[i].value + '" data-comment="' + results[i].description + '" data-member="' + results[i].is_member + '" class="del"></span></td>'
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
                value = getCorrectValue(field[k]);
                if (k == 'code') {
                    tbody += '<td><a href="/api/v1.0/generate_code/' + results[i].user.fullname + ' (' + value + ').pdf?code=' + value + '">' + value + '</a></td>'
                } else {
                    tbody += '<td>' + value + '</td>'
                }
            }
            tbody += '</tr>';
        });
        tbody += '</tbody>';

        var table = '<table>' + thead + tbody + '</table>';

        var page = parseInt(param['page']) || 1,
            pages = Math.ceil(count / config.pagination_count),
            paginations = '',
            elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
        if (page > 1) {
            paginations += '<div class="prev"><span class="arrow"></span></div>';
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
                paginations += '<li class="no-pagin">&hellip;</li>'

                if (page < pages - 3) {
                    paginations += '<li>' + pages + '</li>'
                }


            }
            paginations += '</ul>'
        }

        if (page < pages) {
            paginations += '</ul><div class="next"><span class="arrow"></span></div>'
        }

        document.getElementById('users_list').innerHTML = table;
        // document.querySelector("#users_list tbody").innerHTML = html;
        document.querySelector(".element-select").innerHTML = elementSelect;
        document.getElementsByClassName('preloader')[0].style.display = 'none';
        Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function (el) {
            el.innerHTML = paginations;
        });

        $('#users_list .del').click(function (el) {
            if (el.target.nodeName == 'A') {
                return;
            }
            var id = $(this).data('user-id'),
                usr = $(this).data('fullname'),
                anketa = $(this).attr('data-anketId'),
                val = $(this).attr('data-value'),
                comment = $(this).attr('data-comment'),
                member = $(this).attr('data-member');

            $('#completeDelete').attr('data-id', id);
            $('#deleteAnket').attr('data-anket', anketa);
            $('#summit-valueDelete').val(val);
            $('#popupDelete textarea').val(comment);
            $('#popupDelete h3').html(usr);
            if( member == 'false') {
                $('#member').prop('checked', false);
            } else {
                $('#member').prop('checked', true);
            }

            document.querySelector('#popupDelete').style.display = 'block';
        });

        Array.prototype.forEach.call(document.querySelectorAll(" .pag li"), function (el) {
            el.addEventListener('click', function () {
                if (this.className == 'no-pagin') {
                    return false;
                }
                var data = {};
                data['summit'] = summit_id;
                data['page'] = el.innerHTML;
                data['ordering'] = order;
                data['user__department__title'] = $('input[name="searchDep"]').val();
                getUsersList(path, data);
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll(".pag-wrap p > span"), function (el) {
            el.addEventListener('click', function () {
                var data = {};
                data['summit'] = summit_id;
                data['page'] = el.innerHTML;
                data['ordering'] = order;
                data['user__department__title'] = $('input[name="searchDep"]').val();
                getUsersList(path, data);
            });
        });

        /* Navigation*/

        Array.prototype.forEach.call(document.querySelectorAll(".arrow"), function (el) {
            el.addEventListener('click', function () {
                var page;
                var data = {};
                if (this.parentElement.classList.contains('prev')) {
                    page = parseInt(document.querySelector(".pag li.active").innerHTML) > 1 ? parseInt(document.querySelector(".pag li.active").innerHTML) - 1 : 1;
                    data['page'] = page;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    data['user__department__title'] = $('input[name="searchDep"]').val();
                    getUsersList(path, data);
                } else {

                    page = parseInt(document.querySelector(".pag li.active").innerHTML) != pages ? parseInt(document.querySelector(".pag li.active").innerHTML) + 1 : pages;
                    data['page'] = page;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    data['user__department__title'] = $('input[name="searchDep"]').val();
                    getUsersList(path, data);
                }
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll(".double_arrow"), function (el) {
            el.addEventListener('click', function () {
                var data = {};
                if (this.parentElement.classList.contains('prev')) {
                    data['page'] = 1;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    getUsersList(path, data);
                } else {
                    data['page'] = pages;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    getUsersList(path, data);
                }
            });
        });
        $('#summit_type').select2();
        Array.prototype.forEach.call(document.querySelectorAll(".table-wrap th"), function (el) {
            el.addEventListener('click', function () {
                var data_order = this.getAttribute('data-order');
                var status = !!ordering[data_order];
                ordering = {};
                ordering[data_order] = status;
                // data_order = status ? 'user__' + data_order : '-' + 'user__' + data_order;
                window.order = data_order;
                var page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1;
                var data = {
                    'ordering': data_order,
                    'page': page,
                    'summit': summit_id
                };
                data['user__department__title'] = $('input[name="searchDep"]').val();
                getUsersList(path, data)
            });
        });
    });
}
    