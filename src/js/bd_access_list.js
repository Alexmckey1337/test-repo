'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import {showAlert} from "./modules/ShowNotifications/index";
import updateSettings from './modules/UpdateSettings/index';
import makeSelect from './modules/MakeAjaxSelect/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {BdAccessTable, bdAccessTable} from "./modules/Controls/bg_access_list";
import parseUrlQuery from './modules/ParseUrl/index';

$('document').ready(function () {
    let configData = {},
        init = false;
    const path = window.location.href.split('?')[1];

    $('.selectdb').select2();
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
        bdAccessTable();
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
});
