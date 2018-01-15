'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import {createHomeGroupUsersTable, makeUsersFromDatabaseList, editHomeGroups,
        reRenderTable,updateHomeGroup} from "./modules/HomeGroup/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {dataURLtoBlob} from './modules/Avatar/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import accordionInfo from './modules/accordionInfo';
import {getPotentialLeadersForHG} from "./modules/GetList/index";
import pasteLink from './modules/pasteLink';

$('document').ready(function () {
    let $homeGroup = $('#home_group');
    const ID = $homeGroup.data('id');

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

    $('#addNewUser').on('click', function () {
        let departament_id = $('#home_group').data('departament_id');
        let departament_title = $('#home_group').data('departament_title');
        let option = document.createElement('option');
        $(option).val(departament_id).text(departament_title).attr('selected', true);
        $(this).closest('.popup').css('display', 'none');
        //$('#addNewUserPopup').css('display', 'block');
        $('#addNewUserPopup').addClass('active');
        $('.bg').addClass('active');
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
        updateSettings(createHomeGroupUsersTable, 'group_user');
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
                createNewUser(reRenderTable);
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
        let $edit = $('.edit'),
            exists = $edit.closest('form').find('ul').hasClass('exists'),
            noEdit = false,
            action = $(this).closest('form').data('action'),
            inputWrap = $(this).closest('form').find('.input-wrap'),
            $block = $('#' + $(this).data('edit-block')),
            $input = $block.find('input:not(.select2-search__field), select'),
            $hiddenBlock = $(this).parent().find('.hidden');
        $hiddenBlock.each(function () {
            $(this).removeClass('hidden');
        });
        $edit.each(function () {
            if ($(this).hasClass('active')) {
                noEdit = true;
            }
        });

        if ($(this).data('edit-block') == 'editContact' && $(this).hasClass('active')) {
            $(this).closest('form').get(0).reset();
        }
        if ($(this).hasClass('active')) {
            $input.each(function (i, el) {
                if (!$(this).attr('disabled')) {
                    $(this).attr('disabled', true);
                }
                $(this).attr('readonly', true);
                if ($(el).is('select')) {
                    if ($(this).is(':not([multiple])')) {
                        if (!$(this).is('.no_select')) {
                            $(this).select2('destroy');
                        }
                    }
                }
            });
            $(this).removeClass('active');
        } else {
            if (noEdit) {
                showAlert("Сначала сохраните или отмените изменения в другом блоке");
            } else {
                let leaderId = $('#homeGroupLeader').val(),
                    churchId = $('#editHomeGroupForm').attr('data-departament_id');
                $input.each(function () {
                    if (!$(this).hasClass('no__edit')) {
                        if ($(this).attr('disabled')) {
                            $(this).attr('disabled', false);
                        }
                        $(this).attr('readonly', false);
                        if ($(this).is('select') && $(this).is(':not(.no_select)')) {
                            $(this).select2();
                        }
                        if ($(this).is('#church')) {
                            $(this).attr('readonly', true);
                        }else{
                            $(this).attr('readonly', false);
                        }
                        if ($(this).is('#homeGroupLeader')) {
                            getPotentialLeadersForHG({church: churchId}).then(function (res) {
                                return res.map(function (leader) {
                                    return `<option value="${leader.id}" ${(leaderId == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`;
                                });
                            }).then(function (data) {
                                $('#homeGroupLeader').html(data).prop('disabled', false).select2();
                            });
                        }
                    }
                });
                $(this).addClass('active');
            }
        }

        // if ($(this).hasClass('active')) {
        //     $input.each(function (i, el) {
        //         if (!$(this).attr('disabled')) {
        //             $(this).attr('disabled', true);
        //         }
        //         $(this).attr('readonly', true);
        //         if ($(el).is('select')) {
        //             if (!$(this).is('.no_select')) {
        //                 $(this).select2('destroy');
        //             }
        //         }
        //     });
        //     $(this).removeClass('active');
        // } else {
        //     let leaderId = $('#homeGroupLeader').val(),
        //         churchId = $('#editHomeGroupForm').attr('data-departament_id');
        //     $input.each(function (i, el) {
        //         console.log($(this).is('#homeGroupLeader'));
        //         if (!$(this).hasClass('no__edit')) {
        //             if ($(this).attr('disabled')) {
        //                 $(this).attr('disabled', false);
        //             }
        //             if (!$(el).is('#church')) {
        //                 $(this).attr('readonly', false);
        //             }
        //             if ($(el).is('#homeGroupLeader')) {
        //                 getPotentialLeadersForHG({church: churchId}).then(function (res) {
        //                     return res.map(function (leader) {
        //                         return `<option value="${leader.id}" ${(leaderId == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`;
        //                     });
        //                 }).then(function (data) {
        //                     $('#homeGroupLeader').html(data).prop('disabled', false).select2();
        //                 });
        //             }
        //         }
        //     });
        //     $(this).addClass('active');
        // }
        //  $('#first_name,#file').attr('disabled',false);
        // $('#first_name,#file').attr('readonly',false);
    });

    $('.accordion').find('.save__info').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').find('.edit').removeClass('active');
        let idHomeGroup = $('.accordion').attr('data-id'),
            _self = this,
            idChurch = $('.accordion').attr('data-id'),
            $block = $(this).closest('.right-info__block'),
            $input = $block.find('input:not(.select2-search__field), select'),
            thisForm = $(this).closest('form'),
            success = $(this).closest('.right-info__block').find('.success__block'),
            formName = thisForm.attr('name'),
            partner = thisForm.data('partner'),
            action = thisForm.data('action'),
            form = document.forms[formName],
            formData = new FormData(form),
            hidden = $(this).hasClass('after__hidden'),
            linkIcon = $('#site-link'),
            webLink = $(this).closest('form').find('#web_site').val(),
            liderLink = '/account/' + $('#homeGroupLeader').val();

        if (action === 'update-user') {
            $input.each(function () {
                let id = $(this).data('id');
                console.log('ID-->', id);
                if (!$(this).attr('name')) {
                    if ($(this).is('[type=file]')) {
                        let send_image = $(this).prop("files").length || false;
                        if (send_image) {
                            try {
                                let blob;
                                blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                                formData.append('image', blob, 'logo.jpg');
                                formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
                                formData.append('id', id);

                            } catch (err) {
                                console.log(err);
                            }
                        }
                        return;
                    }
                    let id = $(this).attr('id');
                    let $val = $('#' + id);
                    if ($val.val() instanceof Array) {
                        formData.append(id, JSON.stringify($('#' + id).val()));
                    } else {
                        if ($val.val()) {
                            if ($val.is('#opening_date')) {
                                formData.append(id, $('#' + id).val().trim().split('.').reverse().join('-'));
                            }else if($val.is('#church')){
                                formData.append(id, $('#' + id).data('id'));
                            } else  {
                                formData.append(id, JSON.stringify($('#' + id).val().trim().split(',').map((item) => item.trim())));
                            }
                        } else {
                            if ($val.hasClass('sel__date')) {
                                formData.append(id, '');
                            } else {
                                formData.append(id, JSON.stringify([]));
                            }
                        }
                    }
                }
            });
            updateHomeGroup(idChurch, formData, success)
                .then(function (data) {
                    if (hidden) {
                        let editBtn = $(_self).closest('.hidden').data('edit');
                        setTimeout(function () {
                            $('#' + editBtn).trigger('click');
                        }, 1500);
                    }
                    $('#fullName').text(data.title);
                })
        }
        $input.each(function () {
            if (!$(this).attr('disabled')) {
                $(this).attr('disabled', true);
            }
            $(this).attr('readonly', true);
            if ($(this).is('select')) {
                if ($(this).is(':not([multiple])')) {
                    if (!$(this).is('.no_select')) {
                        $(this).select2('destroy');
                    }
                }
            }
        });
        // updateHomeGroup(idHomeGroup, formData, success);
        // editHomeGroups($(this), idHomeGroup);


        pasteLink($('#homeGroupLeader'), liderLink);
        if (webLink == '' ) {
            !linkIcon.hasClass('link-hide') && linkIcon.addClass('link-hide');
        } else {
            pasteLink($('#web_site'), webLink);
            linkIcon.hasClass('link-hide') && linkIcon.removeClass('link-hide');
        }
    });

    $('#editNameBtn').on('click', function () {
        if ($(this).hasClass('active')) {
            $('#editNameBlock').css({
                display: 'block',
            });
        } else {
            $('#editNameBlock').css({
                display: 'none',
            });
        }
    });
});
