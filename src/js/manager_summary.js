'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
// import moment from 'moment/min/moment.min.js';
import {makeManagerTable} from "./modules/ManagerSummary/index";
import {initCharts} from "./modules/Chart/partners";
import {regLegendPlagin} from "./modules/Chart/config";

$(document).ready(function () {
    const ID = $('#managersFinances').attr('data-id');
    // let dateReports = new Date(),
    //     thisPeriod = moment(dateReports).format('MM/YYYY'),
    //     lastPeriod = moment(dateReports).subtract(1, 'month').format('MM/YYYY'),
    //     configData = {
    //         year: moment(dateReports).format('YYYY'),
    //         month: moment(dateReports).format('MM')
    //     };
    //
    // $('.set-date').find('input').val(thisPeriod);

    // $('#set_month').datepicker({
    //     maxDate: new Date(),
    //     startDate: new Date(),
    //     view: 'months',
    //     minView: 'months',
    //     dateFormat: 'mm/yyyy',
    //     autoClose: true,
    //     onSelect: (formattedDate) => {
    //         if (formattedDate != '') {
    //             $('.preloader').css('display', 'block');
    //             $('#main').find('.prefilter-group').find('.month').removeClass('active');
    //         }
    //     }
    // });

    makeManagerTable(ID);

    $('.prefilter-group').find('.month').on('click', function () {
        let period = $(this).attr('data-period'),
            showChart = $('#show_chart').is(':checked');
        $('.preloader').css('display', 'block');
        $(this).closest('.prefilter-group').find('.month').removeClass('active');
        $(this).addClass('active');
        if (showChart) {
            initCharts(ID, {period}, true);
        } else {
            makeManagerTable(ID, {period});
        }
    });

    $('#show_chart').on('change', function () {
       let period = $('.prefilter-group').find('.month.active').attr('data-period');
       $('.preloader').css('display', 'block');
       if ($(this).is(':checked')) {
           $('#managersFinances').html('');
           $('#managersPartners').html('');
           initCharts(ID, {period});
       } else {
           window.ChartFinances.destroy();
           window.ChartPartners.destroy();
           makeManagerTable(ID, {period});
       }
    });

    regLegendPlagin();

});
