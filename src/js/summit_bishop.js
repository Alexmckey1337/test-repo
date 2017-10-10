'use strict';
import BishopReport from './modules/Reports/bishop_report';
import PrintMasterStat from './modules/Print/printMasterStat';
import {refreshFilter} from "./modules/Filter/index";
import {getCountFilter} from "./modules/Filter/index";

$('document').ready(function () {
    const summitId = $('#summit-title').data('summit-id');
    const report = new BishopReport(summitId);
    report.makeTable();

    //Filter
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block').find('.pop_cont').on('click', function (e) {
            e.preventDefault();
            return false
        });
    });

    $('#applyFilter').on('click', function () {
         report.makeTable();
         $(this).closest('#filterPopup').hide();
         let count = getCountFilter();
        $('#filter_button').attr('data-count', count);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

     $('#download').on('click', function () {
        let stat = new PrintMasterStat(summitId);
        stat.show();
    });

     $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        report.makeTable();
    }, 500));

     $('.selectdb').select2();

});