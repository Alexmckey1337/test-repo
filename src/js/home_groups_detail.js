'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls/index';
import errorHandling from './modules/Error';
import {
    createHomeGroupUsersTable,
    makeUsersFromDatabaseList,
    reRenderTable,
    updateHomeGroup
} from "./modules/HomeGroup/index";
import {
    HomeReportsTable,
    sendReport,
    btnControlsImg,
    deleteReport
} from "./modules/Reports/home_group";
import updateSettings from './modules/UpdateSettings/index';
import {postData} from "./modules/Ajax/index";
import exportTableData from './modules/Export/index';
import {dataURLtoBlob} from './modules/Avatar/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import accordionInfo from './modules/accordionInfo';
import {getPotentialLeadersForHG, updateHGLeaderSelect} from "./modules/GetList/index";
import {getHGChurches} from "./modules/GetList/index";
import pasteLink from './modules/pasteLink';
import {btnLocationControls} from "./modules/Map/index";

$('document').ready(function () {
    let $homeGroup = $('#home_group');
    const ID = $homeGroup.data('id');
    let configReport = {
        home_group: ID,
        last_5: true
    },
        $statusTabs = $('#statusTabs');

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

    $('.create_report').on('click',function () {
        $('#addHomeGroupReport').addClass('active');
        $('.bg').addClass('active');
        $('#addHomeGroupReport').find('#dateReport').val('');
    });

    $('.add-report').on('click',function (e) {
        e.preventDefault();
        let type_id = $(this).parent().closest('form').find('#typeReport').val(),
            date = $(this).parent().closest('form').find('#dateReport').val().trim().split('.').reverse().join('-'),
            data = {
                type_id,
                date
            },
            ID = $('#editHomeGroupForm').data('id');
        postData(URLS.home_group.create_report(ID),data).then(function () {
            HomeReportsTable(configReport, false);
            $('#addHomeGroupReport').removeClass('active');
            $('.bg').removeClass('active');
            showAlert('Отчет успешно создан');
        }).catch(err => errorHandling(err));
    });

    $('#typeReport').select2();
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

    $('#opening_date,#dateReport').datepicker({
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
        if ($(this).data('edit-block') == 'editChurch' && $(this).hasClass('active')) {
            $(this).closest('form').get(0).reset();
            $('homeGroupChurch').attr('disabled', true);
        }
        if ($(this).hasClass('active')) {
            $('.left-contentwrap').find('.search_city_link').css('visibility', 'hidden');
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
            $('#address_show').removeClass('address_isHide');
            $('#address_choose').addClass('address_isHide');
        } else {
            if (noEdit) {
                showAlert("Сначала сохраните или отмените изменения в другом блоке");
            } else {
                $('.left-contentwrap').find('.search_city_link').css('visibility', '');
                let leaderId = $('#homeGroupLeader').val(),
                    churchId = $('#homeGroupChurch').attr('data-id') || null;
                $input.each(function () {
                    if (!$(this).hasClass('no__edit')) {
                        if ($(this).attr('disabled')) {
                            $(this).attr('disabled', false);
                        }
                        $(this).attr('readonly', false);
                        if ($(this).is('select') && $(this).is(':not(.no_select)')) {
                            $(this).select2();
                        }
                        if ($(this).is('#homeGroupChurch')) {
                            getHGChurches().then(function (res) {
                                return res.map(function (church) {
                                    return `<option value="${church.id}" ${(churchId == church.id) ? 'selected' : ''}> ${church.title} </option>`;
                                });
                            }).then(function (data) {
                                $('#homeGroupChurch').html(data).prop('disabled', false).select2();
                            });
                        }
                        if ($(this).is('#homeGroupLeader')) {
                            getPotentialLeadersForHG({church: churchId}).then(function (res) {
                                return res.map(function (leader) {
                                    return `<option value="${leader.id}" ${(leaderId == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`;                                });
                            }).then(function (data) {
                                $('#homeGroupLeader').html(data).prop('disabled', false).select2();
                            });
                        }
                    }
                });
                $(this).addClass('active');
            }
            $('#address_choose').removeClass('address_isHide');
            $('#address_show').addClass('address_isHide');
        }
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
            if (formName === 'editAddress') {
                let id = $('#editAddressForm').find('.select_small').attr('data-id'),
                    title = $('#adress').attr('data-title'),
                    lat = $('#adress').attr('data-lat'),
                    lng = $('#adress').attr('data-lng');
                id && formData.append('locality', id);
                if (lat && lng && lat != 'None' && lng != 'None') {
                    formData.append('address', title);
                    formData.append('latitude', lat);
                    formData.append('longitude', lng);
                }
            }
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

        pasteLink($('#homeGroupLeader'), liderLink);
        if (webLink == '' ) {
            !linkIcon.hasClass('link-hide') && linkIcon.addClass('link-hide');
        } else {
            pasteLink($('#web_site'), webLink);
            linkIcon.hasClass('link-hide') && linkIcon.removeClass('link-hide');
        }
        $('.left-contentwrap').find('.search_city_link').css('visibility', 'hidden');
        $('#address_show').removeClass('address_isHide');
        $('#address_choose').addClass('address_isHide');
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

    $.validate({
        lang: 'ru',
        form: '#homeReportForm',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            sendReport(false, configReport);

            return false;
        }
    });

    $('.close-map').on('click', function () {
        if(!$(this).hasClass('active')){
            $(".a-map").removeClass('active');
        }
    });

    btnControlsImg();
    HomeReportsTable(configReport, false);

    $statusTabs.find('button').on('click', function () {
        $('.preloader').css('display', 'block');
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
        HomeReportsTable(configReport, false);
    });

    $('#delete_report').on('click', function (e) {
        e.preventDefault();
        deleteReport(HomeReportsTable, configReport, false);
    });

    btnLocationControls();

});

// Event to change option in HomeGroupChurch (update potential leaders)
$('#homeGroupChurch').change(function () {
    updateHGLeaderSelect();
});