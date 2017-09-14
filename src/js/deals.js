$(document).ready(function () {
    "use strict";

    $('.preloader').show();
    DealsTable({done: 3});

    //Tabs
    $('#tabs').find('li').on('click', 'a', function (e) {
        $('.preloader').show();
        e.preventDefault();
        let status = $(this).attr('data-status');
        let config = {
            done: status
        };
        Object.assign(config, getFilterParam());
        DealsTable(config);
        $(this).closest('#tabs').find('li').removeClass('current');
        $(this).parent().addClass('current');
    });

    function DealsTable(config) {
        getDeals(config).then(data => {
            makeDealsTable(data);
        });
    }

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(dealsTable);
    });

    $("#close-payment").on('click', function (e) {
        e.preventDefault();
        $('#new_payment_rate').val(1);
        $('#in_user_currency').text('');
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

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
        let id = $(this).find('button[type="submit"]').attr('data-id'),
            sum = $('#new_payment_sum').val(),
            description = $('#popup-create_payment textarea').val();
        let data = $(this).serializeArray();
        createDealsPayment(id, sum, description).then(function () {
            updateDealsTable();
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#popup-create_payment').css('display', 'none');
        }).catch((res) => {
            let error = JSON.parse(res.responseText),
                errKey = Object.keys(error),
                html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
            showPopup(html);
        });
    });

    $('#popup-payments .detail').on('click', function () {
        let url = $(this).attr('data-detail-url');
        window.location.href = url;
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        dealsTable();
    }, 500));

    $('#sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });

    $('.selectdb').select2();

    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    
    $('.apply-filter').on('click', function () {
        applyFilter(this, dealsTable);
    })

});

