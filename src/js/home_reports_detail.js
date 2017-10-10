'use strict';
import {makeHomeReportDetailTable, getHomeReportDetailData,
        getHomeReportDetailTableData, makeCaption, sendForms} from "./modules/Reports/home_group";
import {showAlert} from "./modules/ShowNotifications/index";

$('document').ready(function () {
    let $additionalInformation = $('#additionalInformation'),
        $homeReports = $('#homeReports');

    getHomeReportDetailData().then(data => {
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
        if(!data.can_submit) {
            showAlert(data.cant_submit_cause);
            $('#save').attr({
                disabled: true
            });
            $homeReports.on('click', 'input', function () {
                showAlert(data.cant_submit_cause);
            });
        }
    });

    $('#save').on('click', function () {
        let btn = $(this),
            data = {};
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
                    data[field] = $(this).val().split('.').reverse().join('-');
                } else {
                    data[field] = $(this).data('value') || $(this).val();
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
        data.attends = attends;

        sendForms(btn, data);
    });
    $('.submitBtn').on('click', function (e) {
        e.preventDefault();
    });

});