'use strict';
import URLS from '../Urls/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import ajaxSendFormData from '../Ajax/ajaxSendFormData';
import {dataURLtoBlob} from "../Avatar/index";
import {getCountries, getRegions, getCities, getDepartments, getResponsible, getStatuses, getDivisions,
        getCountryCodes, getManagers} from "../GetList/index";
import {showAlert} from "../ShowNotifications/index";

export function addUserToHomeGroup(user_id, hg_id, exist = false) {
    let url = URLS.user.set_home_group(user_id);
    let config = {
        url: url,
        method: "POST",
        data: {
            home_group_id: hg_id
        }
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}

export function addUserToChurch(user_id, id, exist = false) {
    let url = URLS.user.set_church(user_id);
    let config = {
        url: url,
        method: "POST",
        data: {
            church_id: id
        }
    };
    return new Promise(function (resolve, reject) {
        let codes = {
            200: function (data) {
                resolve(data);
            },
            400: function (data) {
                reject(data)
            }
        };
        newAjaxRequest(config, codes, reject)
    });
}

export function createNewUser(callback) {
    let $createUser = $('#createUser'),
        $phoneNumber = $('#phoneNumber'),
        $extraPhoneNumbers = $('#extra_phone_numbers'),
        $preloader = $('.preloader');

    let oldForm = document.forms.createUser;
    let formData = new FormData(oldForm);
    // if ($('#division_drop').val()) {
    //     formData.append('divisions', JSON.stringify($('#chooseDivision').val()));
    // } else {
    //     formData.append('divisions', JSON.stringify([]));
    // }
    let divisions = $('#chooseDivision').val() || [];
    formData.append('divisions', JSON.stringify(divisions));

    let spirLevel = $('#spir_level').val() || null;
    if (spirLevel !== 'Выберите духовный уровень') {
        formData.append('spiritual_level', spirLevel);
    }

    formData.append('departments', JSON.stringify($('#chooseDepartment').val()));
    if ($phoneNumber.val()) {
        let phoneNumber = $('#phoneNumberCode').val() + $phoneNumber.val();
        formData.append('phone_number', phoneNumber)
    }
    if ($extraPhoneNumbers.val()) {
        formData.append('extra_phone_numbers', JSON.stringify($extraPhoneNumbers.val().split(',').map((item) => item.trim())));
    } else {
        formData.append('extra_phone_numbers', JSON.stringify([]));
    }
    if ($('#partner').is(':checked')) {
        let partner = {};
        partner.value = parseInt($('#val_partnerships').val()) || 0;
        partner.currency = parseInt($('#payment_currency').val());
        partner.date = $('#partnerFrom').val() || null;
        partner.responsible = parseInt($("#chooseManager").val());
        formData.append('partner', JSON.stringify(partner));
    }
    let send_image = $('#file').prop("files").length || false;
    if (send_image) {
        try {
            let blob;
            blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
            formData.append('image', blob, 'logo.jpg');
            formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
        } catch (err) {
            console.log(err);
        }
    }
    let url = URLS.user.list();
    let config = {
        url: url,
        data: formData,
        method: 'POST'
    };

    $preloader.css('display', 'block');
    return ajaxSendFormData(config).then(function (data) {
        $preloader.css('display', 'none');
        // showPopup(`${data.fullname} добален(а) в базу данных`);
        showPopupAddUser(data);
        $createUser.find('input').each(function () {
            $(this).val('').attr('disabled', false);
        });
        //Пересмотреть ф-цию очистки
        $createUser.find('.cleared').each(function () {
            $(this).find('option').eq(0).prop('selected', true).select2()
        });
        $('#addNewUserPopup').css('display', 'none');
        if (callback != null) {
            callback(data);
        }
    }).catch(function (data) {
        $preloader.css('display', 'none');
        if (data.phone_number) {
            showAlert(data.phone_number.message);
            $('#createUser').css("transform", "translate3d(0px, 0px, 0px)");
        }
        if (data.detail) {
            showAlert(data.detail[0]);
        }
    });
}

function showPopupAddUser(data) {
    let tmpl = document.getElementById('addUserSuccessPopup').innerHTML;
    let rendered = _.template(tmpl)(data);
    $('body').append(rendered);

    $('#addPopup').find('.close, .rewrite').on('click', function (e) {
        e.preventDefault();
        $('#addPopup').css('display', 'none').remove();
        $('#addNewUserPopup').find('form').removeClass('active');
        clearAddNewUser();
        $('#addNewUserPopup').find('.body').scrollTop(0);
        if ($(this).is('a')) {
            let url = $(this).attr('href');
            setTimeout(function () {
                window.open(url);
            }, 1000);
        }
    });
    $('#addPopup').find('.addMore').on('click', function () {
        $('#addPopup').css('display', 'none').remove();
        $('body').addClass('no_scroll');
        $('#addNewUserPopup').find('form').removeClass('active');
        $('#addNewUserPopup').css('display', 'block');
        clearAddNewUser();
        $('#addNewUserPopup').find('.body').scrollTop(0);
    });
}

function clearAddNewUser() {
    let form = $('#createUser');
    let flag = $('#addNewUserPopup').attr('data-flagdepart');
    form.find('#partner').attr('checked', false);
    form.find('.hidden-partner').hide();
    form.find('#edit-photo').attr('data-source', '').find('img').attr('src', '/static/img/no-usr.jpg');
    form.find('.anketa-photo').unbind('click');
    form.find('select:not(#payment_currency, #spir_level, #chooseDepartment).select2-hidden-accessible')
        .select2('destroy').find('option').remove();
    if (flag) {
        initAddNewUser({
            getDepartments: false,
        });
    } else {
        form.find('select#chooseDepartment').select2('destroy').find('option').remove();
        initAddNewUser();
    }
    form.find('#chooseResponsible, #chooseRegion, #chooseCity').attr('disabled', true);
    form.find('input').each(function () {
        $(this).val('');
    });
    form.find('#spir_level').select2('destroy').find('option').attr('selected', false)
        .find('option:first-child').attr('selected', true);
}

export function initAddNewUser(config = {}) {
    let configDefault = {
        getCountries: true,
        getDepartments: true,
        getStatuses: true,
        getDivisions: true,
        getCountryCodes: true,
        getManagers: true,
    };
    let $form = $('#createUser'),
        $input = $form.find('input');
    $input.each(function () {
        $(this).val('');
    });
    Object.assign(configDefault, config);
    if (configDefault.getCountries) {
        getCountries().then(function (data) {
            let rendered = [];
            let option = document.createElement('option');
            $(option).val('').text('Выберите страну').attr('disabled', true).attr('selected', true);
            rendered.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.title).text(item.title).attr('data-id', item.id);
                rendered.push(option);
            });
            $('#chooseCountry').html(rendered).on('change', function () {
                let config = {};
                config.country = $(this).find(':selected').data('id');
                getRegions(config).then(function (data) {
                    let rendered = [];
                    let option = document.createElement('option');
                    $(option).val('').text('Выберите регион');
                    rendered.push(option);
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.title).text(item.title).attr('data-id', item.id);
                        rendered.push(option);
                    });
                    $('#chooseRegion').html(rendered).attr('disabled', false).on('change', function () {
                        let config = {};
                        config.region = $(this).find(':selected').data('id');
                        getCities(config).then(function (data) {
                            let rendered = [];
                            let option = document.createElement('option');
                            $(option).val('').text('Выберите город');
                            rendered.push(option);
                            data.forEach(function (item) {
                                let option = document.createElement('option');
                                $(option).val(item.title).text(item.title).attr('data-id', item.id);
                                rendered.push(option);
                            });
                            $('#chooseCity').html(rendered).attr('disabled', false).select2();
                        })
                    }).select2();
                })
            }).select2();
        });
    }
    if (configDefault.getDepartments) {
        getDepartments().then(function (data) {
            let departments = data.results;
            let rendered = [];
            let option = document.createElement('option');
            // $(option).text('Выберите департамент').attr('disabled', true).attr('selected', true);
            // rendered.push(option);
            departments.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.title);
                rendered.push(option);
            });
            $('#chooseDepartment').html(rendered).select2().removeAttr('disabled').on('change', function () {
                let status = $('#chooseStatus').find('option').filter(':selected').data('level');
                let department = $(this).val();
                if (!status) {
                    return;
                }
                getResponsible(department, status).then(function (data) {
                    let rendered = [];
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        rendered.push(option);
                    });
                    $('#chooseResponsible').html(rendered).attr('disabled', false).select2();
                })
            });
        });
    } else {
        $('#addNewUserPopup').attr('data-flagdepart', true);
    }
    if (configDefault.getStatuses) {
        getStatuses().then(function (data) {
            let statuses = data;
            let rendered = [];
            let option = document.createElement('option');
            $(option).text('Выберите статус').attr('disabled', true).attr('selected', true);
            rendered.push(option);
            statuses.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).attr('data-level', item.level).text(item.title);
                rendered.push(option);
            });
            return rendered;
        }).then(function (rendered) {
            $('#chooseStatus').html(rendered).select2().on('change', function () {
                let status = $(this).find('option').filter(':selected').data('level');
                let department = $('#chooseDepartment').val();
                getResponsible(department, status).then(function (data) {
                    let rendered = [];
                    if (status > 60) {
                        let option = document.createElement('option');
                        $(option).val('').text('Нет ответственного');
                        rendered.push(option);
                    }
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        rendered.push(option);
                    });
                    $('#chooseResponsible').html(rendered).attr('disabled', false).select2();
                })
            });
        });
    }
    if (configDefault.getDivisions) {
        getDivisions().then(function (data) {
            let divisions = data.results;
            let rendered = [];
            divisions.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.title);
                rendered.push(option);
            });
            $('#chooseDivision').html(rendered).select2();
        });
    }
    if (configDefault.getCountryCodes) {
        getCountryCodes().then(function (data) {
            let codes = data;
            let rendered = [];
            codes.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.phone_code).text(item.title + ' ' + item.phone_code);
                if (item.phone_code == '+38') {
                    $(option).attr('selected', true);
                }
                rendered.push(option);
            });
            $('#chooseCountryCode').html(rendered).on('change', function () {
                let code = $(this).val();
                $('#phoneNumberCode').val(code);
            }).trigger('change');
        });
    }
    if (configDefault.getManagers) {
        getManagers().then(function (data) {
            let rendered = [];
            let option = document.createElement('option');
            $(option).val('').text('Выберите менеджера').attr('disabled', true).attr('selected', true);
            rendered.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                rendered.push(option);
            });
            $('#chooseManager').html(rendered).select2();
        });
    }

    $('#spir_level').select2();

    $('#repentance_date').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#partnerFrom').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#bornDate').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#chooseCountryCode').select2();

    $('#partner').on('change', function () {
        let partner = $(this).is(':checked');
        if (partner) {
            $('.hidden-partner').css('display', 'block');
        } else {
            $('.hidden-partner').css('display', 'none');
        }
    });
}

export function addUser2Church(data) {
    const CHURCH_ID = $('#church').data('id');
    let userId = data.id;
    let config = {};
    config.user_id = userId;
    return new Promise(function (resolve, reject) {
        let data = {
            method: 'POST',
            url: URLS.church.add_user(CHURCH_ID),
            data: config
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }
        };
        newAjaxRequest(data, status, reject);
    });
}