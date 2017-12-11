'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import {renderStats} from "./modules/ManagerSummary/index";
import {regLegendPlagin} from "./modules/Chart/config";

$(document).ready(function () {
    const ID = $('#managersFinances').attr('data-id');

    renderStats(ID);

    $('.prefilter-group').find('.month').on('click', function () {
        let id = $('#managersFinances').attr('data-id'),
            period = $(this).attr('data-period');
        $('.preloader').css('display', 'block');
        $(this).closest('.prefilter-group').find('.month').removeClass('active');
        $(this).addClass('active');
        renderStats(id, {period}, true);
    });

    regLegendPlagin();

    $('#stats_manager').select2();
    
    $('#stats_manager').on('change', function () {
        let id = $(this).val(),
            period = $('.prefilter-group').find('.month.active').attr('data-period');
        $('.preloader').css('display', 'block');
        $('#managersFinances').attr('data-id', id);
        renderStats(id, {period}, true);
    })

});
