'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import updateSettings from './modules/UpdateSettings/index';
import {
    PartnershipSummaryTable,
    PartnershipCompareSummaryTable,
    partnershipSummaryTable
} from "./modules/PartnerSummary/index";

$(document).ready(function () {
    const USER_ID = $('body').data('user');
    let dateReports = new Date(),
        thisPeriod = moment(dateReports).format('MM/YYYY'),
        lastPeriod = moment(dateReports).subtract(1, 'month').format('MM/YYYY'),
        configData = {
            year: moment(dateReports).format('YYYY'),
            month: moment(dateReports).format('MM')
        };

    $('#date_field_stats').val(thisPeriod)
        .datepicker({
            maxDate: new Date(),
            startDate: new Date(),
            view: 'months',
            minView: 'months',
            dateFormat: 'mm/yyyy',
            autoClose: true,
            onSelect: (formattedDate) => {
                if (formattedDate != '') {
                    $('.preloader').css('display', 'block');
                    (formattedDate === thisPeriod) ? partnershipSummaryTable() : partnershipSummaryTable({}, false);
                }
            }
        });

    $('#date_field_compare').val(lastPeriod)
        .datepicker({
        maxDate: new Date(),
        startDate: new Date(),
        view: 'months',
        minView: 'months',
        dateFormat: 'mm/yyyy',
        autoClose: true,
        onSelect: (formattedDate) => {
            if (formattedDate != '') {
                $('.preloader').css('display', 'block');
            }
        }
    });

    PartnershipSummaryTable(configData);

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(PartnershipSummaryTable, 'partner_summary');
        $('#date_field_stats').val(thisPeriod);
    });

    $('#showCompare').on('change', function () {
       if ($(this).is(':checked')) {
           $('#date_field_compare').prop('disabled', false);
           PartnershipCompareSummaryTable();
       } else {
           $('#date_field_compare').prop('disabled', true);
       }
    });

});
