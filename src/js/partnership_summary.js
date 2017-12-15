'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment';
import updateSettings from './modules/UpdateSettings/index';
import {
    PartnershipSummaryTable,
    PartnershipCompareSummaryTable,
    partnershipSummaryTable,
    partnershipCompareSummaryTable,
    updatePartnershipSummaryTable,
    updatePartnershipCompareSummaryTable
} from "./modules/PartnerSummary/index";

$(document).ready(function () {
    let dateReports = new Date(),
        thisPeriod = moment(dateReports).format('MM/YYYY'),
        lastPeriod = moment(dateReports).subtract(1, 'month').format('MM/YYYY'),
        configData = {
            year: moment(dateReports).format('YYYY'),
            month: moment(dateReports).format('MM')
        };
    // Temporary solution. Need to rewrite on React/Redux
    window.state = {
            table_columns: null,
            result: null,
            resultCompare: null,
            firstDate: null,
            secondDate: null,
            canEdit: null,
        };

    $('#date_field_stats').val(thisPeriod)
        .datepicker({
            maxDate: new Date(),
            startDate: new Date(),
            view: 'months',
            minView: 'months',
            dateFormat: 'mm/yyyy',
            autoClose: true,
            onSelect: (formattedDate, date) => {
                let showCompare = $('#showCompare').is(':checked'),
                    flag = (formattedDate === thisPeriod);
                window.state = Object.assign(window.state, {
                    firstDate: moment(date).toISOString(),
                    canEdit: flag,
                });
                if (showCompare) {
                    PartnershipCompareSummaryTable({}, true);
                } else {
                    partnershipSummaryTable();
                }
            }
        });

    $('#date_field_compare').val(lastPeriod)
        .datepicker({
        maxDate: new Date(moment(dateReports).subtract(1, 'month').format()),
        startDate: new Date(),
        view: 'months',
        minView: 'months',
        dateFormat: 'mm/yyyy',
        autoClose: true,
        onSelect: (formattedDate, date) => {
            window.state = Object.assign(window.state, {secondDate: moment(date).toISOString()});
            PartnershipCompareSummaryTable();
        }
    });

    PartnershipSummaryTable(configData);

    // Sort table
    $('#sort_save').on('click', function () {
        let showCompare = $('#showCompare').is(':checked');
        if (showCompare) {
            updateSettings(partnershipCompareSummaryTable, 'partner_summary');
        } else {
            updateSettings(PartnershipSummaryTable, 'partner_summary');
        }
    });

    $('#showCompare').on('change', function () {
       if ($(this).is(':checked')) {
           $('#date_field_compare').prop('disabled', false);
           if (window.state.secondDate) {
                updatePartnershipCompareSummaryTable();
           } else {
               window.state = Object.assign(window.state, {secondDate: moment(dateReports).subtract(1, 'month').toISOString()});
               PartnershipCompareSummaryTable();
           }
       } else {
           $('#date_field_compare').prop('disabled', true);
           updatePartnershipSummaryTable();
       }
    });

});
