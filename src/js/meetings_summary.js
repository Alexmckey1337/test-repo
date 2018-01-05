'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import URLS from './modules/Urls/index';
import getData from './modules/Ajax/index';
import updateSettings from './modules/UpdateSettings/index';
import {getPastorsByDepartment, getHomeLiderReports} from "./modules/GetList/index";
import parseUrlQuery from './modules/ParseUrl/index';
import {makeHomeLiderReportsTable, homeLiderReportsTable} from "./modules/Reports/meetings_summary";
import {applyFilter, refreshFilter} from "./modules/Filter/index";

$('document').ready(function () {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#master_tree_filter'),
        $churchFilter = $('#church_filter'),
        $responsibleFilter = $('#responsible_filter'),
        initResponsible = false,
        urlChurch = URLS.church.for_select(),
        init = false;
    const USER_ID = $('body').data('user'),
          PATH = window.location.href.split('?')[1];

    function filterInit(set = null) {
        if (!init) {
            console.log(set);
            if (set != null) {
                $('#departments_filter').find(`option[value='${set.department_id}']`).prop('selected', true);
                let departamentID = $('#departments_filter').val(),
                    config = {},
                    config2 = {};
                if (departamentID) {
                    config.department = departamentID;
                    config2.department_id = departamentID;
                }
                getPastorsByDepartment(config2).then(data => {
                    const pastors = data.map(pastor => `<option value="${pastor.id}" ${(set.master_id == pastor.id) ? 'selected' : ''}>${pastor.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(pastors);
                    return false;
                }).then(() => {
                    (set.master_id) && (config.master_tree = set.master_id);
                    return getData(urlChurch, config).then(res => {
                        let churches = res.results.map(church => `<option value="${church.id}" ${(set.church_id == church.id) ? 'selected' : ''}>${church.get_title}</option>`);
                        $churchFilter.html('<option>ВСЕ</option>').append(churches);
                    });
                }).then(() => {
                    return getHomeLiderReports().then(data => {
                        let responsibles = data.results.map(res => res.master),
                            uniqResponsibles = _.uniqWith(responsibles, _.isEqual);
                        const options = uniqResponsibles.map(option => {
                            if (option) {
                                return `<option value="${option.id}" ${(set.responsible_id == option.id) ? 'selected' : ''}>${option.fullname}</option>`
                            }
                        });
                        $responsibleFilter.append(options);
                        $('.apply-filter').trigger('click');
                    });
                });
            } else {
                getPastorsByDepartment({master_tree: USER_ID}).then(res => {
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

    (PATH == undefined) && HomeLiderReportsTable();

    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });

    $('.selectdb').select2();

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(HomeLiderReportsTable, 'meeting_summary');
    });

    function HomeLiderReportsTable() {
        getHomeLiderReports().then(data => {
            makeHomeLiderReportsTable(data);
            if (!initResponsible) {
                let responsibles = data.results.map(res => res.master),
                    uniqResponsibles = _.uniqWith(responsibles, _.isEqual);
                const options = uniqResponsibles.map(option => {
                    if (option != null) {
                        return `<option value="${option.id}">${option.fullname}</option>`
                    }
                });
                $responsibleFilter.append(options);
                initResponsible = true;
            }
        });
    }

    $('input[name="fullsearch"]').on('keyup', _.debounce(function () {
        $('.preloader').css('display', 'block');
        homeLiderReportsTable();
    }, 500));

        //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, homeLiderReportsTable);
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
