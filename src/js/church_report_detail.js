'use strict';
import {showAlert} from "./modules/ShowNotifications/index";
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import {getChurchReportDetailData, makeCaption, makeReportData, sendForms} from "./modules/Reports/church";

$('document').ready(function () {
    let $additionalInformation = $('#additionalInformation');
    let $reportBlock = $('#report_block');
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    getChurchReportDetailData().then(data => {
        $additionalInformation.append(makeCaption(data));
        $reportBlock.append(makeReportData(data));
        return data;
    }).then(data => {
        if (data.status === 2) {
            $('#save').text('Редактировать').attr('data-click', false);
            $('#databaseChurchReportsForm').find('input:not(:hidden), textarea').each(function () {
                $(this).attr('disabled', true);
            })
        }
        $('#total_tithe, #total_donations').on('input', function () {
            let tithe = $('#total_tithe').val(),
                donat = $('#total_donations').val(),
                calc = (+tithe + +donat)*0.15;
            $('#transfer_payments').val(calc.toFixed(1));
        });
        if(!data.can_submit) {
            showAlert(data.cant_submit_cause);
            $('#save').attr({
                disabled: true
            });
            $('#databaseChurchReportsForm').on('click', 'input', function () {
                showAlert(data.cant_submit_cause);
            });
        }
        $.validate({
            lang: 'ru',
            form: '#databaseChurchReportsForm'
        });
    });

    $('#save').on('click', function () {
        let btn = $(this),
            data = {},
            $input = $('#databaseChurchReportsForm').find('input:not(:hidden), textarea');
        if (btn.attr('data-click') == "false") {
            btn.attr({
                'data-click': true,
                'data-update': true,
            });
            $input.each(function () {
                $(this).attr('disabled', false);
            });

            btn.text('Сохранить');
            return false;
        }
        $input.each(function () {
            let field = $(this).attr('name');
            if (field) {
                if (field == 'date') {
                    data[field] = $(this).val().split('.').reverse().join('-');
                } else {
                    data[field] = $(this).val();
                }
            }
        });
        sendForms(btn, data);
    });

    $('.submitBtn').on('click', function (e) {
        e.preventDefault();
    });

});