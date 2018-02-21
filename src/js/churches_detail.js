'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls/index';
import {postData, postFormData} from "./modules/Ajax/index";
import errorHandling from './modules/Error';
import {
    createChurchesDetailsTable,
    setOptionsToPotentialLeadersSelect,
    makeUsersFromDatabaseList,
    reRenderTable,
    updateChurch,
} from "./modules/Church/index";
import {
    ChurchReportsTable,
    sendReport,
    deleteReport,
    calcTransPayments,
} from './modules/Reports/church';
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import {dataURLtoBlob} from './modules/Avatar/index';
import {makePastorList, makeDepartmentList} from "./modules/MakeList/index";
import pasteLink from './modules/pasteLink';
import {addHomeGroup, clearAddHomeGroupData} from "./modules/HomeGroup/index";
import reverseDate from './modules/Date/index';
import {convertNum} from "./modules/ConvertNum/index";
import {btnLocationControls} from "./modules/Map/index";

import {
    btnNeed,
    btnPartners,
    btnDeal,
    tabs,
    renderDealTable,
    renderPaymentTable,
} from "./modules/Partnerships/index";

$('document').ready(function () {
    const CHURCH_ID = $('#church').data('id');
    const D_ID = $('#added_home_group_church').data('department'),
          ChID = $('#editChurchForm').attr('data-id');
    let responsibleList = false,
        link = $('.get_info .active').data('link'),
        ChIsPartner = $('.left-contentwrap').attr('data-partner'),
        configReport = {
            church: ChID,
            last_5: true
        };

    if (ChIsPartner === 'True') {
        renderDealTable({done: 'False'});
        renderPaymentTable();
    }

    createChurchesDetailsTable({}, CHURCH_ID, link);

    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });

    $('.selectdb').select2();

