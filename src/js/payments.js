'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index"
import {createPaymentsTable} from "./modules/Payment/index";
import {deleteDealsPayment, updateDealsPayment, cleanUpdateDealsPayment} from "./modules/Payment/index";

$(document).ready(function () {
    createPaymentsTable({});

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createPaymentsTable({});
    }, 500));

    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        let search = 'search_purpose_fio',
            config = {};
        exportTableData(this, config, search).then(function () {
            $('.preloader').css('display', 'none');
        });
    });

    $('#filter_button').on('click', ()=> {
        $('#filterPopup').show();
    });
    $('#date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#sent_date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#sent_date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#purpose_date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        view: 'months',
        minView: 'months',
        position: "left top",
    });
    $('#purpose_date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        view: 'months',
        minView: 'months',
        position: "left top",
    });

    $('#payment_sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

    $('.custom_select').select2();

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createPaymentsTable);
    });

    //Filter
    $('.apply-filter').on('click', function () {
        applyFilter(this, createPaymentsTable);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.selectdb').select2();

    //Update payment
    $("#close-payment").on('click', function (e) {
        e.preventDefault();
        $('#popup-update_payment').css('display', 'none');
    });

    $('#delete-payment').on('click', function (e) {
        e.preventDefault();
        let id = $(this).attr('data-id');
        showConfirm('Удаление', 'Вы действительно хотите удалить данный платеж?', function () {
            deleteDealsPayment(id).then(() => {
                showAlert('Платеж успешно удален!');
                $('#popup-update_payment').css('display', 'none');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                createPaymentsTable({page: page});
            }).catch((res) => {
                showAlert(res, 'Ошибка');
            });
        }, () => {});
    });

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
        let id = $(this).find('button[type="submit"]').attr('data-id'),
            data = {
                "sum": $('#new_payment_sum').val(),
                "description": $('#popup-update_payment textarea').val(),
                "rate": $('#new_payment_rate').val(),
                "sent_date": $('#payment_sent_date').val().split('.').reverse().join('-'),
            };
        updateDealsPayment(id, data).then(function () {
            let page = $('.pagination__input').val();
            $('#popup-update_payment').css('display', 'none');
            cleanUpdateDealsPayment();
            $('.preloader').css('display', 'block');
            createPaymentsTable({page: page});
            showAlert('Платеж успешно изменен!');
        }).catch((res) => {
            showAlert(res, 'Ошибка');
        });
    });

});