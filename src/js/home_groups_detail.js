'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import {createHomeGroupUsersTable, makeUsersFromDatabaseList, editHomeGroups,
        reRenderTable} from "./modules/HomeGroup/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import accordionInfo from './modules/accordionInfo';
import {getPotentialLeadersForHG} from "./modules/GetList/index";
import pasteLink from './modules/pasteLink';

$('document').ready(function () {
    let $createUserForm = $('#createUser'),
        $homeGroup = $('#home_group');
    const ID = $homeGroup.data('id');
    const HG_ID = $homeGroup.data('departament_id');
    const CH_ID = $homeGroup.data('church-id');
    const HG_TITLE = $homeGroup.data('departament_title');

    createHomeGroupUsersTable({}, ID);

// Events
    $('#add_userToHomeGroup').on('click', function () {
        // $('#addUser').css('display', 'block');
        initAddNewUser({getDepartments: false});
        $('#searchedUsers').html('');
        $('#searchUserFromDatabase').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        document.querySelector('#searchUserFromDatabase').focus();
        $('#searchedUsers').css('height', 'auto');
        $('#chooseUserINBases').css('display', 'block');
    });

    // $('#choose').on('click', function () {
    //     $(this).closest('.popup').css('display', 'none');
    //     $('#searchedUsers').html('');
    //     $('#searchUserFromDatabase').val('');
    //     $('.choose-user-wrap .splash-screen').removeClass('active');
    //     $('#chooseUserINBases').css('display', 'block');
    // });

    $('#addNewUser').on('click', function () {
        let departament_id = $('#home_group').data('departament_id');
        let departament_title = $('#home_group').data('departament_title');
        let option = document.createElement('option');
        $(option).val(departament_id).text(departament_title).attr('selected', true);
        $(this).closest('.popup').css('display', 'none');
        $('#addNewUserPopup').css('display', 'block');
        $('#chooseDepartment').html(option).attr('required', false).attr('disabled', false);
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
    });
    $('#searchUserFromDatabase').on('keyup', _.debounce(function () {
        let search = $(this).val();
        if (search.length > 2) makeUsersFromDatabaseList();
    }, 500));

    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        createHomeGroupUsersTable();
    }, 500));

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupUsersTable);
    });

    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'none');
        exportTableData(this)
            .then(function () {
                $('.preloader').css('display', 'none');
            })
            .catch(function () {
                showAlert('Ошибка при загрузке файла');
                $('.preloader').css('display', 'none');
            });
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
                createNewUser(reRenderTable).then(function() {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        }
    });

    accordionInfo();

    $('#opening_date').datepicker({
        dateFormat: 'dd.mm.yyyy',
        autoClose: true
    });

    $('.accordion').find('.edit').on('click', function (e) {
        e.preventDefault();
        let $input = $(this).closest('form').find('input:not(.select2-search__field), select');

        if ($(this).hasClass('active')) {
            $input.each(function (i, el) {
                if (!$(this).attr('disabled')) {
                    $(this).attr('disabled', true);
                }
                $(this).attr('readonly', true);
                if ($(el).is('select')) {
                    if (!$(this).is('.no_select')) {
                        $(this).select2('destroy');
                    }
                }
            });
            $(this).removeClass('active');
        } else {
            let leaderId = $('#homeGroupLeader').val(),
                churchId = $('#editHomeGroupForm').attr('data-departament_id');

             getPotentialLeadersForHG({church: churchId}).then(function (res) {
                    return res.map(function (leader) {
                        return `<option value="${leader.id}" ${(leaderId == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`;
                    });
                }).then(function (data) {
                    $('#homeGroupLeader').html(data).prop('disabled', false).select2();
                });
            $input.each(function (i, el) {
                if (!$(this).hasClass('no__edit')) {
                    if ($(this).attr('disabled')) {
                        $(this).attr('disabled', false);
                    }
                    if (!$(el).is('#church')) {
                        $(this).attr('readonly', false);
                    }
                }
            });
            $(this).addClass('active');
        }
    });

    $('.accordion').find('.save__info').on('click', function (e) {
        e.preventDefault();
        let idHomeGroup = $(this).closest('form').attr('data-id');
        editHomeGroups($(this), idHomeGroup);
        let liderLink = '/account/' + $('#homeGroupLeader').val();
        pasteLink($('#homeGroupLeader'), liderLink);
        let webLink = $(this).closest('form').find('#web_site').val();
        let linkIcon = $('#site-link');
        if (webLink == '' ) {
            !linkIcon.hasClass('link-hide') && linkIcon.addClass('link-hide');
        } else {
            pasteLink($('#web_site'), webLink);
            linkIcon.hasClass('link-hide') && linkIcon.removeClass('link-hide');
        }
    });

});
