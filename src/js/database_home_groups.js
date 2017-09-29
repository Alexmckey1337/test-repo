'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import {getHGLeaders} from "./modules/GetList/index";
import {updateLeaderSelect} from "./modules/GetList/index";
import {addHomeGroup, saveHomeGroups, clearAddHomeGroupData, createHomeGroupsTable} from "./modules/HomeGroup/index";
import {makePastorList} from "./modules/MakeList/index";
import updateSettings from './modules/UpdateSettings/index';
import {showAlert} from "./modules/ShowNotifications/index";
import exportTableData from './modules/Export/index';
import {getChurchesListINDepartament} from './modules/GetList/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";

$('document').ready(function () {
    let filterInit = (function () {
        let init = false;
        return function () {
            if (!init) {
                getHGLeaders().then(res => {
                    const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $('#tree_filter').html('<option value="">ВСЕ</option>').append(leaders);
                    $('#leader_filter').html('<option value="">ВСЕ</option>').append(leaders);
                });
                init = true;
            }
        }
    })();

    let $departmentSelect = $('#department_select');
    const $churchSelect = $('#added_home_group_church_select');
    createHomeGroupsTable();
    let $departmentsFilter = $('#departments_filter'),
        $churchFilter = $('#church_filter'),
        $treeFilter = $('#tree_filter');
    $departmentSelect.select2();
    $('#pastor_select').select2();
    $('.selectdb').select2();
    $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    // Events
    $('#add').on('click', function () {
        clearAddHomeGroupData();
        updateLeaderSelect();
        setTimeout(function () {
            $('#addHomeGroup').css('display', 'block');
        }, 100);
    });

    if ($churchSelect) {
        $churchSelect.on('change', function () {
            updateLeaderSelect();
        });
    }

    $departmentSelect.on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupsTable);
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createHomeGroupsTable();
    }, 500));

    $('#export_table').on('click', function () {
        exportTableData(this);
    });

    //Filter
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createHomeGroupsTable);
    });

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        if (departamentID != '') {
            getChurchesListINDepartament(departamentID).then(data => {
                const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
            });
        }
    });
    $churchFilter.on('change', function () {
        let churchID = $(this).val();
        let config = {};
        if (churchID) {
            config.church = churchID;
        }
        getHGLeaders(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#tree_filter').html('<option value="">ВСЕ</option>').append(pastors);
            $('#leader_filter').html('<option value="">ВСЕ</option>').append(pastors);
        })
    });
    $treeFilter.on('change', function () {
        let masterTreeID = $(this).val();
        let config = {};
        if (masterTreeID) {
            config = {
                master_tree: masterTreeID
            }
        }
        getHGLeaders(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#leader_filter').html('<option value="">ВСЕ</option>').append(pastors);
        });
    });
    $('#added_home_group_church_select').select2();

    $('.save-group').on('click', function () {
        saveHomeGroups(this, createHomeGroupsTable);
    });

    $('#addHomeGroup').find('form').on('submit', function (event) {
        addHomeGroup(event, this, createHomeGroupsTable);
    })

});