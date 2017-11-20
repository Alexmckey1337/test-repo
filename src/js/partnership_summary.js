'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import updateSettings from './modules/UpdateSettings/index';
import {PartnershipSummaryTable, partnershipSummaryTable} from "./modules/PartnerSummary/index";

$(document).ready(function () {
    const USER_ID = $('body').data('user');
    let dateReports = new Date(),
        thisPeriod = moment(dateReports).format('MM/YYYY'),
        lastPeriod = moment(dateReports).subtract(1, 'month').format('MM/YYYY'),
        configData = {
            year: moment(dateReports).format('YYYY'),
            month: moment(dateReports).format('MM')
        };

    $('.set-date').find('input').val(thisPeriod);

    $('#date_field_stats').datepicker({
        maxDate: new Date(),
        startDate: new Date(),
        view: 'months',
        minView: 'months',
        dateFormat: 'mm/yyyy',
        autoClose: true,
        onSelect: (formattedDate) => {
            if (formattedDate != '') {
                $('.preloader').css('display', 'block');
                $('#main').find('.prefilter-group').find('.month').removeClass('active');
                (formattedDate == thisPeriod) ? partnershipSummaryTable() : partnershipSummaryTable({}, false);
            }
        }
    });

    PartnershipSummaryTable(configData);

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(PartnershipSummaryTable, 'partner_summary');
    });

    $('.prefilter-group').find('.month').on('click', function () {
        $('.preloader').css('display', 'block');
        $(this).closest('.prefilter-group').find('.month').removeClass('active');
        $(this).addClass('active');
        if (!$(this).hasClass('month_prev')) {
            $('#date_field_stats').val(`${thisPeriod}`);
            partnershipSummaryTable();
        } else {
            $('#date_field_stats').val(`${lastPeriod}`);
            partnershipSummaryTable({}, false);
        }
    });

});
