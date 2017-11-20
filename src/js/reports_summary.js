'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import URLS from './modules/Urls/index';
import getData from './modules/Ajax/index';
import updateSettings from './modules/UpdateSettings/index';
import {getPastorsByDepartment, getChurches} from "./modules/GetList/index";
import parseUrlQuery from './modules/ParseUrl/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {churchPastorReportsTable, makeChurchPastorReportsTable, getChurchPastorReports} from "./modules/Reports/reports_summary";

$('document').ready(function () {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#tree_filter'),
        $churchFilter = $('#church_filter'),
        $responsibleFilter = $('#responsible_filter'),
        initResponsible = false,
        urlChurch = URLS.church.for_select(),
        init = false;
    const USER_ID = $('body').data('user'),
          PATH = window.location.href.split('?')[1];

    function filterInit(set = null) {
        if (!init) {
            if (set != null) {
                $('#departments_filter').find(`option[value='${set.department_id}']`).prop('selected', true);
                $('.apply-filter').trigger('click');
            } else {
                getPastorsByDepartment({
                    master_tree: USER_ID
                }).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                getData(urlChurch).then(res => {
                    let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
            }
            init = true;
        }
    }

    function ChurchPastorReportsTable(config={}) {
        getChurchPastorReports(config).then(data => {
            makeChurchPastorReportsTable(data);
            (!initResponsible) && makeResponsibleList(data);
        });
    }

    function makeResponsibleList(data) {
        let responsibles = data.results.map(res => res.master),
            uniqResponsibles = _.without(_.uniqWith(responsibles, _.isEqual), null);
        const options = uniqResponsibles.map(option => `<option value="${option.id}">${option.fullname}</option>`);
        $responsibleFilter.append(options);
        initResponsible = true;
    }

    // (PATH == undefined) && ChurchPastorReportsTable();
    ChurchPastorReportsTable();

    // Events
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });

     $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        churchPastorReportsTable();
    }, 500));

    $('.selectdb').select2();

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(ChurchPastorReportsTable, 'report_summary');
    });

    //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, churchPastorReportsTable);
    });

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {};
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department_id = departamentID;
        }
        getPastorsByDepartment(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $treeFilter.html('<option>ВСЕ</option>').append(pastors);
        });

        getData(urlChurch, config).then(res => {
            let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
            $churchFilter.html('<option>ВСЕ</option>').append(churches);
        });
    });

    $treeFilter.on('change', function () {
        let config = {};
        if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
            config.master_tree = $(this).val();
        }
        getData(urlChurch, config).then(res => {
            let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
            $churchFilter.html('<option>ВСЕ</option>').append(churches);
        });
    });

    //Parsing URL
    if (PATH != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

});
