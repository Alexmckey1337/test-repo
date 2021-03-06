'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index";
import {postData, deleteData} from "./modules/Ajax/index";
import {
    createChurchPaymentsTable,
    cleanUpdateDealsPayment,
} from "./modules/Payment/index";
import updateSettings from './modules/UpdateSettings/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import errorHandling from './modules/Error';
import reverseDate from './modules/Date/index';
import {convertNum} from "./modules/ConvertNum/index";

$('document').ready(function () {
    createChurchPaymentsTable({});

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createChurchPaymentsTable({});
    }, 500));

    //Filter
    $('#filter_button').on('click', ()=> {
        //$('#filterPopup').show();
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });

    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchPaymentsTable, 'report_payment');
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createChurchPaymentsTable);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.selectdb').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });

    //Update payment
    $("#close-payment").on('click', function (e) {
        e.preventDefault();
        $('#popup-update_payment').css('display', 'none');
    });

    $('#payment_sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

    $('#delete-payment').on('click', function (e) {
        e.preventDefault();
        let id = $(this).attr('data-id');
        showConfirm('Удаление', 'Вы действительно хотите удалить данный платеж?', function () {
            deleteData(URLS.payment.edit_payment(id)).then(() => {
                showAlert('Платеж успешно удален!');
                $('#popup-update_payment').css('display', 'none');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                createChurchPaymentsTable({page: page});
            }).catch(err => errorHandling(err))
        }, _ => {});
    });

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
    });


    function submitPayment() {
        let id = $('#complete-payment').attr('data-id'),
            data = {
                "sum": convertNum($('#new_payment_sum').val(), '.'),
                "description": $('#popup-update_payment textarea').val(),
                "rate": convertNum($('#new_payment_rate').val(), '.'),
                "sent_date": reverseDate($('#payment_sent_date').val() ,'-'),
            };
        postData(URLS.payment.edit_payment(id), data, {method: 'PATCH'}).then(function () {
            let page = $('.pagination__input').val();
            $('#popup-update_payment').css('display', 'none');
            cleanUpdateDealsPayment();
            $('.preloader').css('display', 'block');
            createChurchPaymentsTable({page: page});
            showAlert('Платеж успешно изменен!');
            $('#complete-payment').prop('disabled', false);
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

});
