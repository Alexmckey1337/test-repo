'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls/index';
import ajaxRequest from './modules/Ajax/ajaxRequest';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {createPayment} from "./modules/Payment/index";
import {createSummitUsersTable, predeliteAnket, deleteSummitProfile, unsubscribeOfSummit,
        updateSummitParticipant, registerUser, makePotencialSammitUsersList} from "./modules/Summit/index";
import {showPopupHTML, closePopup} from "./modules/Popup/popup";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import {makePastorListNew, makePastorListWithMasterTree} from "./modules/MakeList/index";
import {addUserToSummit} from "./modules/User/addUserToSummit";

$(document).ready(function () {
    const $summitUsersList = $('#summitUsersList');
    const SUMMIT_ID = $summitUsersList.data('summit');

    function makeSummitInfo() {
        let width = 150,
            count = 1,
            position = 0,
            $carousel = $('#carousel'),
            $list = $carousel.find('ul'),
            $listElements;
        $listElements = $list.find('li');
        $carousel.find('.arrow-left').on('click', function () {
            position = Math.min(position + width * count, 0);

            $($list).css({
                marginLeft: position + 'px'
            });
        });

        $carousel.find('.arrow-right').on('click', function () {
            position = Math.max(position - width * count, -width * ($listElements.length - 3));
            $($list).css({
                marginLeft: position + 'px'
            });
        });
    }

    $('#export_table').on('click', function () {
        exportTableData(this);
    });

    createSummitUsersTable({summit: SUMMIT_ID});

    makeSummitInfo();
    $('body').on('click', '#carousel li span', function () {
        $('#carousel').find('li').removeClass('active');
        $(this).parent().addClass('active')
    });

    $("#popup h3 span").on('click', function () {
        $('#popup').css('display', 'none');
        $('.choose-user-wrap').css('display', 'block');
    });

    $("#close").on('click', function () {
        $('#popup').css('display', 'none');
        $('.choose-user-wrap').css('display', 'block');
    });

    $("#closeDelete").on('click', function () {
        $('#popupDelete').css('display', 'none');
    });

    $("#close-payment").on('click', function () {
        $('#popup-create_payment').css('display', 'none');
    });

    $("#close-payments").on('click', function () {
        $('#popup-payments').css('display', 'none');
        $('#popup-payments table').html('');
    });

    $("#popup-create_payment .top-text span").on('click', function (el) {
        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', '');
    });

    $("#popup-payments .top-text span").on('click', function (el) {
        $('#popup-payments').css('display', '');
        $('#popup-payments table').html('');
    });

    $('#payment-form').on("submit", function (e) {
        e.preventDefault();
        let data = $('#payment-form').serializeArray();
        let userID;
        let new_data = {};
        data.forEach(function (field) {
            if (field.name == 'sent_date') {
                new_data[field.name] = field.value.trim().split('.').reverse().join('-');
            } else if (field.name != 'id') {
                new_data[field.name] = field.value
            } else {
                userID = field.value;
            }
        });
        if (userID) {
            createPayment({
                data: new_data
            }, userID).then(function (data) {
                console.log(data);
            });
        }
        // create_payment(id, sum, description, rate, currency);

        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', 'none');
    });

    $(".add-user-wrap .top-text span").on('click', function () {
        $('.add-user-wrap').css('display', '');
    });

    $("#load-tickets").on('click', function () {
        let summit_id = $('#summitUsersList').data('summit');
        ajaxRequest(URLS.generate_summit_tickets(summit_id), null, function (data) {
            console.log(data);
        }, 'GET', true, {
            'Content-Type': 'application/json'
        });
    });

    $(".add-user-wrap").on('click', function (el) {
        if (el.target !== this) {
            return;
        }
        $('.add-user-wrap').css('display', '');
    });

    $("#popupDelete").on('click', function (el) {
        if (el.target !== this) {
            return;
        }
        $('#popupDelete').css('display', '');
    });

    $("#popupDelete .top-text span").on('click', function (el) {
        $('#popupDelete').css('display', '');
    });

    $(".choose-user-wrap").on('click', function (el) {
        if (el.target !== this) {
            return;
        }
        $('.choose-user-wrap').css('display', '');
        $('searchUsers').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
    });

    $(".choose-user-wrap .top-text > span").on('click', function () {
        $('searchUsers').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        $('.choose-user-wrap').css('display', '');
    });

    $('.choose-user-wrap h3 span').on('click', function () {
        $('searchUsers').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        $('.choose-user-wrap').css('display', '');
        $('.add-user-wrap').css('display', 'block');
        $('#choose').on('click', function () {
            $('.choose-user-wrap').css('display', 'block');
            $('.add-user-wrap').css('display', '');
        });
    });

    $('#addNewUser').on('click', function () {
        $(this).closest('.popup').css('display', 'none');
        $('#addNewUserPopup').css('display', 'block');
    });

    // $('#choose').on('click', function () {
    //     $('.choose-user-wrap').css('display', 'block');
    //     $('.add-user-wrap').css('display', 'none');
    //     document.querySelector('#searchUsers').focus();
    // });

    $('#changeSum').on('click', function () {
        $('#summit-value').removeAttr('readonly');
        $('#summit-value').focus();
    });

    $('#changeSumDelete').on('click', function () {
        $('#summit-valueDelete').removeAttr('readonly');
        $('#summit-valueDelete').focus();
    });

    $('#preDeleteAnket').on('click', function () {
        let _self = this;
        let anketID = $(this).attr('data-anket');
        let fullName = $('#fullNameCard').text();
        predeliteAnket(anketID).then(function (data) {
            $(_self).closest('.pop-up-splash').hide();
            let div = document.createElement('div');
            let mainBlock = document.createElement('div');
            let topText = document.createElement('div');
            let title = document.createElement('h3');
            let closePopup = document.createElement('span');
            let body = document.createElement('div');
            let user = document.createElement('h2');
            $(closePopup).addClass('close').addClass('close-popup').text('×').on('click', function () {
                $(this).closest('.pop-up-universal').hide().remove();
            });
            $(title).text('Подтверждение удаления');
            $(topText).addClass('top-text').append(title).append(closePopup);

            $(mainBlock).addClass('splash-screen').append(topText);

            $(body).addClass('wrap');
            $(user).text(fullName);
            $(mainBlock).append(user);
            let keys = Object.keys(data);
            let list = document.createElement('dl');
            $(list).addClass('list__item');
            keys.forEach(function (item) {
                let dt = document.createElement('dt');
                let dd = document.createElement('dd');
                $(dt).text(item);
                console.log(data[item]);
                // data[item].forEach(function (i) {
                //     $(dd).text(i.length)
                // });
                $(dd).text(data[item].length);
                $(list).append(dt).append(dd);
            });
            $(body).append(list);
            $(mainBlock).append(body);
            let splashButtons = document.createElement('div');
            let deleteBtn = document.createElement('button');
            $(deleteBtn)
                .addClass('delete_btn')
                .attr('id', 'deleteAnket')
                .text('Подтвердить удаление')
                .on('click', function () {
                    deleteSummitProfile(anketID).then(function (msg) {
                        $(div).hide().remove();
                        $('.pop-up-universal').hide();
                        setTimeout(() => showAlert(msg), 100);
                        createSummitUsersTable({summit: SUMMIT_ID});
                    });
                });
            $(splashButtons).addClass('splash-buttons wrap').append(deleteBtn);
            $(mainBlock).append(splashButtons);
            $(div).append(mainBlock);
            showPopupHTML(div);
        }).catch(function (err) {
            console.log(err);
        });
        // closePopup(this);
    });

    $('yes').on('click', function () {
        let summitAnketID = $(this).attr('data-anket');
        $('#deletePopup').css('display', '');
        unsubscribeOfSummit(summitAnketID);
    });

    $('#deletePopup').click(function (el) {
        if (el.target != this) {
            return;
        }
        $(this).hide();
    });

    $('#no').click(function () {
        $('#deletePopup').hide();
    });

    $('#deletePopup .top-text span').click(function () {
        $('#deletePopup').hide();
    });

    $('#applyChanges').on('click', function () {
        let profileID = $(this).data('id');
        let formData = $('#participantInfoForm').serializeArray();
        let data = {};

        formData.forEach(function (item) {
            data[item.name] = (item.value == 'on') ? true : item.value;
        });

        updateSummitParticipant(profileID, data);
        closePopup(this);
    });

    $('#complete').on('click', function () {
        let userID = $(this).attr('data-id'),
            description = $('#popup textarea').val(),
            summitID = $('#summitUsersList').data('summit');
        registerUser(userID, summitID, description);

        document.querySelector('#popup').style.display = 'none';
    });

    // function create_payment(id, sum, description, rate, currency) {
    //     let data = {
    //         "sum": sum,
    //         "description": description,
    //         "rate": rate,
    //         "currency": currency
    //     };
    //
    //     let json = JSON.stringify(data);
    //
    //     ajaxRequest(URLS.summit_profile.create_payment(id), json, function (JSONobj) {
    //         showAlert('Оплата прошла успешно.');
    //     }, 'POST', true, {
    //         'Content-Type': 'application/json'
    //     }, {
    //         403: function (data) {
    //             data = data.responseJSON;
    //             showAlert(data.detail)
    //         }
    //     });
    // }

    // function show_payments(id) {
    //     ajaxRequest(URLS.summit_profile.list_payments(id), null, function (data) {
    //         let payments_table = '';
    //         let sum, date_time;
    //         data.forEach(function (payment) {
    //             sum = payment.effective_sum_str;
    //             date_time = payment.created_at;
    //             payments_table += `<tr><td>${sum}</td><td>${date_time}</td></tr>`
    //         });
    //         $('#popup-payments table').html(payments_table);
    //         $('#popup-payments').css('display', 'block');
    //     }, 'GET', true, {
    //         'Content-Type': 'application/json'
    //     }, {
    //         403: function (data) {
    //             data = data.responseJSON;
    //             showAlert(data.detail)
    //         }
    //     });
    // }

    $('#departments_filter').select2();
    $('.select__db').select2();

    //    Events
    $("#add").on('click', function () {
        // $('#addUser').css('display', 'block');
        initAddNewUser();
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
        $('#searchedUsers').html('');
        $('#searchUsers').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        $('#chooseUserINBases').css('display', 'block');
        document.querySelector('#searchUsers').focus();
    });

    //Filter
    $('.apply-filter').on('click', function () {
        applyFilter(this, createSummitUsersTable);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('#departments_filter').on('change', function () {
        $('#master_tree').prop('disabled', true);
        let department_id = parseInt($(this).val()) || null;
        makePastorListNew(department_id, ['#master_tree', '#master']);
    });

    $('#master_tree').on('change', function () {
        $('#master').prop('disabled', true);
        let config = {};
        let master_tree = parseInt($(this).val());
        if (!isNaN(master_tree)) {
            config = {master_tree: master_tree}
        }
        makePastorListWithMasterTree(config, ['#master'], null);
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createSummitUsersTable({summit: SUMMIT_ID, page: 1});
    }, 500));

    $('#searchUsers').on('keyup', _.debounce(function () {
        makePotencialSammitUsersList();
    }, 500));

    $('#summitsTypes').find('li').on('click', function () {
        $('.preloader').css('display', 'block');
        let config = {};
        config.summit = $(this).data('id');
        config.page = 1;
        createSummitUsersTable(config);
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createSummitUsersTable);
    });

    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });

    $.validate({
        lang: 'ru',
        form: '#createUser',
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(addUserToSummit).then(function () {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        }
    });

    $('#filterPopup').find('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });

    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });

    $('#summitUsersList').on('click', '.ticket_status', _.debounce(function(e) {
        console.log($(this));
        let option = {
                method: 'POST',
                credentials: "same-origin",
                headers: new Headers({
                    'Content-Type': 'application/json',
                })
            };
        const profileId = $(this).data('user-id');
        fetch(URLS.summit_profile.set_ticket_status(profileId), option)
            .then( res => res.json())
            .then(data => {
                $(this).find('.text').text(data.text);
                if(data.new_status == 'given' || data.new_status == 'print' ) {
                    $(this).find('div').show();
                    (data.new_status == 'given') ? $(this).find('input').prop('checked', true) : $(this).find('input').prop('checked', false);
                } else {
                     $(this).find('div').hide();
                }
            })

    },300));

});