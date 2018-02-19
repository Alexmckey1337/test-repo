'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import {initChart, initBarChart, initPieChart, updatePieChart} from "./modules/Chart/summit";
import {makeResponsibleSummitStats} from "./modules/Statistics/summit";
import {regLegendPlagin} from "./modules/Chart/config";

function getBoxWidth(labelOpts, fontSize) {
    return labelOpts.usePointStyle ?
        fontSize * Math.SQRT2 :
        labelOpts.boxWidth;
}


$('document').ready(function () {
    let summitId = $('#summit-title').data('summit-id');
    initChart(summitId);
    initBarChart(summitId);

    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block').find('.pop_cont').on('click', function (e) {
            e.preventDefault();
            return false
        });
    });

    $('.selectdb').select2();

    let data = {
        without_pagination: '',
        level_gte: 4,
        summit: summitId
    };

    makeResponsibleSummitStats(data, ['#master']);

    initPieChart();

    $('#departments_filter').on('change', function () {
        let department_id = parseInt($(this).val()) || null,
            update = true,
            data;
        if (department_id !== null) {
            data = {
                without_pagination: '',
                level_gte: 4,
                department: department_id,
                summit: summitId,
            }
        } else {
            data = {
                without_pagination: '',
                level_gte: 4,
                summit: summitId,
            }
        }
        makeResponsibleSummitStats(data, ['#master']);
        initChart(summitId, update);
        initBarChart(summitId, update);
        $('#pie_stats').hide();
        $(this).closest('label').find('.preloader_chart').css('display', 'block');
    });

    $('#master').on('change', function () {
        let update = true,
            filter = $('#master').val();
        initChart(summitId, update);
        initBarChart(summitId, update);
        if (filter !== 'ВСЕ') {
            updatePieChart(summitId, filter);
            $('#pie_stats').show();
        } else {
            $('#pie_stats').hide();
        }
        $(this).closest('label').find('.preloader_chart').css('display', 'block');
    });

    $('.preloader_chart').css('display', 'none');

    $('#print').on('click', function () {
        $('body').addClass('is-print');
        setTimeout(window.print, 300);
    });

    (function () {
        let afterPrint = function () {
            $('body').removeClass('is-print');
        };

        if (window.matchMedia) {
            let mediaQueryList = window.matchMedia('print');
            mediaQueryList.addListener(function (mql) {
                if (!mql.matches) {
                    afterPrint();
                }
            });
        }

        window.onafterprint = afterPrint;
    }());

    regLegendPlagin();

});