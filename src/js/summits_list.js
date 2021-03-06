'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import updateSettings from './modules/UpdateSettings/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {SummitListTable, summitListTable, submitSummit, removeValidText} from "./modules/Controls/summits_list";
import parseUrlQuery from './modules/ParseUrl/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {btnSummitControlls} from "./modules/Controls/summits_list";
import {refreshAddSummitFields} from "./modules/Controls/summits_list";

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
        SummitListTable(configData);
    }

    // Events
    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        summitListTable();
    }, 500));

    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, summitListTable);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(summitListTable);
    });

    $('#add').on('click',function () {
        $('#addSammit').addClass('active').addClass('add').removeClass('change');
        $('.bg').addClass('active');
        refreshAddSummitFields();
        $('#addSammit').find('.popup_text').find('h2').text('Добавить саммит');
        removeValidText($('#addSammit'));
    });

    $('.summit-date').datepicker({
        dateFormat: 'dd.mm.yyyy',
        autoClose: true,
        position: "bottom center",
    });

    $('.start_date').datepicker({
        onSelect: function (formattedDate, date) {
            $('.end_date').datepicker({
                minDate: new Date(date),
            });
        }
    });

    $.validate({
        lang: 'ru',
        form: '#addSammitForm',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            submitSummit();
            return false;
        }
    });

    if (path != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

    btnSummitControlls();
});