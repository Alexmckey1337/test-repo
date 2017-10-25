'use strict';
import URLS from '../Urls/index';
import {postData} from "../Ajax/index";
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import {dataURLtoBlob} from "../Avatar/index";
import {getCountries, getRegions, getCities, getDepartments, getResponsible, getStatuses, getDivisions} from "../GetList/index";
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
        $phoneNumber = $('#phone'),
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
        let phoneNumber = $phoneNumber.inputmask('unmaskedvalue');
        formData.append('phone_number', phoneNumber)
    }
    if ($extraPhoneNumbers.val()) {
        formData.append('extra_phone_numbers', JSON.stringify($extraPhoneNumbers.val().split(',').map((item) => item.trim())));
    } else {
        formData.append('extra_phone_numbers', JSON.stringify([]));
    }
    // if ($('#partner').is(':checked')) {
    //     let partner = {};
    //     partner.value = parseInt($('#val_partnerships').val()) || 0;
    //     partner.currency = parseInt($('#payment_currency').val());
    //     partner.date = $('#partnerFrom').val() || null;
    //     partner.responsible = parseInt($("#chooseManager").val());
    //     formData.append('partner', JSON.stringify(partner));
    // }
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

    $preloader.css('display', 'block');
    console.log('FormData -->',formData);
    console.log('Departments -->',formData.get('departments'));
    postData(URLS.user.list(), formData).then(function (data) {
        $preloader.css('display', 'none');
        showPopupAddUser(data);
        // $createUser.find('input').each(function () {
        //     $(this).val('').attr('disabled', false);
        // });
        //Пересмотреть ф-цию очистки
        // $createUser.find('.cleared').each(function () {
        //     $(this).find('option').eq(0).prop('selected', true).select2()
        // });
        $('#addNewUserPopup').css('display', 'none');
        if (callback != null) {
            callback(data);
        }
        $('#saveNew').attr('disabled', false);
    }).catch(function (err) {
        $preloader.css('display', 'none');
        showAlert('Проверьте введенные данные', 'Ошибка');
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
        let flag = $('#addNewUserPopup').attr('data-flagdepart');
        $('#addPopup').css('display', 'none').remove();
        $('body').addClass('no_scroll');
        $('#addNewUserPopup').find('form').removeClass('active');
        clearAddNewUser();
        if (flag) {
            initAddNewUser({
                getDepartments: false,
            });
        } else {
            $('#createUser').find('select#chooseDepartment').select2('destroy').find('option').remove();
            initAddNewUser();
        }
        $('#addNewUserPopup').css('display', 'block');
        $('#addNewUserPopup').find('.body').scrollTop(0);
    });
}

function clearAddNewUser() {
    let form = $('#createUser'),
        $select = form.find('#spir_level #church_list');
    // form.find('#partner').attr('checked', false);
    // form.find('.hidden-partner').hide();
    form.find('#edit-photo').attr('data-source', '').find('img').attr('src', '/static/img/no-usr.jpg');
    form.find('.anketa-photo').unbind('click');
    form.find('select:not(#payment_currency, #spir_level, #chooseDepartment, #church_list).select2-hidden-accessible')
        .select2('destroy').find('option').remove();
    form.find('#chooseResponsible, #chooseRegion, #chooseCity').attr('disabled', true);
    form.find('input').each(function () {
        $(this).val('');
    });
    form.find('.phone .comment').text('');
    $('#bornDate').val('');
    $('#repentanceDate').val('');
    $select.each(function () {
        $(this).val(null).trigger("change");
    });
}

