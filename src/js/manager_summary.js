'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import {makeManagerTable} from "./modules/ManagerSummary/index";
import {initCharts} from "./modules/Chart/partners";
import {regLegendPlagin} from "./modules/Chart/config";

$(document).ready(function () {
    const ID = $('#managersFinances').attr('data-id');

    makeManagerTable(ID);

    $('.prefilter-group').find('.month').on('click', function () {
        let id = $('#managersFinances').attr('data-id'),
            period = $(this).attr('data-period'),
            showChart = $('#show_chart').is(':checked');
        $('.preloader').css('display', 'block');
        $(this).closest('.prefilter-group').find('.month').removeClass('active');
        $(this).addClass('active');
        if (showChart) {
            initCharts(id, {period}, true);
        } else {
            makeManagerTable(id, {period});
        }
    });

    $('#show_chart').on('change', function () {
        let id = $('#managersFinances').attr('data-id'),
            period = $('.prefilter-group').find('.month.active').attr('data-period');
       $('.preloader').css('display', 'block');
       if ($(this).is(':checked')) {
           $('#managersFinances').html('');
           $('#managersPartners').html('');
           initCharts(id, {period});
       } else {
           window.ChartFinances.destroy();
           window.ChartPercent.destroy();
           window.ChartPartners.destroy();
           makeManagerTable(id, {period});
       }
    });

    regLegendPlagin();

    $('#stats_manager').select2();
    
    $('#stats_manager').on('change', function () {
        let id = $(this).val(),
            period = $('.prefilter-group').find('.month.active').attr('data-period'),
            showChart = $('#show_chart').is(':checked');
        $('.preloader').css('display', 'block');
        $('#managersFinances').attr('data-id', id);
        if (showChart) {
            initCharts(id, {period}, true);
        } else {
            makeManagerTable(id, {period});
        }
    })

});
