'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import URLS from './modules/Urls/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {getResponsible, getShortUsers, getPastorsByDepartment} from "./modules/GetList/index";
import {getPartners} from "./modules/Partner/index";

$(document).ready(function () {
    let $departmentsFilter = $('#department_filter');
    let $treeFilter = $("#master_tree_filter");

    $('#export_table').on('click', function () {
        let type = $('#statusTabs').find('.current button').attr('data-type'),
            url = (type === 'people') ? URLS.export.partners() : URLS.export.church_partners();
        exportTableData(this, {}, 'search_fio', url);
    });

    $('#accountable').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        getPartners({page: 1});
    }, 500));

    getPartners();

    $('#sort_save').on('click', function () {
        let type = $('#statusTabs').find('.current button').attr('data-type'),
            option = (type === 'people') ? 'partner' : 'church_partner';
        $('.preloader').css('display', 'block');
        updateSettings(getPartners, option);
    });

    $('#filter_button').on('click', function () {
         $('#filterPopup').addClass('active');
         $('.bg').addClass('active');
    });

    //Filter
    $('.apply-filter').on('click', function () {
        applyFilter(this, getPartners);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {
            level_gte: 2
        };
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
        }
        getShortUsers(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ');
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#master_tree_filter').html(options);
        }).then(function () {
            if ($('#master_tree_filter').val() == "ВСЕ") {
                getResponsible(departamentID, 2).then(function (data) {
                    let options = [];
                    let option = document.createElement('option');
                    $(option).text('ВСЕ');
                    options.push(option);
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        options.push(option);
                    });
                    $('#responsible_filter').html(options);
                });
            } else {
                getPastorsByDepartment(departamentID).then(function (data) {
                    let options = [];
                    let option = document.createElement('option');
                    $(option).text('ВСЕ');
                    options.push(option);
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        options.push(option);
                    });
                    $('#responsible_filter').html(options);
                });
            }
        });
    });

    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config = {
                master_tree: $(this).val()
            };
        }
        getShortUsers(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ');
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#responsible_filter').html(options);
        });
    });

    $('.selectdb').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        selectOtherYears: false,
        showOtherYears: false,
        moveToOtherYearsOnSelect: false,
        minDate: new Date((new Date().getFullYear()), 0, 1),
        maxDate: new Date((new Date().getFullYear()), 11, 31),
        autoClose: true,
        position: "left top",
    });

    $('.select_rep_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });

    //Tabs
    $('#statusTabs').on('click', 'button', function () {
        $('#statusTabs').find('li').each(function () {
            $(this).removeClass('current');
        });
        $(this).parent().addClass('current');
        $('.preloader').css('display', 'block');
        getPartners();
    });

});