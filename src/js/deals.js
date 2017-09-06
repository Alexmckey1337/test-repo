$(document).ready(function () {
    "use strict";

    $('.preloader').show();
    createIncompleteDealsTable();
    // createExpiredDealsTable();
    createDoneDealsTable();

    $('#overdue, #completed').hide();

    $('#tabs').find('li').on('click', 'a', function (e) {
        e.preventDefault();
        let tableSelector = $(this).attr('href');
        $(this).closest('#tabs').find('li').removeClass('current');
        $(this).parent().addClass('current');
        $('.tabs-cont').hide();
        $(tableSelector).show();
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createIncompleteDealsTable);
        // updateSettings(createExpiredDealsTable);
        updateSettings(createDoneDealsTable);
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

    // $('#complete').on('click', function () {
    //     let id = $(this).attr('data-id'),
    //         description = $('#deal-description').val();
    //     updateDeals(id, description);
    // });
    $('#popup-payments .detail').on('click', function () {
        let url = $(this).attr('data-detail-url');
        window.location.href = url;
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createIncompleteDealsTable();
        // createExpiredDealsTable();
        createDoneDealsTable();
    }, 500));

    // function updateDeals(id, description) {
    //     let data = {
    //         "done": true,
    //         "description": description
    //     };
    //     let config = JSON.stringify(data);
    //     ajaxRequest(URLS.deal.detail(id), config, function () {
    //         updateDealsTable();
    //         document.getElementById('popup').style.display = '';
    //     }, 'PATCH', true, {
    //         'Content-Type': 'application/json'
    //     }, {
    //         403: function (data) {
    //             data = data.responseJSON;
    //             showPopup(data.detail);
    //         }
    //     });
    // }

    $('#sent_date').datepicker({
        dateFormat: "yyyy-mm-dd",
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
        applyFilter(this, createIncompleteDealsTable);
        // applyFilter(this, createExpiredDealsTable);
        applyFilter(this, createDoneDealsTable);
    })

});

