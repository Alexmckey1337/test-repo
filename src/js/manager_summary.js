'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import {makeManagerTable} from "./modules/ManagerSummary/index";
import {initCharts} from "./modules/Chart/partners";
import {regLegendPlagin} from "./modules/Chart/config";

$(document).ready(function () {
    const ID = $('#managersFinances').attr('data-id');

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
