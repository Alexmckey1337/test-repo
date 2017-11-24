'use strict';
import moment from 'moment/min/moment.min.js';
import {
    makeHomeReportDetailTable,
    getHomeReportDetailData,
    getHomeReportDetailTableData,
    makeCaption,
    sendForms,
    handleImgFileSelect
} from "./modules/Reports/home_group";
import {showAlert} from "./modules/ShowNotifications/index";
import reverseDate from './modules/Date/index';

$('document').ready(function () {
    let $additionalInformation = $('#additionalInformation'),
        $homeReports = $('#homeReports');

    getHomeReportDetailData().then(data => {
        let dateReportsFormatted = new Date( reverseDate(data.date, ',')),
            thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).subtract(6, 'days').format() : moment(dateReportsFormatted).day(1).format(),
            thisSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
        if (data.status === 1 || data.status === 3) {
            getHomeReportDetailTableData().then(data => {
                makeHomeReportDetailTable(data);
            });
        } else {
            $('#save').text('Редактировать').attr('data-click', false);
            let field = {
                results: data.attends,
                table_columns: data.table_columns
            };
            makeHomeReportDetailTable(field);
            let $input = $homeReports.find('input');
            $input.each(function () {
                $(this).attr('disabled', true);
            })
        }
        $additionalInformation.html(makeCaption(data));
        $('#report_date').datepicker({
            autoClose: true,
            minDate: new Date(thisMonday),
            maxDate: new Date(thisSunday),
        });
        $('#clear_img').on('click', function () {
            $('#file').val('');
            $('#hg_attds').attr('src', '');
            if (!/safari/i.test(navigator.userAgent)) {
                $('#file').attr('type', '');
                $('#file').attr('type', 'file');
            }
        });
        if(!data.can_submit) {
            showAlert(data.cant_submit_cause);
            $('#save').attr({
                disabled: true
            });
            $homeReports.on('click', 'input', function () {
                showAlert(data.cant_submit_cause);
            });
        }
        $('#file').on('change', handleImgFileSelect);
    });

    $('#save').on('click', function () {
        let btn = $(this),
            data = new FormData();
        if (btn.attr('data-click') == "false") {
            btn.attr({
                'data-click': true,
                'data-update': true,
            });
            $homeReports.find('input').each(function () {
                $(this).attr('disabled', false);
            });

            btn.text('Сохранить');
            return false;
        }

        $additionalInformation.find('input').each(function () {
            let field = $(this).data('name');
            if (field) {
                if (field == 'date') {
                    data.append(field, reverseDate($(this).val(), '-'));
                } else if (field == 'image') {
                    ($(this)[0].files.length > 0) && data.append(field, $(this)[0].files[0] );
                } else {
                    data.append(field, $(this).data('value') || $(this).val() );
                }
            }
        });

        let $items = $homeReports.find('tbody').find('tr');
        let attends = [];
        $items.each(function () {
            let $input = $(this).find('input');
            let data = {};
            $input.each(function () {
                let elem = $(this);
                let name = elem.attr('name');
                if (name == 'attended') {
                    data[elem.attr('name')] = elem.prop("checked")
                } else if (name == 'user_id') {
                    data[elem.attr('name')] = parseInt(elem.val());
                } else {
                    data[elem.attr('name')] = elem.val();
                }
            });
            attends.push(data);
        });
        data.append('attends', JSON.stringify(attends));
        sendForms(btn, data);
    });
    $('.submitBtn').on('click', function (e) {
        e.preventDefault();
    });

});