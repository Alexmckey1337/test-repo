'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import parseUrlQuery from './modules/ParseUrl/index';
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {createUsersTable} from "./modules/Users/index";
import {createNewUser, saveUser, initAddNewUser} from "./modules/User/addUser";
import {getChurchesListINDepartament, getShortUsers, getResponsible, getPastorsByDepartment} from "./modules/GetList/index";

$('document').ready(function () {
    let $departmentsFilter = $('#departments_filter'),
        $churchFilter = $('#church_filter'),
        $treeFilter = $("#tree_filter"),
        path = window.location.href.split('?')[1];

    (path == undefined) && createUsersTable({});

    $('.selectdb').select2();
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        selectOtherYears: false,
        showOtherYears: false,
        moveToOtherYearsOnSelect: false,
        minDate: new Date((new Date().getFullYear()), 0, 1),
        maxDate: new Date((new Date().getFullYear()), 11, 31),
        position: "left top",
        autoClose: true
    });

    $('.select_rep_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });

    //Events
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });

    $('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });

    $('.editprofile').on('click', function (e) {
        e.stopPropagation();
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createUsersTable({});
    }, 500));

    $('#sort_save').on('click', function () {
        updateSettings(createUsersTable);
    });

    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        exportTableData(this);
    });

    $('#quickEditCartPopup').find('.close').on('click', function () {
        let $input = $(this).closest('.pop_cont').find('input');
        let $select = $(this).closest('.pop_cont').find('select');
        let $button = $(this).closest('.pop_cont').find('.save-user');
        let $info = $(this).closest('.pop_cont').find('.info');
        $button.css('display', 'inline-block');
        $button.removeAttr('disabled');
        $button.text('Сохранить');
        $info.each(function () {
            $(this).css('display', 'none');
        });
        $input.each(function () {
            $(this).removeAttr('readonly');
        });
        $select.each(function () {
            $(this).removeAttr('disabled');
        });
    });

    $('#add').on('click', function () {
        $('body').addClass('no_scroll');
        $('#addNewUserPopup').css('display', 'block');
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
        initAddNewUser();
    });

    $.validate({
        lang: 'ru',
        form: '#createUser',
        onError: function (form) {
            showAlert(`Введены некорректные данные`);
            let top = $(form).find('div.has-error').first().offset().top;
            $(form).find('.body').animate({scrollTop: top}, 500);
        },
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(null).then(function () {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        },
    });

    //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createUsersTable)
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
        getChurchesListINDepartament(departamentID).then(data => {
            const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
            $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
        });
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
            $('#tree_filter').html(options);
        }).then(function () {
                if ($('#tree_filter').val() == "ВСЕ") {
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
                        $('#masters_filter').html(options);
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
                        $('#masters_filter').html(options);
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
            $('#masters_filter').html(options);
        });
    });

    $('.save-user').on('click', function () {
        saveUser(this);
    });

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        $('#church_filter').find(`option[value='${filterParam.church_id}']`).prop('selected', true).trigger('change');
        $('#partner_filter').find(`option[value='${filterParam.is_partner}']`).prop('selected', true).trigger('change');
        $('.apply-filter').trigger('click');
    }

});