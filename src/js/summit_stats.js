'use strict';
import 'jquery-timepicker/jquery.timepicker.js';
import 'jquery-timepicker/jquery.timepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import SummitStat from './modules/Statistics/summit';
import {getTabsFilter} from "./modules/Filter/index";
import {getCountFilter} from "./modules/Filter/index";
import {makePastorListNew, makePastorListWithMasterTree} from "./modules/MakeList/index";
import exportTableData from './modules/Export/index';
import {refreshFilter} from "./modules/Filter/index";

$('document').ready(function () {
    const summitId = $('#summit-title').data('summit-id');
    const summit = new SummitStat(summitId);
    $('#tabsFilterData')
        .val(moment().format('YYYY-MM-DD'))
        .datepicker({
            dateFormat: 'yyyy-mm-dd',
            autoClose: true,
            maxDate: new Date(),
            onSelect: function () {
                summit.makeDataTable();
            }
        });

    $('.week').on('click', function () {
        $('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('day_prev')) {
            $('#tabsFilterData').val(moment().subtract(1, 'days').format('YYYY-MM-DD'))
        } else {
            $('#tabsFilterData').val(moment().format('YYYY-MM-DD'))
        }
        summit.makeDataTable();
    });

    $('#tabs').find('li').on('click', function () {
        $('#tabs').find('li').removeClass('active');
        $(this).addClass('active');
        summit.makeDataTable();
    });

    getTabsFilter();

	$('#filter_button').on('click', function () {
		$('#filterPopup').show();
		$('#filterPopup').addClass('active');
		$('.bg').addClass('active');
	});
    // $('#filter_button').on('click', function () {
    //     let $fp = $('#filterPopup');
    //     $fp.addClass('active');
    //     $('.bg').addClass('active');
    //     // $fp.addClass('active').find('.pop_cont').on('click', function (e) {
    //     //     e.preventDefault();
    //     //     return false
    //     // });
    // });

    //Filter
    $('.apply-filter').on('click', function (e) {
        e.preventDefault();
        summit.makeDataTable();
        $(this).closest('#filterPopup').hide();
        let count = getCountFilter();
        $('#filter_button').attr('data-count', count);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        summit.makeDataTable();
    }, 500));

    $('.selectdb').select2();

    $('#department_filter').on('change', function () {
        $('#author_tree_filter').prop('disabled', true);
        let department_id = parseInt($(this).val()) || null;
        makePastorListNew(department_id, summitId, ['#author_tree_filter', '#author_filter']);
    });

    $('#author_tree_filter').on('change', function () {
        $('#author_filter').prop('disabled', true);
        let config = {};
        let author_tree = parseInt($(this).val());
        if (!isNaN(author_tree)) {
            config = {author_tree: author_tree}
        }
        makePastorListWithMasterTree(config, summitId, ['#author_filter'], null);
    });

    $('#export_table').on('click', function () {
        exportTableData(this, getTabsFilter());
    });

    $('#time_from').timepicker({
        timeFormat: 'H:mm',
        interval: 30,
        minTime: '0',
        maxTime: '23:30',
        dynamic: true,
        dropdown: true,
        scrollbar: true,
        change: function () {
            summit.makeDataTable();
        }
    });

    $('#time_to').timepicker({
        timeFormat: 'H:mm',
        interval: 30,
        minTime: '0',
        maxTime: '23:30',
        dynamic: true,
        dropdown: true,
        scrollbar: true,
        change: function () {
            summit.makeDataTable();
        }
    });

    summit.makeDataTable();
});