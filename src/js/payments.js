'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import URLS from './modules/Urls';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index"
import {createPaymentsTable} from "./modules/Payment/index";
import {deleteDealsPayment, updateDealsPayment, cleanUpdateDealsPayment} from "./modules/Payment/index";
import makeSelect from './modules/MakeAjaxSelect';

$(document).ready(function () {
    createPaymentsTable({});

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createPaymentsTable({});
    }, 500));

    $('#export_table').on('click', function () {
        let search = 'search_purpose_fio',
            config = {};
        exportTableData(this, config, search);
    });

    $('#filter_button').on('click', ()=> {
        //$('#filterPopup').show();
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');

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
    });

    $('#complete-payment').on('click', _.debounce(function (e) {
        e.preventDefault();
        $(this).prop('disabled', true);
        let id = $(this).attr('data-id'),
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
            $('#complete-payment').prop('disabled', false);
        }).catch((res) => {
            $('#complete-payment').prop('disabled', false);
            showAlert(res, 'Ошибка');
        });
    }, 500));

    function parse(data, params) {
        params.page = params.page || 1;
        const results = [];
        results.push({
            id: '',
            text: 'ВСЕ',
        });
        data.results.forEach(function makeResults(element, index) {
            results.push({
                id: element.id,
                text: element.title,
            });
        });
        return {
            results: results,
            pagination: {
                more: (params.page * 100) < data.count
            }
        };
    }

    function formatRepo(data) {
        if (data.id === '') {
            return 'ВСЕ';
        }
        return `<option value="${data.id}">${data.text}</option>`;
    }

    makeSelect($('#manager'), URLS.payment.supervisors(), parse, formatRepo);
    makeSelect($('#search_purpose_manager_fio'), URLS.user.managers(), parse, formatRepo);

});