(function ($) {
    function addSummitInfo() {
        let width = 150,
            count = 1,
            position = 0,
            $carousel = $('#carousel'),
            $list = $carousel.find('ul'),
            $listElements;

        $listElements = $list.find('li');
        $carousel.find('.arrow-left').on('click', function () {
            position = Math.min(position + width * count, 0);
            $($list).css({
                marginLeft: position + 'px'
            });
        });
        $carousel.find('.arrow-right').on('click', function () {
            position = Math.max(position - width * count, -width * ($listElements.length - 3));
            $($list).css({
                marginLeft: position + 'px'
            });
        });
    }

    function addUserToSummit(data) {
        let id = data.id,
            name = data.fullname,
            master = data.master.fullname;
        let $summitVal = $('#summit-value');
        let $popup = $('#popup');
        $summitVal.val("0");
        $summitVal.attr('readonly', true);
        $popup.find('textarea').val('');
        setDataForPopup(id, name, master);
        $popup.css('display', 'block');
    }

    createSummitUsersTable();

    addSummitInfo();

    $('body').on('click', '#carousel li span', function () {
        $('#carousel li').removeClass('active');
        $(this).parent().addClass('active')
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
    $('#payment-form').on("submit", function (e) {
        e.preventDefault();
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

    $('#changeSumDelete').on('click', function () {
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
            description = $('#popup textarea').val(),
            summit_id = $('#date .active span').data('id');
        registerUser(id, summit_id, money, description);
        document.querySelector('#popup').style.display = 'none';
    });

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
        registerUserToSummit(json);
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

    function makePotencialSammitUsersList() {
        let param = {};
        let search = $('#searchUsers').val();
        if (search) {
            param['search'] = search;
        }
        param.summit_id = $('#date .active span').data('id');
        getPotencialSammitUsers(param).then(function (data) {
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
                setDataForPopup(id, name, master);
                $('#popup').css('display', 'block');
            });
        });
    }


    function setDataForPopup(id, name, master) {
        $('#complete').attr('data-id', id);
        $('#client-name').html(name);
        $('#responsible-name').html(master);
    }


    $('#departments_filter').select2();
    //    Events
    $("#add").on('click', function () {
        $('#addUser').css('display', 'block');
        initAddNewUser();
    });
    $('input[name="fullsearch"]').keyup(function () {
        let val = $(this).val();
        delay(function () {
            let data = {};
            data['search'] = val;
            createSummitUsersTable(data);
        }, 100);
    });

    $('#searchUsers').on('keyup', makePotencialSammitUsersList);
    $('#carousel li span').on('click', function () {
        $('.preloader').css('display', 'block');
        let config = {};
        config.summit = $(this).data('id');
        createSummitUsersTable(config);
    });
    $('#sort_save').on('click', function () {
        let path =
            $('.preloader').css('display', 'block');
        updateSettings(createSummitUsersTable);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });

    $('.quick-edit').on('click', function () {
        $('#popupDelete').css('display', 'block');
    });

    $.validate({
        lang: 'ru',
        form: '#createUser',
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(addUserToSummit).then(function() {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        }
    });
})(jQuery);