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
import {PhoneTable, phoneTable,getDataUserPhone} from "./modules/Phone/index";
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
        PhoneTable(configData);
    }
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

    // Events
    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        phoneTable();
    }, 500));
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });
    $('.apply-filter').on('click', function () {
        applyFilter(this, phoneTable);
    });
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(phoneTable);
    });
    $('#add-phone').on('click',function () {
        $('#searchPhone').val('');
        getDataUserPhone();
        $('#popupAddUserToPhone').css('display', 'block');
    });
    $('.close_pop').on('click',function () {
        $('#popupAddUserToPhone').css('display', 'none');
    })
    $('.date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#searchPhone').keypress(function (event) {
        if (event.which === 13) {
            let value = $(this).val(),
                config = {search: value};
            getDataUserPhone(config);
        }
    });
});
