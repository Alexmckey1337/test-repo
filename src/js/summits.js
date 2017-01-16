$(document).ready(function () {
    if (document.getElementById('summits')) {
        create_summit_buttons('summits');
    }

    $('body').on('click', '#summit_buttons li', function () {
        $(this).addClass('active');
        let summit_id = $(this).attr('data-id');
        createSummits({'summit': summit_id});
        window.summit = summit_id;
    });

    $('input[name="fullsearch"]').keyup(function () {
        let val = $(this).val();
        delay(function () {
            let data = {};
            data['summit'] = summit_id;
            data['search'] = val;
            getUsersList(path, data);
        }, 1500);
    });

    $('input[name="searchDep"]').on('keyup', function () {
        delay(function () {
            let data = {};
            let path = config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/?';
            data['summit'] = summit_id;
            data['user__department__title'] = $('input[name="searchDep"]').val();
            getUsersList(path, data);
        }, 1500);
    });

    $('#searchUsers').on('keyup', getUnregisteredUsers);

    $('#dep_filter').on('change', function () {
        let params = {};
        getUsersList(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/', params)

    });

    $('#summit_type').on('change', function () {
        let val = this.value;
        let path = '/api/v1.0/summit_ankets/';
        let param;
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

    $('#sort_save').on('click', function () {
        updateSettings(getUsersList, path);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });

    if ($('.table-wrap')) {

        $("#add").on('click', function () {
            $('#addUser').css('display', 'block');
        });


        $("#popup h3 span").on('click', function () {
            $('#popup').css('display', 'none');
            $('.choose-user-wrap').css('display', 'block');
        });

        $("#close").on('click', function () {
            $('#popup').on('display', 'none');
            $('.choose-user-wrap').css('display', 'block');
        });

        $("#closeDelete").on('click', function () {
            $('#popupDelete').css('display', 'none');
        });

        $(".add-user-wrap .top-text span").on('click', function () {
            $('.add-user-wrap').css('display', '');
        });

        $(".add-user-wrap").on('click', function (el) {
            if (el.target !== this) {
                return;
            }
            $('.add-user-wrap').css('display', '');
        });

        $("#popupDelete").on('click', function (el) {
            if (el.target !== this) {
                return;
            }
            $('#popupDelete').css('display', '');
        });

        $("#popupDelete .top-text span").on('click', function (el) {
            $('#popupDelete').css('display', '');
        });

        $(".choose-user-wrap").on('click', function (el) {
            if (el.target !== this) {
                return;
            }
            $('.choose-user-wrap').css('display', '');
            $('searchUsers').val('');
            $('.choose-user-wrap .splash-screen').removeClass('active');
        });

        $(".choose-user-wrap .top-text > span").on('click', function () {
            $('searchUsers').val('');
            $('.choose-user-wrap .splash-screen').removeClass('active');
            $('.choose-user-wrap').css('display', '');
        });

        $('choose').on('click', function () {
            $('.choose-user-wrap').css('display', 'block');
            $('.add-user-wrap').css('display', '');
        });

        $('.choose-user-wrap h3 span').on('click', function () {
            $('searchUsers').val('');
            $('.choose-user-wrap .splash-screen').removeClass('active');
            $('.choose-user-wrap').css('display', '');
            $('.add-user-wrap').css('display', 'block');
        });

        $('#add_new').on('click', function () {
            $('.pop-up-splash-add').css('display', 'block');
        });
        $('#choose').on('click', function () {
            console.log(this);
            $('.choose-user-wrap').css('display', 'block');
            $('.add-user-wrap').css('display', 'none');
            document.querySelector('#searchUsers').focus();
        });
        $('changeSum').on('click', function () {
            $('#summit-value').removeAttr('readonly');
            $('#summit-value').focus();
        });

        $('changeSumDelete').on('click', function () {
            $('#summit-valueDelete').removeAttr('readonly');
            $('#summit-valueDelete').focus();
        });

        $('#deleteAnket').on('click', function () {
            let summitAnket = $(this).attr('data-anket');
            $('yes').attr('data-anket', summitAnket);
            $('#deletePopup').css('display', 'block');
            $('#popupDelete').css('display', '');
        });

        $('yes').on('click', function () {
            let summitAnket = $(this).attr('data-anket');
            $('#deletePopup').css('display', '');
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

        $('#completeDelete').on('click', function () {
            let id = this.attr('data-id'),
                money = $('#summit-valueDelete').val(),
                description = $('#popupDelete textarea').val();
            registerUser(id, summit_id, money, description);
            $('#popupDelete').css('display', 'none');
        });

        $('complete').on('click', function () {
            let id = this.attr('data-id'),
                money = $('#summit-value').val(),
                description = $('#popup textarea').val();
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
        let data = {};
        data['summit'] = summit_id;
        getUsersList(path, data);
        document.querySelector('#popupDelete').style.display = 'none';
    }, 'DELETE', true, {
        'Content-Type': 'application/json'
    });
}

function registerUser(id, summit_id, money, description) {
    let member_club = $("#member").prop("checked");
    let send_email = $("#send_email").prop("checked");
    let data = {
        "user_id": id,
        "summit_id": summit_id,
        "value": money,
        "description": description,
        "visited": member_club,
        "send_email": send_email
    };

    let json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/post_anket/', json, function (JSONobj) {
        if (JSONobj.status) {
            let data = {};
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

function getUnregisteredUsers() {
    let param = {};
    let search = $('#searchUsers').val();

    if (search) {
        param['search'] = search;
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_search/?summit_id!=' + summit_id, param, function (data) {
        let html = '';
        data = data.results;
        for (let i = 0; i < data.length; i++) {
            html += '<div class="rows-wrap"><button data-master="' + data[i].master_short_fullname + '" data-name="' + data[i].fullname + '" data-id="' + data[i].id + '">Выбрать</button><div class="rows"><div class="col"><p><span><a href="/account/' + data[i].id + '">' + data[i].fullname + '</a></span></p></div><div class="col"><p><span>' + data[i].country + '</span>,<span> ' + data[i].city + '</span></p></div></div></div>';
        }
        if (data.length > 0) {
            $('#searchedUsers').html(html);
        } else {
            $('#searchedUsers').html('<div class="rows-wrap"><div class="rows"><p>По запросу не найдено учасников</p></div></div>');
        }
        $('.choose-user-wrap .splash-screen').addClass('active');
        let but = $('.rows-wrap button');
        but.on('clock', function () {
            let id = this.attr('data-id'),
                name = this.attr('data-name'),
                master = this.attr('data-master');
            $('#summit-value').val("0");
            $('#summit-value').attr('readonly', true);
            $('#popup textarea').val("");
            getDataForPopup(id, name, master);
            $('popup').css('display', 'block');
            $('.choose-user-wrap').css('display', 'block');
        });
    });
}

function getDataForPopup(id, name, master) {
    $('#complete').attr('data-id', id);
    $('#client-name').html(name);
    $('#responsible-name').html(master);
}

function create_summit_buttons(id) {
    let img = $('#summits img');
    img.on('click', function () {
        location.href = '/summit_info/' + $(this).attr('data-id');
    })
}

function addSummitInfo() {
    let width = 150,
        count = 1,
        carousel = $('#carousel'),
        list = carousel.find('ul'),
        listElems = carousel.find('li'),
        position = 0;
    carousel.find('.arrow-left').on('click', function () {
        position = Math.min(position + width * count, 0);
        $(list).css({
            marginLeft: position + 'px'
        });
    });
    carousel.find('.arrow-right').on('click', function () {
        position = Math.max(position - width * count, -width * (listElems.length - 3));
        $(list).css({
            marginLeft: position + 'px'
        });
    });
    let butt = $('#carousel li span');
    for (let z = 0; z < butt.length; z++) {
        butt[z].addEventListener('click', function () {
            let data = {};
            data['summit'] = this.getAttribute('data-id');
            window.summit_id = data['summit'];
            getUsersList(path, data);
        })
    }
}

function getCurrentSummitSetting(data) {
    let html = '';
    data.forEach(function (obj) {
        let titles = obj[1];
        html += '<h3>' + obj[0] + '</h3>';
        for (let prop in titles) {
            if (!titles.hasOwnProperty(prop)) continue;
            let ischeck = titles[prop]['active'] ? 'check' : '';
            let isdraggable = titles[prop]['editable'] ? 'draggable' : 'disable';
            html += '<li ' + isdraggable + ' >' +
                '<input id="' + titles[prop]['ordering_title'] + '" type="checkbox">' +
                '<label for="' + titles[prop]['ordering_title'] + '"  class="' + ischeck + '" id= "' + titles[prop]['id'] + '">' + titles[prop]['title'] + '</label>';
            if (isdraggable == 'disable') {
                html += '<div class="disable-opacity"></div>'
            }
            html += '</li>'
        }
    });

    $('#sort-form').html(html);
    $('#sort-form input').on('click', function (el) {
        if (!$(this).prop('disable')) {
            $(this).hasClass('check') ? $(this).removeClass('check') : $(this).addClass('check');
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
    let search = document.getElementsByName('fullsearch')[0].value;
    let el = document.getElementById('dep_filter');
    let value = el.options[el.selectedIndex].value;
    if (parseInt(value)) {
        param['user__department__title'] = el.options[el.selectedIndex].text;
    }
    let ordering = param.ordering || 'user__last_name';
    param['summit'] = summit_id;
    document.getElementsByClassName('preloader')[0].style.display = 'block';
    ajaxRequest(path, param, function (data) {

        let results = data.results;

        let k;
        let value;

        let count = data.count;

        if (results.length == 0) {
            $('#users_list').html('<p>По запросу не найдено учасников</p>');
            $(".element-select").html('<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>');
            $('.preloader')[0].css('display', 'none');
            $(".pag-wrap").each(function (i, el) {
                el.html('');
            });
            return;
        }

        let common_fields = data.common_table;
        let user_fields = data.user_table;

        getCurrentSummitSetting([['Пользователь', user_fields]]);

        let thead = '<thead><tr>';
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

        let tbody = '<tbody>';
        results.forEach(function (field, i) {
            tbody += '<tr>';

            for (k in user_fields) {
                if (!user_fields.hasOwnProperty(k) || !user_fields[k].active) continue;
                value = getCorrectValue(field['user'][k]);
                if (k === 'fullname') {
                    // results[i].is_member
                    tbody += '<td';
                    let classes = [];
                    if (results[i].is_member) {
                        classes = classes.concat('member_user')
                    }
                    if (results[i].emails.length > 0) {
                        classes = classes.concat('email_is_send')
                    }
                    if (classes.length > 0) {
                        tbody += ' class="' + classes.join(' ') + '"';
                    }
                    tbody += '>' + '<a href="' + results[i].user.link + '">' + value + '</a><span title="Удалить анкету" data-fullname="' + results[i].user.fullname + '" data-user-id="' + results[i].user.id + '" data-anketId="' + results[i].id + '"" data-value="' + results[i].value + '" data-comment="' + results[i].description + '" data-member="' + results[i].is_member + '" class="del"></span></td>'
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

        let table = '<table>' + thead + tbody + '</table>';

        let page = parseInt(param['page']) || 1,
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

        $('#users_list').html(table);
        $(".element-select").html(elementSelect);
        $('.preloader').css('display', 'none');
        $(".pag-wrap").each(function (i, el) {
            $(el).html(paginations);
        });

        $('#users_list .del').on('click', function (el) {
            console.log(this);
            let id = $(this).attr('data-user-id'),
                usr = $(this).attr('fullname'),
                anketa = $(this).attr('data-anketId'),
                val = $(this).attr('data-value'),
                comment = $(this).attr('data-comment'),
                member = $(this).attr('data-member');

            $('#completeDelete').attr('data-id', id);
            $('#deleteAnket').attr('data-anket', anketa);
            $('#summit-valueDelete').val(val);
            $('#popupDelete textarea').val(comment);
            $('#popupDelete h3').html(usr);
            if (member == 'false') {
                $('#member').prop('checked', false);
            } else {
                $('#member').prop('checked', true);
            }
            $('#popupDelete').css('display', 'block');
        });

        $('.pag li').each(function (i, el) {
            $(el).on('click', function () {
                if (this.className == 'no-pagin') {
                    return false;
                }
                let data = {};
                data['summit'] = summit_id;
                data['page'] = el.innerHTML;
                data['ordering'] = order;
                data['user__department__title'] = $('input[name="searchDep"]').val();
                getUsersList(path, data);
            });
        });

        $('.pag-wrap p > span').each(function (i, el) {
            $(el).on('click', function () {
                let data = {};
                data['summit'] = summit_id;
                data['page'] = el.innerHTML;
                data['ordering'] = order;
                data['user__department__title'] = $('input[name="searchDep"]').val();
                getUsersList(path, data);
            });
        });

        /* Navigation*/

        $(".arrow").each(function (i, el) {
            $(el).on('click', function () {
                let page;
                let data = {};
                if ($(this).hasClass('prev')) {
                    page = parseInt($(".pag li.active").html()) > 1 ? parseInt($(".pag li.active").html()) - 1 : 1;
                    data['page'] = page;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    data['user__department__title'] = $('input[name="searchDep"]').val();
                    getUsersList(path, data);
                } else {
                    page = parseInt($(".pag li.active").html()) != pages ? parseInt($(".pag li.active").html()) + 1 : pages;
                    data['page'] = page;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    data['user__department__title'] = $('input[name="searchDep"]').val();
                    getUsersList(path, data);
                }
            });
        });

        $(".double_arrow").each(function (i, el) {
            $(el).on('click', function () {
                let data = {};
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
        $(".table-wrap th").each(function (el) {
            $(el).on('click', function () {
                let data_order = this.getAttribute('data-order');
                let status = !!ordering[data_order];
                ordering = {};
                ordering[data_order] = status;
                window.order = data_order;
                let page = $(".pag li.active") ? parseInt($(".pag li.active").html()) : 1;
                let data = {
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