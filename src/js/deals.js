'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import {showAlert} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {DealsTable, updateDealsTable, createDealsPayment, dealsTable, updateDeal} from './modules/Deals/index';
import getSearch from './modules/Search/index';
import {getFilterParam} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';

$(document).ready(function () {
    $('.preloader').css('display', 'block');
    DealsTable({done: 3});

    //Tabs
    $('#tabs').find('li').on('click', 'a', function (e) {
        $('.preloader').css('display', 'block');
        e.preventDefault();
        let status = $(this).attr('data-status');
        let config = {
            done: status
        };
        Object.assign(config, getSearch('search'));
        Object.assign(config, getFilterParam());
        DealsTable(config);
        $(this).closest('#tabs').find('li').removeClass('current');
        $(this).parent().addClass('current');
    });

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
        $('#popup-create_payment').css('display', 'none');
    });

    $("#popup-payments .top-text span").on('click', function (el) {
        $('#popup-payments').css('display', 'none');
        $('#popup-payments table').html('');
    });

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
    });

    $('#complete-payment').on('click', _.debounce(function (e) {
        e.preventDefault();
        $(this).prop('disabled', true);
        let id = $(this).attr('data-id'),
            sum = $('#new_payment_sum').val(),
            description = $('#popup-create_payment textarea').val();
        createDealsPayment(id, sum, description).then(function () {
            updateDealsTable();
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#complete-payment').prop('disabled', false);
            $('#popup-create_payment').css('display', 'none');
        }).catch((res) => {
            let error = JSON.parse(res.responseText),
                errKey = Object.keys(error),
                html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
            $('#complete-payment').prop('disabled', false);
            showAlert(html);
        });
    }, 500));

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
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    //Update deal
    $("#close-deal").on('click', function (e) {
        e.preventDefault();
        clearDealForm();
        $('#popup-create_deal').css('display', 'none');
    });

    function clearDealForm() {
        let popup = $('#popup-create_deal'),
            $input = popup.find('input, textarea');
        $input.each(function () {
            $(this).val('');
        });
        popup.find('select').val('1').trigger("change");
    }

    $('#new_deal_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

    $('#send_new_deal').on('click', _.debounce(function () {
        $(this).prop('disabled', true);
    let id = $(this).attr('data-id'),
        description = $('#popup-create_deal textarea').val(),
        value = $('#new_deal_sum').val(),
        date = $('#new_deal_date').val().trim().split('.').reverse().join('-'),
        type = $('#new_deal_type').val(),
        data = {
            'date_created': date,
            'value': value,
            'description': description,
            'type': type,
        };

    if (value && date) {
        updateDeal(id, data).then(() => {
            let page = $('#sdelki').find('.pagination__input').val();
            $('.preloader').css('display', 'block');
            dealsTable({page:page});
            showAlert('Редактирование сделки прошло успешно');
            clearDealForm();
            $('#send_new_deal').prop('disabled', false);
            $('#popup-create_deal').css('display', 'none');
        }).catch((err) => {
            $('#send_new_deal').prop('disabled', false);
            showAlert(err);
        });
    } else {
        showAlert('Заполните поле суммы и дату.');
    }
}, 500));

});

