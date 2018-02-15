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
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {BdAccessTable, bdAccessTable} from "./modules/Controls/bg_access_list";
import parseUrlQuery from './modules/ParseUrl/index';
import {postData} from './modules/Ajax/index';

$('document').ready(function () {
    let configData = {},
        init = false,
        reg = /(?=.*\d)((?=.*[a-z])|(?=.*[A-Z])).{8,20}/g;
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
    $('#passwordForm').on('input', 'input', function () {
        let newPass = $(this).closest('form').find('input[name="newPassword"]').val(),
            confirmPass = $(this).val();
        if ($(this).attr('name') === 'confirmPassword') {
            $('#passwordForm').find('.errorTxt').addClass('error').removeClass('green').find('span').text('').text('Пароли не совпадают');
            if (newPass === confirmPass && newPass !='') {
                $('#passwordForm').find('.errorTxt').removeClass('error').addClass('green').find('span').text('').text('Пароли совпадают');
            }
        } else if ($(this).attr('name') === 'newPassword') {
            let result = String(newPass).search(reg);
            if(result === -1 && $(this).val() != ''){
                $('#passwordForm').find('.errorTxt').removeClass('green').addClass('error').addClass('novalid').find('span').text('').text('Пароль не валидный');
            }else {
                $('#passwordForm').find('.errorTxt').removeClass('green').removeClass('error').removeClass('novalid').find('span').text('');
            }
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
        if (newPass === confirmPass && !$('.errorTxt').hasClass('novalid') && newPass != '') {
            postData(URLS.controls.password_submit(userId), data, {method: "PUT"}).then(function () {
                $('#newPassword').css({
                    'display': 'none'
                });
                bdAccessTable();
                showAlert('Пароль успешно изменен');
            }).catch(function (err) {
                console.log(err);
            })
        }else if($('.errorTxt').hasClass('novalid')){
            $('.errorTxt').removeClass('green').addClass('error').find('span').text('').text('Пароль не валидный');
        }else if(newPass === '' || confirmPass === ''){
            $('.errorTxt').removeClass('green').addClass('error').find('span').text('').text('Заполните все поля');
        }
    });

    if (path != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }
});