//    Events
    $('#addHomeGroupToChurch').on('click', function () {
        clearAddHomeGroupData();
        if (!responsibleList) {
            responsibleList = true;
            setOptionsToPotentialLeadersSelect(CHURCH_ID);
        }
        setTimeout(function () {
            $('#addHomeGroup').addClass('active');
            $('.bg').addClass('active');
        }, 100)
    });

    $('#addUserToChurch').on('click', function () {
        initAddNewUser({
            getDepartments: false,
        });
        $('#searchedUsers').html('');
        $('#searchUserFromDatabase').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        document.querySelector('#searchUserFromDatabase').focus();
        $('#searchedUsers').css('height', 'auto');
        $('#chooseUserINBases').css('display', 'block');
    });

    $('#addNewUser').on('click', function () {
        let department_id = $('#church').data('department_id');
        let department_title = $('#church').data('department_title');
        let option = document.createElement('option');
        $(option).val(department_id).text(department_title).attr('selected', true).attr('required', false);
        $(this).closest('.popup').css('display', 'none');
        $('#addNewUserPopup').addClass('active');
        $('.bg').addClass('active');
        $('#chooseDepartment').html(option).attr('disabled', false);
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
    });

    $('#searchUserFromDatabase').on('keyup', _.debounce(function () {
        let search = $(this).val();
        (search.length > 2 ) && makeUsersFromDatabaseList();
    }, 500));

    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        createChurchesDetailsTable();
    }, 500));

    $('.get_info button').on('click', function () {
        let link = $(this).data('link');
        let exportUrl = $(this).data('export-url');
        let canEdit = $(this).data('editable');
        $('#church').removeClass('can_edit');
        if (canEdit) {
            $('#church').addClass('can_edit');
        }
        createChurchesDetailsTable({}, CHURCH_ID, link);
        $('.get_info button').removeClass('active');
        $(this).addClass('active');
        $('#export_table').attr('data-export-url', exportUrl);
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesDetailsTable, 'group_user');
    });

    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
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
        $('#addChurchReport').addClass('active');
        $('.bg').addClass('active');
    });

    $('.add-report').on('click',function (e) {
        e.preventDefault();
        let date = $(this).parent().closest('form').find('#dateReport').val().trim().split('.').reverse().join('-'),
            data = {
                date: date
            };
        postData(URLS.church.create_report(ChID),data).then(function () {
            $('#addChurchReport').removeClass('active');
            $('.bg').removeClass('active');
            showAlert('Отчет успешно создан');
            $('.preloader').css('display', 'block');
            ChurchReportsTable(configReport, false);
        }).catch(err => showAlert(err.message))
    });

    $('#delete_report').on('click', function (e) {
        e.preventDefault();
        deleteReport(ChurchReportsTable, configReport, false);
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

    $('#opening_date,#dateReport').datepicker({
        dateFormat: 'dd.mm.yyyy',
        autoClose: true
    });

    $('#addHomeGroup, #popup-create_partners, #popup-create_deal, #editReport, #popup-create_payment')
        .find('.pop_cont')
        .on('click', function (e) {
        e.stopPropagation();
    });

    let department = $('#editDepartmentSelect').val(),
        pastor = $('#editPastorSelect').val();

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
                showAlert("Сначала сохраните или отмените изменения в другом блоке")
            } else {
                $('.left-contentwrap').find('.search_city_link').css('visibility', '');
                $input.each(function () {
                    if (!$(this).hasClass('no__edit')) {
                        if ($(this).attr('disabled')) {
                            $(this).attr('disabled', false);
                        }
                        $(this).attr('readonly', false);
                        if ($(this).is('select') && $(this).is(':not(.no_select)')) {
                            $(this).select2();
                        }
                    }
                });
                $(this).addClass('active');
            }
            if ($(this).attr('data-edit-block') === 'editDepartment') {
                makePastorList(department, '#editPastorSelect', pastor);
                makeDepartmentList('#editDepartmentSelect', department);
            } else if ($(this).attr('data-edit-block') === 'editCurrency') {
                $('#report_currency').prop('disabled', false).select2().on('select2:open', function () {
                    $('.select2-search__field').focus();
                });
            }
            $('#address_choose').removeClass('address_isHide');
            $('#address_show').addClass('address_isHide');
        }
    });

    $('.accordion').find('.save__info').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').find('.edit').removeClass('active');
        let _self = this,
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
            webLink = $(this).closest('form').find('#web_site').val(),
            linkIcon = $('#site-link'),
            pastorLink = '/account/' + $(this).closest('form').find('#editPastorSelect').val();


        if (action === 'update-user') {
            $input.each(function () {
                let id = $(this).data('id');
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
                            } else if ($val.is('#is_open')) {
                                if ($val.is(':checked')) {
                                    formData.append(id, "true");
                                } else {
                                    formData.append(id, "false");
                                }
                            } else {
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
                let id = $('#editAddressForm').find('.chooseCity').attr('data-id'),
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
            updateChurch(idChurch, formData, success)
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
        pasteLink($('#editPastorSelect'), pastorLink);
        if (webLink == '') {
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

    $('#no_partners-link').on('click', function (e) {
        e.preventDefault();
        let url = $(this).attr('href');
        window.location = `${url}?church_id=${CHURCH_ID}&is_partner=false`;
    });

    $('#addHomeGroupForm').on('submit', function (event) {
        addHomeGroup(event, this, createChurchesDetailsTable);
    });

    $('#Sdelki').find('.edit').on('click', function (e) {
        e.preventDefault();
        let $edit = $('.edit'),
            noEdit = false;
        $edit.each(function () {
            if ($(this).hasClass('active')) {
                noEdit = true;
            }
        });
        let $block = $('#' + $(this).data('edit-block'));
        let $input = $block.find('input:not(.select2-search__field), select');
        let $hiddenBlock = $(this).parent().find('.hidden');
        $hiddenBlock.each(function () {
            $(this).removeClass('hidden');
        });

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
                showAlert("Сначала сохраните или отмените изменения в другом блоке")
            } else {
                $input.each(function () {
                    if (!$(this).hasClass('no__edit')) {
                        if ($(this).attr('disabled')) {
                            $(this).attr('disabled', false);
                        }
                        $(this).attr('readonly', false);
                        if ($(this).is('select') && $(this).is(':not(.no_select)')) {
                            $(this).select2();
                        }
                    }
                });
                $(this).addClass('active');
            }
        }
    });

    $('#Sdelki').find('.save__info').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').find('.edit').removeClass('active');
        let thisForm = $(this).closest('form');
        let $input = thisForm.find('input:not(.select2-search__field), select, textarea');
        let partnershipData = new FormData();
        let $newInput = $input.filter(":not(':checkbox')");
        let partner = thisForm.data('partner'),
            url = (!partner) ? URLS.partner.church_list() : URLS.partner.church_detail(partner),
            config = {
                method: (!partner) ? 'POST' : 'PATCH',
            },
            msg = (!partner) ? 'Церковь добавлена в партнество' : 'Изменения внесены';
        partnershipData.append('is_active', !!$input.is(':checked'));
        $newInput.each(function () {
            let id = $(this).data('id');
            if ($(this).hasClass('sel__date')) {
                partnershipData.append(id, reverseDate($(this).val().trim(), '-'));
            } else if ($(this).hasClass('par__group')) {
                if ($(this).val() != null) {
                    partnershipData.append(id, $(this).val());
                }
            } else {
                partnershipData.append(id, $(this).val());
            }
        });
        (!partner) && partnershipData.append('church', CHURCH_ID);
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
        postFormData(url, partnershipData, config).then(data => {
            let id = data.id;
            $('form#partnership').attr('data-partner', id);
            showAlert(msg);
        }).catch(err => {
            errorHandling(err);
        });
    });

    $('.sel__date').datepicker({
        autoClose: true,
        dateFormat: 'dd.mm.yyyy'
    });

    $('.tabs_report').find('button').on('click', function () {
        $('.preloader').css('display', 'block');
        $('.tabs_report').find('li').removeClass('current');
        $(this).closest('li').addClass('current');
        ChurchReportsTable(configReport, false);
    });

    $.validate({
        lang: 'ru',
        form: '#chReportForm',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            sendReport(false, configReport);

            return false;
        }
    });

    ChurchReportsTable(configReport, false);
    btnNeed();
    btnPartners();
    btnDeal();
    tabs();
    calcTransPayments();

    //Payments
    $("#popup-create_payment .top-text span").on('click', () => {
        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', 'none');
    });

    $("#close-payment").on('click', function (e) {
        e.preventDefault();
        $('#new_payment_rate').val(1);
        $('#in_user_currency').text('');
        $('#popup-create_payment').css('display', 'none');
    });

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
    });

    $('#sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

    function submitPayment() {
        let id = $('#complete-payment').attr('data-id'),
            data = {
                "sum": convertNum($('#new_payment_sum').val(), '.'),
                "description": $('#popup-create_payment textarea').val(),
                "rate": convertNum($('#new_payment_rate').val(), '.'),
                "sent_date": $('#sent_date').val().split('.').reverse().join('-'),
                "operation": $('#operation').val()
            };
        postData(URLS.event.church_report.create_uah_payment(id), data).then(() => {
            ChurchReportsTable(configReport, false);
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#popup-create_payment').css('display', 'none');
            showAlert('Оплата прошла успешно.');
            $('#complete-payment').prop('disabled', false);
        }).catch(err => {
            errorHandling(err);
            $('#complete-payment').prop('disabled', false);
        });
    }

    $.validate({
        lang: 'ru',
        form: '#payment-form',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            submitPayment();
            $('#complete-payment').prop('disabled', true);

            return false;
        }
    });

    $('#editDepartmentSelect').on('change', function () {
        let id = parseInt($(this).val());
        makePastorList(id, '#editPastorSelect');
    });

    $('.close-map').on('click', function () {
        if(!$(this).hasClass('active')){
            $(".a-map").removeClass('active');
        }
    });

    btnLocationControls();

});
