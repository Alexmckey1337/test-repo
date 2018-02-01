'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls/index';
import {showAlert} from "./modules/ShowNotifications/index";
import updateSettings from './modules/UpdateSettings/index';
import makeSelect from './modules/MakeAjaxSelect/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {BdAccessTable, bdAccessTable} from "./modules/Controls/bg_access_list";
import parseUrlQuery from './modules/ParseUrl/index';
import {postData} from './modules/Ajax/index';

$('document').ready(function () {
    let configData = {},
        init = false,
        reg = '/(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9!@#$%^&*a-zA-Z]{6,}/g'
    const path = window.location.href.split('?')[1];

    $('.selectbd').select2();

    function filterInit(set = null) {
        if (!init) {
            if (set != null) {
                initFilterAfterParse(set);
            }
            init = true;
        }
    }
    function initFilterAfterParse(set) {
        for (let [key, value] of Object.entries(set)) {
            $('#filterPopup').find(`input[data-filter="${key}"]`).val(value);
            $('#filterPopup').find(`select[data-filter="${key}"]`).val(value).trigger('change');
        }
        $('.apply-filter').trigger('click');
    }

    if (path == undefined) {
        BdAccessTable(configData);
    }
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

    // Events
    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        bdAccessTable();
    }, 500));
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });
    $('.apply-filter').on('click', function () {
        applyFilter(this, bdAccessTable);
    });
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(bdAccessTable);
    });
    $('#passwordForm').on('input','input[name="confirmPassword"]',function () {
       let newPass = $(this).closest('form').find('input[name="newPassword"]').val(),
           confirmPass = $(this).val();
       if(newPass === confirmPass){
            console.log(confirmPass);
        }
    });
    $('#passwordForm').on('submit', function (e) {
        e.preventDefault();
        let newPass = $(this).find('input[name="newPassword"]').val(),
            confirmPass = $(this).find('input[name="confirmPassword"]').val(),
            userId = $('#passwordForm').data('id'),
            data = {
                'password': confirmPass
            };
        if (newPass === confirmPass) {
            postData(URLS.controls.password_submit(userId), data, {method:"PATCH"});
        }
    });
});
