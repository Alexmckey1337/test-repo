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
    editChurches,
} from "./modules/Church/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import accordionInfo from './modules/accordionInfo';
import {makePastorList, makeDepartmentList} from "./modules/MakeList/index";
import pasteLink from './modules/pasteLink';
import {addHomeGroup, clearAddHomeGroupData} from "./modules/HomeGroup/index";
import reverseDate from './modules/Date/index';
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
    const D_ID = $('#added_home_group_church').data('department');
    let responsibleList = false,
        link = $('.get_info .active').data('link'),
        ChIsPartner = $('.left-contentwrap').attr('data-partner');

    if (ChIsPartner === 'True') {
        renderDealTable({done: 'False'});
        renderPaymentTable();
    }
    createChurchesDetailsTable({}, CHURCH_ID, link);

    $('#added_home_group_pastor').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
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

    $('#addHomeGroup, #popup-create_partners, #popup-create_deal').find('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });

    let department = $('#editDepartmentSelect').val(),
        pastor = $('#editPastorSelect').val();

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
                    if ($(this).is(':not([multiple])')) {
                        if (!$(this).is('.no_select')) {
                            $(this).select2('destroy');
                        }
                    }
                }
            });
            $(this).removeClass('active');
        } else {
            if($(this).attr('data-edit-block') === 'editDepartment'){
                makePastorList(department, '#editPastorSelect', pastor);
                makeDepartmentList('#editDepartmentSelect', department).then(function () {
                $('#editDepartmentSelect').on('change', function () {
                    let id = parseInt($(this).val());
                    makePastorList(id, '#editPastorSelect');
                })
            });
            }else if($(this).attr('data-edit-block') === 'editCurrency'){
                $('#report_currency').prop('disabled', false).select2().on('select2:open', function () {
                $('.select2-search__field').focus();
            });
            }
            $input.each(function () {
                if (!$(this).hasClass('no__edit')) {
                    if ($(this).attr('disabled')) {
                        $(this).attr('disabled', false);
                    }
                    $(this).attr('readonly', false);
                }
            });
            $(this).addClass('active');
        }
    });

    $('.accordion').find('.save__info').on('click', function (e) {
        e.preventDefault();
        let idChurch = $('.accordion').attr('data-id');
        editChurches($(this), idChurch);
        let pastorLink = '/account/' + $(this).closest('form').find('#editPastorSelect').val();
        pasteLink($('#editPastorSelect'), pastorLink);
        let webLink = $(this).closest('form').find('#web_site').val();
        let linkIcon = $('#site-link');
        if (webLink == '') {
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

    $('#no_partners-link').on('click', function (e) {
        e.preventDefault();
        let url = $(this).attr('href');
        window.location = `${url}?church_id=${CHURCH_ID}&is_partner=false`;
    });

    $('#addHomeGroupForm').on('submit', function () {
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

    btnNeed();
    btnPartners();
    btnDeal();
    tabs();

});