export function initAddNewUser(config = {}) {
    let configDefault = {
        getCountries: true,
        getDepartments: true,
        getStatuses: true,
        getDivisions: true,
        // getCountryCodes: true,
    };
    let $form = $('#createUser'),
        $input = $form.find('input');
    // $input.each(function () {
    //     $(this).val('');
    // });
    // $form.find('.phone .comment').text('');
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
    // if (configDefault.getCountryCodes) {
    //     getCountryCodes().then(function (data) {
    //         let codes = data;
    //         let rendered = [];
    //         codes.forEach(function (item) {
    //             let option = document.createElement('option');
    //             $(option).val(item.phone_code).text(item.title + ' ' + item.phone_code);
    //             if (item.phone_code == '+38') {
    //                 $(option).attr('selected', true);
    //             }
    //             rendered.push(option);
    //         });
    //         $('#chooseCountryCode').html(rendered).on('change', function () {
    //             let code = $(this).val();
    //             $('#phoneNumberCode').val(code);
    //         }).trigger('change');
    //     });
    // }

    $('#spir_level').select2();
    $('#church_list').select2();

    $('#repentance_date').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#partnerFrom').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('#bornDate').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    // $('#chooseCountryCode').select2();

    // $('#partner').on('change', function () {
    //     let partner = $(this).is(':checked');
    //     if (partner) {
    //         $('.hidden-partner').css('display', 'block');
    //     } else {
    //         $('.hidden-partner').css('display', 'none');
    //     }
    // });
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

export function addUserToHomeGroupHG(data) {
    let $homeGroup = $('#home_group');
    const ID = $homeGroup.data('id');
    let id = data.id;
    let config = {};
    config.user_id = id;
    return new Promise(function (resolve, reject) {
        let data = {
            method: 'POST',
            url: URLS.home_group.add_user(ID),
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

export function saveUser(el) {
    let $input, $select, fullName, first_name, last_name, middle_name, departments, hierarchy, phone_number, data, id;
    let send = true;
    let $department = $($(el).closest('.pop_cont').find('#departmentSelect'));
    departments = $department.val();
    let $hierarchy = $($(el).closest('.pop_cont').find('#hierarchySelect'));
    hierarchy = $hierarchy.val();
    let $master = $('#master_hierarchy');
    let master_id = $master.val() || "";
    let $fullname = $($(el).closest('.pop_cont').find('input.fullname'));
    fullName = $fullname.val().split(' ');
    let $phone_number = $($(el).closest('.pop_cont').find('#phone_number'));
    phone_number = $phone_number.val();
    if (!$fullname.val()) {
        $fullname.css('border-color', 'red');
        send = false;
    } else {
        $fullname.removeAttr('style');
    }
    if (!master_id) {
        $('label[for="master_hierarchy"]').css('color', 'red');
        send = false;
    } else {
        $('label[for="master_hierarchy"]').removeAttr('style');
    }
    if (!phone_number) {
        $phone_number.css('border-color', 'red');
        send = false;
    } else {
        $phone_number.removeAttr('style');
    }
    if (!send) {
        return
    }
    first_name = fullName[1];
    last_name = fullName[0];
    middle_name = fullName[2] || "";
    data = {
        email: $($(el).closest('.pop_cont').find('#email')).val(),
        first_name: first_name,
        last_name: last_name,
        middle_name: middle_name,
        hierarchy: hierarchy,
        departments: departments,
        master: master_id,
        skype: $($(el).closest('.pop_cont').find('#skype')).val(),
        phone_number: phone_number,
        extra_phone_numbers: _.filter(_.map($($(el).closest('.pop_cont').find('#extra_phone_numbers')).val().split(","), x => x.trim()), x => !!x),
        repentance_date: $($(el).closest('.pop_cont').find('#repentance_date')).val() || null,
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        region: $($(el).closest('.pop_cont').find('#region')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val()
    };
    id = $(el).closest('.pop_cont').find('img').attr('alt');
    saveUserData(data, id);
    $(el).text("Сохранено");
    $(el).closest('.popap').find('.close-popup.change__text').text('Закрыть');
    $(el).attr('disabled', true);
    $input = $(el).closest('.popap').find('input');
    $select = $(el).closest('.popap').find('select');
    $select.on('change', function () {
        $(el).text("Сохранить");
        $(el).closest('.popap').find('.close-popup').text('Отменить');
        $(el).attr('disabled', false);
    });
    $input.on('change', function () {
        $(el).text("Сохранить");
        $(el).closest('.popap').find('.close-popup').text('Отменить');
        $(el).attr('disabled', false);
    })
}

function saveUserData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        ajaxRequest(URLS.user.detail(id), json, function (data) {
        }, 'PATCH', false, {
            'Content-Type': 'application/json'
        });
    }
}