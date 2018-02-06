'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import moment from 'moment/min/moment.min.js';
import URLS from './modules/Urls';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index"
import {createPaymentsTable} from "./modules/Payment/index";
import {
    deleteDealsPayment,
    cleanUpdateDealsPayment,
    getPreFilterParam
} from "./modules/Payment/index";
import makeSelect from './modules/MakeAjaxSelect';
import {postData} from "./modules/Ajax/index";
import errorHandling from './modules/Error';

$(document).ready(function () {
    let date = new Date(),
        thisMonth = moment(date).startOf('month').format('DD.MM.YYYY'),
        lastMonth = moment(date).subtract(1, 'months').startOf('month').format('DD.MM.YYYY');

    $('#date_deal').val(thisMonth);
    createPaymentsTable();

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createPaymentsTable();
    }, 500));

    $('#export_table').on('click', function () {
        let search = 'search_purpose_fio',
            config = getPreFilterParam();
        exportTableData(this, config, search);
    });

    $('.tab-home-stats').find('.week').on('click', function () {
        $('.preloader').css('display', 'block');
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('week_now')) {
            $('#date_deal').val(thisMonth);
        } else if ($(this).hasClass('week_prev')) {
            $('#date_deal').val(lastMonth);
        } else {
            $('#date_deal').val('');
        }
        createPaymentsTable();
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

    $('#date_deal').datepicker({
        dateFormat: 'dd.mm.yyyy',
        autoClose: true,
        view: 'months',
        minView: 'months',
        onSelect: function () {
            $('.preloader').css('display', 'block');
            createPaymentsTable();
            $('.tab-home-stats').find('.week').removeClass('active');
        }
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
        updateSettings(createPaymentsTable, 'deal_payment');
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

    //Payments
    function submitPayment() {
        let id = $('#complete-payment').attr('data-id'),
            data = {
                "sum": $('#new_payment_sum').val(),
                "description": $('#popup-update_payment textarea').val(),
                "rate": $('#new_payment_rate').val(),
                "sent_date": $('#payment_sent_date').val().split('.').reverse().join('-'),
            };
        postData(URLS.payment.edit_payment(id), data, {method: 'PATCH'}).then(function () {
            let page = $('.pagination__input').val();
            $('#popup-update_payment').css('display', 'none');
            cleanUpdateDealsPayment();
            $('.preloader').css('display', 'block');
            createPaymentsTable({page: page});
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