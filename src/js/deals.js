'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import moment from 'moment/min/moment.min.js';
import {showAlert} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import URLS from './modules/Urls/index';
import {postData} from "./modules/Ajax/index";
import {
    DealsTable,
    updateDealsTable,
    dealsTable,
    makeDuplicateDealsWithCustomPagin,
    deleteDeal,
} from './modules/Deals/index';
import updateSettings from './modules/UpdateSettings/index';
import reverseDate from './modules/Date/index';
import errorHandling from './modules/Error';
import {convertNum} from "./modules/ConvertNum/index";

$(document).ready(function () {
        let date = new Date(),
        thisMonthStart = moment(date).startOf('month').format('DD.MM.YYYY'),
        thisMonthEnd = moment(date).endOf('month').format('DD.MM.YYYY'),
        lastMonthStart = moment(date).subtract(1, 'months').startOf('month').format('DD.MM.YYYY'),
        lastMonthEnd = moment(date).subtract(1, 'months').endOf('month').format('DD.MM.YYYY'),
        configData = {
        from_date: reverseDate(thisMonthStart, '-'),
        to_date: reverseDate(thisMonthEnd, '-'),
    };

    $('.preloader').css('display', 'block');
    DealsTable(configData);

    $('#statusTabs').on('click', 'button', function () {
        $('#statusTabs').find('li').each(function () {
            $(this).removeClass('current');
        });
        $(this).parent().addClass('current');
        $('.preloader').css('display', 'block');
        dealsTable();
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(dealsTable, 'deal');
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

    // Events
    $('#date_range').datepicker({
        dateFormat: 'dd.mm.yyyy',
        range: true,
        autoClose: true,
        multipleDatesSeparator: '-',
        onSelect: function (date) {
            if (date.length > 10) {
                $('.preloader').css('display', 'block');
                dealsTable();
                $('.tab-home-stats').find('.week').removeClass('active');
            } else if (date == '') {
                $('.preloader').css('display', 'block');
                dealsTable();
                $('.tab-home-stats').find('.week').removeClass('active');
            }
        }
    });

    $('.tab-home-stats').find('.week').on('click', function () {
        $('.preloader').css('display', 'block');
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('week_now')) {
            $('.set-date').find('input').val(`${thisMonthStart}-${thisMonthEnd}`);
        } else if ($(this).hasClass('week_prev')) {
            $('.set-date').find('input').val(`${lastMonthStart}-${lastMonthEnd}`);
        } else {
            $('.set-date').find('input').val('');
        }
        dealsTable();
    });

    $('#filter_button').on('click', function () {
        //$('#filterPopup').css('display', 'block');
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });

    $('.selectdb').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
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

    //Find duplicates
    $('#duplicates').on('click', function () {
       $('.preloader').css('display', 'block');
        makeDuplicateDealsWithCustomPagin();
    });

    $('.pop-up__table').find('.close_pop').on('click', function () {
        $('.pop-up_duplicate__table').css('display', 'none');
    });

    $('#delete_deal').on('click', function (e) {
        e.preventDefault();
        let id = $(this).attr('data-id'),
            pageCount = $('#sdelki').find('.pagination__input').first().val();
        deleteDeal(id, pageCount, dealsTable);
    });

    $('#date_range').val(`${thisMonthStart}-${thisMonthEnd}`);

    //Payments
    function submitPayment() {
        let id = $('#complete-payment').attr('data-id'),
            data = {
                "sum": convertNum($('#new_payment_sum').val(), '.'),
                "description": $('#popup-create_payment textarea').val(),
                "rate": convertNum($('#new_payment_rate').val(), '.'),
                "sent_date": reverseDate($('#sent_date').val(), '-'),
                "operation": $('#operation').val()
            },
            type = $('#statusTabs').find('.current button').attr('data-type'),
            url = (type === 'people') ? URLS.deal.create_uah_payment(id) : URLS.church_deal.create_uah_payment(id);

        postData(url, data).then(function () {
            updateDealsTable();
            showAlert('Оплата прошла успешно.');
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#complete-payment').prop('disabled', false);
            $('#popup-create_payment').css('display', 'none');
        }).catch(err => {
            errorHandling(err);
            $('#complete-payment').prop('disabled', false);
        });
    }

    $.validate({
        lang: 'ru',
        form: '#payment-form',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            submitPayment();
            $('#complete-payment').prop('disabled', true);

            return false;
        }
    });

    function submitDeal() {
        let id = $('#send_new_deal').attr('data-id'),
            description = $('#popup-create_deal textarea').val(),
            value = $('#new_deal_sum').val(),
            date = reverseDate($('#new_deal_date').val(), '-'),
            type = $('#new_deal_type').val(),
            data = {
                'date_created': date,
                'value': value,
                'description': description,
                'type': type,
            },
            typeTable = $('#statusTabs').find('.current button').attr('data-type');

        if (value && date) {
            let url = (typeTable === 'people') ? URLS.deal.detail(id) : URLS.church_deal.detail(id);
            postData(url, data, {method: 'PATCH'}).then(() => {
                let page = $('#sdelki').find('.pagination__input').val();
                $('.preloader').css('display', 'block');
                dealsTable({page: page});
                showAlert('Редактирование сделки прошло успешно');
                clearDealForm();
                $('#send_new_deal').prop('disabled', false);
                $('#popup-create_deal').css('display', 'none');
            }).catch(err => {
                $('#send_new_deal').prop('disabled', false);
                errorHandling(err);
            });
        } else {
            showAlert('Заполните поле суммы и дату.');
        }
    }

    $.validate({
        lang: 'ru',
        form: '#deal-form',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            submitDeal();
            $('#send_new_deal').prop('disabled', true);

            return false;
        }
    });

});

