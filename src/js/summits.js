$(document).ready(function () {
    if (document.getElementById('summits')) {
        create_summit_buttons('summits');
    }

    $('#summit_buttons li').on('click', function () {
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
            let path = CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/?';
            data['summit'] = summit_id;
            data['user__department__title'] = $('input[name="searchDep"]').val();
            getUsersList(path, data);
        }, 1500);
    });

    $('#searchUsers').on('keyup', getUnregisteredUsers);

    $('#dep_filter').on('change', function () {
        let params = {};
        getUsersList(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/', params)

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
        console.log(path);
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
            $('#popup').css('display', 'none');
            $('.choose-user-wrap').css('display', 'block');
        });

        $("#closeDelete").on('click', function () {
            $('#popupDelete').css('display', 'none');
        });
        $("#close-payment").on('click', function () {
            $('#popup-create_payment').css('display', 'none');
        });
        $("#close-payments").on('click', function () {
            $('#popup-payments').css('display', 'none');
            $('#popup-payments table').html('');
        });
        $("#popup-create_payment .top-text span").on('click', function (el) {
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#popup-create_payment').css('display', '');
        });
        $("#popup-payments .top-text span").on('click', function (el) {
            $('#popup-payments').css('display', '');
            $('#popup-payments table').html('');
        });
        $('#payment-form').on("submit", function (event) {
            event.preventDefault();
            let data = $('#payment-form').serializeArray();
            console.log(data);
            let new_data = {};
            data.forEach(function (field) {
                new_data[field.name] = field.value
            });
            let id = new_data.id,
                sum = new_data.sum,
                description = new_data.description,
                rate = new_data.rate,
                currency = new_data.currency;
            console.log(id, sum, description, rate, currency);
            create_payment(id, sum, description, rate, currency);
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#popup-create_payment').css('display', 'none');
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

        $('.choose-user-wrap h3 span').on('click', function () {
            $('searchUsers').val('');
            $('.choose-user-wrap .splash-screen').removeClass('active');
            $('.choose-user-wrap').css('display', '');
            $('.add-user-wrap').css('display', 'block');
            $('#choose').on('click', function () {
                $('.choose-user-wrap').css('display', 'block');
                $('.add-user-wrap').css('display', '');
            });
        });

        $('#add_new').on('click', function () {
            $('#addNewUserPopup').css('display', 'block');
            $(this).closest('#addUser').css('display', 'none');
        });

        $('#choose').on('click', function () {
            $('.choose-user-wrap').css('display', 'block');
            $('.add-user-wrap').css('display', 'none');
            document.querySelector('#searchUsers').focus();
        });
        $('#changeSum').on('click', function () {
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

        $('#complete').on('click', function () {
            let id = $(this).attr('data-id'),
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
var path = CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/?';

function unsubscribe(id) {
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/' + id + '/', null, function () {
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

    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/post_anket/', json, function (JSONobj) {
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
function create_payment(id, sum, description, rate, currency) {
    let data = {
        "sum": sum,
        "description": description,
        "rate": rate,
        "currency": currency
    };

    let json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + `api/v1.0/summit_ankets/${id}/create_payment/`, json, function (JSONobj) {
        showPopup('Оплата прошла успешно.');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail)
        }
    });
}
function show_payments(id) {

    ajaxRequest(config.DOCUMENT_ROOT + `api/v1.0/summit_ankets/${id}/payments/`, null, function (data) {
        let payments_table = '';
        let sum, date_time;
        data.forEach(function (payment) {
            sum = payment.effective_sum_str;
            date_time = payment.created_at;
            payments_table += `<tr><td>${sum}</td><td>${date_time}</td></tr>`
        });
        $('#popup-payments table').html(payments_table);
        $('#popup-payments').css('display', 'block');
    }, 'GET', true, {
        'Content-Type': 'application/json'
    }, {
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail)
        }
    });
}

function getUnregisteredUsers() {
    let param = {};
    let search = $('#searchUsers').val();

    if (search) {
        param['search'] = search;
    }
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_search/?summit_id!=' + summit_id, param, function (data) {
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
        but.on('click', function () {
            let id = $(this).attr('data-id'),
                name = $(this).attr('data-name'),
                master = $(this).attr('data-master');
            $('#summit-value').val("0");
            $('#summit-value').attr('readonly', true);
            $('#popup textarea').val("");
            getDataForPopup(id, name, master);
            $('#popup').css('display', 'block');
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
    console.log(data);
    let sortFormTmpl, obj, rendered;
    sortFormTmpl = document.getElementById("sortForm").innerHTML;
    obj = {};
    obj.user = data[0];
    console.log(obj);
    rendered = _.template(sortFormTmpl)(obj);
    document.getElementById('sort-form').innerHTML = rendered;
}

function getUsersList(path, param) {
    param = param || {};
    let search = document.getElementsByName('fullsearch')[0].value;
    param.search = search;
    let el = document.getElementById('dep_filter');
    let value = el.options[el.selectedIndex].value;
    if (parseInt(value)) {
        param['user__department__title'] = el.options[el.selectedIndex].text;
    }
    param['summit'] = summit_id;
    $('.preloader').css('display', 'block');
    ajaxRequest(path, param, function (data) {
        console.log(data);
        let filter_data = {};
        filter_data.results  =  data.results.map(function (item) {
            return item.user;
        });
        console.log(filter_data);
        filter_data.user_table = data.user_table;
        console.log(filter_data);

        // getCurrentSummitSetting([['Пользователь', user_fields]]);
        let count = data.count;
            let page = 1;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
            let id = "users_list";
            let text = `Показано ${showCount} из ${count}`;
            let paginationConfig = {
                container: ".users__pagination",
                currentPage: page,
                pages: pages,
                callback: createUsersTable
            };
            makeDataTable(filter_data, id);
            makePagination(paginationConfig);
            $('.table__count').text(text);
            makeSortForm(data.user_table);
            $('.preloader').css('display', 'none');
            // orderTable.sort(createUsersTable);
        $('.create_payment').on('click', function (el) {
            let id = $(this).attr('data-anketId');
            $('#complete-payment').attr('data-id', id);
            $('#purpose-id').val(id);

            $('#popup-create_payment').css('display', 'block');
        });
        $('.show_payments').on('click', function (el) {
            let id = $(this).attr('data-anketId');
            show_payments(id);
        });
        // Sorting
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

                    getUsersList(path, data);
                });
            }

            return {
                addListener: addListener
            }
        })();
        orderTable.addListener();
        $('#users_list .del').on('click', function () {
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