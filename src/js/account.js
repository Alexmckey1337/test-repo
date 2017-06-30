function updateUser(id, data, success = null) {
    let url = URLS.user.detail(id);
    let config = {
        url: url,
        data: data,
        method: 'PATCH'
    };
    return ajaxSendFormData(config).then(function (data) {
        if (success) {
            $(success).text('Сохранено');
            setTimeout(function () {
                $(success).text('');
            }, 3000);
        }
        return data;
    }).catch(function (data) {
        let msg = "";
        if (typeof data == "string") {
            msg += data;
        } else {
            let errObj = null;
            if (typeof data != 'object') {
                errObj = JSON.parse(data);
            } else {
                errObj = data;
            }
            for (let key in errObj) {
                msg += key;
                msg += ': ';
                if (errObj[key] instanceof Array) {
                    errObj[key].forEach(function (item) {
                        msg += item;
                        msg += ' ';
                    });
                } else {
                    msg += errObj[key];
                }
                msg += '; ';
            }
        }

        showPopup(msg);
        return false;
    });
}

function makeResponsibleList(department, status, flag = false) {
    let $selectResponsible = $('#selectResponsible');
    let activeMaster = $selectResponsible.val();
    let activeOption = $selectResponsible.find('option:selected');
    getResponsible(department, status).then(function (data) {
        let rendered = [];
        rendered.push(activeOption);
        if (flag) {
            if (status > 5) {
                let option = document.createElement('option');
                $(option).val('').text('Нет ответственного');
                rendered.push(option);
            } else {
                rendered.splice(0,rendered.length);
            }
        }
        data.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.fullname);
            if (activeMaster == item.id) {
                $(option).attr('selected', true);
            }
            rendered.push(option);
        });
        $selectResponsible.html(rendered);
    })
}

const ID = getLastId();

$('.hard-login').on('click', function () {
    let user = $(this).data('user-id');
    setCookie('hard_user_id', user, {path: '/'});
    window.location.reload();
});
$("#tabs1 li").on('click', function () {
    let id_tab = $(this).attr('data-tab');
    $('[data-tab-content]').hide();
    $('[data-tab-content="' + id_tab + '"]').show();
    $(this).closest('.tab-status').find('li').removeClass('active');
    $(this).addClass('active');
});

$('#send_need').on('click', function () {
    let need_text = $('#id_need_text').val();
    let url = URLS.partner.update_need($(this).data('partner'));
    let need = JSON.stringify({'need_text': need_text});
    ajaxRequest(url, need, function () {
        showPopup('Нужда сохранена.');
    }, 'PUT', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
        }
    });
    $(this).siblings('.editText').removeClass('active');
    $(this).parent().siblings('textarea').attr('readonly', true);
});
$('#sendNote').on('click', function () {
    let _self = this;
    let id = $(_self).data('id');
    let resData = new FormData();
    resData.append('description', $('#id_note_text').val());
    updateUser(id, resData).then(() => showPopup('Ваше примечание добавлено.'));
    $(this).siblings('.editText').removeClass('active');
    $(this).parent().siblings('textarea').attr('readonly', true);

});
$("#close-payment").on('click', function () {
    $('#popup-create_payment').css('display', 'none');
});
$("#popup-create_payment .top-text span").on('click', function () {
    $('#new_payment_sum').val('');
    $('#popup-create_payment textarea').val('');
    $('#popup-create_payment').css('display', '');
});
$('#payment-form').on("submit", function (event) {
    event.preventDefault();
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

        });
    }
    // create_payment(id, sum, description, rate, currency);

    $('#new_payment_sum').val('');
    $('#popup-create_payment textarea').val('');
    $('#popup-create_payment').css('display', 'none');
});

$("#create_new_payment").on('click', function () {
    $('#popup-create_payment').css('display', 'block');
});
$("#change-password").on('click', function () {
    $('#popup-change_password').css('display', 'block');
});
$("#close-password").on('click', function () {
    $('#popup-change_password').css('display', 'none');
});
$('#change-password-form').on('submit', function (event) {
    event.preventDefault();
    let data = $('#change-password-form').serializeArray();
    let new_data = {};
    data.forEach(function (field) {
        new_data[field.name] = field.value
    });
    $('.password-error').html('');
    ajaxRequest(`${CONFIG.DOCUMENT_ROOT}rest-auth/password/change/`, JSON.stringify(new_data), function (JSONobj) {
        window.location.href = `/entry/?next=${window.location.pathname}`;
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            for (let field in data) {
                if (!data.hasOwnProperty(field)) continue;
                $(`#error-${field}`).html(data[field]);
            }
        },
        403: function (data) {
            data = data.responseJSON;
            for (let field in data) {
                if (!data.hasOwnProperty(field)) continue;
                $(`#error-${field}`).html(data[field]);
            }
        }
    });
});
$("#popup-change_password .top-text span").on('click', function (el) {
    $('#popup-change_password').css('display', 'none');
});

$("#close-deal").on('click', function () {
    $('#popup-create_deal').css('display', 'none');
});
$("#popup-create_deal .top-text span").on('click', function (el) {
    $('#new_deal_sum').val('');
    $('#popup-create_deal textarea').val('');
    $('#popup-create_deal').css('display', '');
});
$("#create_new_deal").on('click', function () {
    $('#popup-create_deal').css('display', 'block');
});

$('#send_new_deal').on('click', function () {
    let description = $('#popup-create_deal textarea').val();
    let value = $('#new_deal_sum').val();
    let date = $('#new_deal_date').val();

    if (description && value && date) {
        let url = URLS.deal.list();

        let deal = JSON.stringify({
            'date_created': date.trim().split('.').reverse().join('-'),
            'value': value,
            'description': description,
            'partnership': $(this).data('partner')
        });
        ajaxRequest(url, deal, function (data) {
            showPopup('Сделка создана.');
            $('#popup-create_deal textarea').val('');
            $('#new_deal_sum').val('');
            $('#new_deal_date').val('');
            $('#popup-create_deal').css('display', 'none');

        }, 'POST', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showPopup(data.detail)
            }
        });
    } else {
        showPopup('Заполните все поля.');
    }
});

$("#tabs1 li").click();

$("#id_deal_date").datepicker({
    dateFormat: "yy-mm-dd",
    maxDate: new Date(),
    yearRange: '2010:+0',
    autoClose: true,
    onSelect: function (date) {
    }
}).mousedown(function () {
    $('#ui-datepicker-div').toggle();
});
$('#partnershipCheck').on('click', function () {
    let $input = $(this).closest('form').find('input:not([checkbox])');
    if ($(this).is(':checked')) {
        $input.each(function () {
            $(this).attr('readonly', false)
        });
    } else {
        $input.each(function () {
            $(this).attr('readonly', true)
        });
    }
});
$(".send_note").on('click', function (e) {
    e.preventDefault();
    let form = $(this).closest('form');
    let text_field = form.find('.js-add_note');
    let box = $(this).closest(".note-box");
    let text = text_field.val();
    let anket_id = form.data('anket-id');
    sendNote(anket_id, text, box);
    text_field.val('');
});

$(".js-lesson").on('click', function (e) {
    let lesson_id = $(this).data("lesson-id");
    let anket_id = $(this).data('anket-id');
    let checked = $(this).is(':checked');
    changeLessonStatus(lesson_id, anket_id, checked);
});

$("#tabs2 li").on('click', function (e) {
    e.preventDefault();
    let id_tab = this.getAttribute('data-tab');
    $('[data-summit-id]').hide();
    $('[data-summit-id="' + id_tab + '"]').show();
    $('.summits-block').hide();
    $(this).closest('.tab-status').find('li').removeClass('active');
    $(this).addClass('active');
});

if ($("#tabs2 li")) {
    $('#Sammits').css('display', 'block');
} else {
    $('#Sammits').css('display', 'block');
}

$('#deleteUser').click(function () {
    let id = $(this).attr('data-id');
    $('#yes').attr('data-id', ID);
    $('.add-user-wrap').show();
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

$('#deletePopup span').click(function () {
    $('#deletePopup').hide();
});

function create_payment(partnerId, sum, description, rate, currency) {
    let data = {
        "sum": sum,
        "description": description,
        "rate": rate,
        "currency": currency
    };

    let json = JSON.stringify(data);

    ajaxRequest(URLS.partner.create_payment(partnerId), json, function (JSONobj) {
        showPopup('Оплата прошла успешно.');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail)
        }
    });
}

function sendNote(profileId, text, box) {
    let data = {
        "text": text
    };
    let json = JSON.stringify(data);
    ajaxRequest(URLS.summit_profile.create_note(profileId), json, function (note) {
        box.before(function () {
            return '<div class="rows"><div><p>' + note.text + ' — ' + moment(note.date_created).format("DD.MM.YYYY HH:mm:ss")
                + ' — Author: ' + note.owner_name
                + '</p></div></div>'
        });
        showPopup('Примечание добавлено');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function changeLessonStatus(lessonId, profileId, checked) {
    let data = {
        "anket_id": profileId
    };
    let url;
    if (checked) {
        url = URLS.summit_lesson.add_viewer(lessonId);
    } else {
        url = URLS.summit_lesson.del_viewer(lessonId);
    }
    let json = JSON.stringify(data);
    ajaxRequest(url, json, function (data) {
        if (data.checked) {
            showPopup('Урок ' + data.lesson + ' просмотрен.');
        } else {
            showPopup('Урок ' + data.lesson + ' не просмотрен.');
        }
        $('#lesson' + data.lesson_id).prop('checked', data.checked);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showPopup(data.detail);
            $('#lesson' + data.lesson_id).prop('checked', data.checked);
        }
    });
}

(function ($) {
    let $img = $(".crArea img");
    let flagCroppImg = false;

    let $selectDepartment = $('#departments');

    function makeHomeGroupsList(ID) {
        let churchID = ID || $('#church_list').val();
        if (churchID && typeof parseInt(churchID) == "number") {
            return getHomeGroupsINChurches(churchID)
        }
        return new Promise(function (reject) {
            reject(null);
        })
    }

    // makeHomeGroupsList().then((results) => {
    //     if (!results) {
    //         return null
    //     }
    //     let $homeGroupsList = $('#home_groups_list');
    //     let homeGroupsID = $homeGroupsList.val();
    //     console.log(homeGroupsID);
    //     let options = [];
    //     let option = document.createElement('option');
    //     $(option).val('').text('Выберите домашнюю группу').attr('selected', true);
    //     options.push(option);
    //     results.forEach(function (item) {
    //         let option = document.createElement('option');
    //         $(option).val(item.id).text(item.get_title);
    //         if (homeGroupsID == item.id) {
    //             console.log(homeGroupsID == item.id);
    //             $(option).attr('selected', true);
    //             console.log(option);
    //         }
    //         options.push(option);
    //     });
    //     console.log(options);
    //     $homeGroupsList.html(options);
    // });

    function makeChurches() {
        let departmentID = $selectDepartment.val();
        if (departmentID && typeof parseInt(departmentID) == "number") {
            getChurchesListINDepartament(departmentID).then(function (data) {
                console.log(departmentID);
                let selectedChurchID = $('#church_list').val();
                let options = [];
                let option = document.createElement('option');
                $(option).val('').text('Выберите церковь').attr('selected', true).attr('disabled', true);
                options.push(option);
                data.forEach(function (item) {
                    let option = document.createElement('option');
                    $(option).val(item.id).text(item.get_title);
                    if (selectedChurchID == item.id) {
                        $(option).attr('selected', true);
                    }
                    options.push(option);
                });
                $('#church_list').html(options).on('change', function () {
                    let churchID = $(this).val();
                    if (churchID && typeof parseInt(churchID) == "number") {
                        makeHomeGroupsList(churchID).then(function (data) {
                            let $homeGroupsList = $('#home_groups_list');
                            let homeGroupsID = $homeGroupsList.val();
                            let options = [];
                            let option = document.createElement('option');
                            $(option).val('').text('Выберите домашнюю группу').attr('selected', true);
                            options.push(option);
                            data.forEach(function (item) {
                                let option = document.createElement('option');
                                $(option).val(item.id).text(item.get_title);
                                if (homeGroupsID == item.id) {
                                    $(option).attr('selected', true);
                                }
                                options.push(option);
                            });
                            $homeGroupsList.html(options);
                        });
                    }
                }).trigger('change');
            });
        }
    }

    $selectDepartment.on('change', function () {
        let option = document.createElement('option');
        $(option).val('').text('Выберите церковь').attr('selected', true);
        makeChurches();
        $('#home_groups_list').html(option);
    });
    makeChurches();
    $('.edit').on('click', function (e) {
        e.preventDefault();
        let $edit = $('.edit');
        let exists = $edit.closest('form').find('ul').hasClass('exists');
        if (!exists) {
            console.log(exists);
        }
        let noEdit = false;
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
                showPopup("Сначала сохраните или отмените изменения в другом блоке")
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
    $('.save__info').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').find('.edit').removeClass('active');
        let _self = this;
        let $block = $(this).closest('.right-info__block');
        let $input = $block.find('input:not(.select2-search__field), select');
        let thisForm = $(this).closest('form');
        let success = $(this).closest('.right-info__block').find('.success__block');
        let formName = thisForm.attr('name');
        let action = thisForm.data('action');
        let form = document.forms[formName];
        let formData = new FormData(form);
        let hidden = $(this).hasClass('after__hidden');
        if (action == 'update-user') {
            if ($input.is(':checkbox')) {
                let partnerData = {};
                if ($input.is(':checked')) {
                    partnerData.is_active = true;
                } else {
                    partnerData.is_active = false;
                }
                let $newInput = $input.filter(":not(':checkbox')");
                $newInput.each(function () {
                    let id = $(this).data('id');
                    if ($(this).hasClass('sel__date')) {
                        partnerData[id] = $(this).val().trim().split('.').reverse().join('-');
                    } else {
                        partnerData[id] = $(this).val();
                    }
                });
                formData.append('partner', JSON.stringify(partnerData));
            } else {
                $input.each(function () {
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
                                if ($val.hasClass('sel__date')) {
                                    if ($val.val() == "Не покаялся") {
                                        formData.append(id, "");
                                    } else {
                                        formData.append(id, $('#' + id).val().trim().split('.').reverse().join('-'));
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
            }
            updateUser(ID, formData, success).then(function (data) {
                if (formName === 'editHierarchy') {
                    $('.is-hidden__after-edit').html('');
                }
                if (hidden) {
                    let editBtn = $(_self).closest('.hidden').data('edit');
                    setTimeout(function () {
                        $('#' + editBtn).trigger('click');
                    }, 1500)
                }
                $('#fullName').text(data.fullname);
                $('#searchName').text(data.search_name);
            }).catch(function (data) {
                console.log(data);
            });
        } else if (action == 'update-church') {
            let $existBlock = $('#editChurches').find('ul');
            let noExist = $existBlock.hasClass('exists');
            let church_id = $('#church_list').val();
            let home_groups_id = $('#home_groups_list').val();
            if (!!home_groups_id) {
                addUserToHomeGroup(ID, home_groups_id, noExist).then(function (data) {
                    let success = $(_self).closest('.right-info__block').find('.success__block');
                    $(success).text('Сохранено');
                    setTimeout(function () {
                        $(success).text('');
                        $('.no_church_in').text('');
                    }, 3000);
                    $existBlock.addClass('exists');
                }).catch(function (data) {
                    showPopup(JSON.parse(data.responseText));
                });
            } else if (!!church_id) {
                addUserToChurch(ID, church_id, noExist).then(function (data) {
                    let success = $(_self).closest('.right-info__block').find('.success__block');
                    $(success).text('Сохранено');
                    setTimeout(function () {
                        $(success).text('');
                        $('.no_church_in').text('');
                    }, 3000);
                    $existBlock.addClass('exists');
                }).catch(function (data) {
                    showPopup(JSON.parse(data.responseText));
                });
            }

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
    });

    $.validate({
        lang: 'ru',
        form: '#editContactForm',
        modules: 'toggleDisabled',
    });

    initLocationSelect({
        country: 'selectCountry',
        region: 'selectRegion',
        city: 'selectCity'
    });
    $('.datepicker-here').datepicker({
        autoClose: true
    });
    $('#departments').on('change', function () {
        let status = $('#selectHierarchy').find('option:selected').data('level');
        let department = $(this).val();
        makeResponsibleList(department, status);
    });
    // after fix
    makeResponsibleList($('#departments').val(), $('#selectHierarchy').find('option:selected').data('level'));
    $('#selectHierarchy').on('change', function () {
        let department = $('#departments').val();
        let status = $(this).find('option:selected').data('level');
        makeResponsibleList(department, status, true);
    });
    $('.sel__date').each(function () {
        let $el = $(this);
        let date = ($el.val() && $el.val() != 'Не покаялся') ? new Date($el.val().split('.').reverse().join(', ')) : new Date();
        $el.datepicker({
            autoClose: true,
            startDate: date,
            dateFormat: 'dd.mm.yyyy'
        })
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

    $('#file').on('change', handleFileSelect);

    $('#editCropImg').on('click', function () {
        let imgUrl;
        imgUrl = $img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
        $('.anketa-photo').html('<img src="' + imgUrl + '" />');
        $('#impPopup').fadeOut(300, function () {
            $img.cropper("destroy");
        });

        if (flagCroppImg && !$('#editNameBtn').hasClass('active')) {
            let form = document.forms['editName'];
            let formData = new FormData(form);
            let blob;
            blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
            formData.append('image', blob, 'logo.jpg');
            formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
            // formData.append('id', id);
            updateUser(ID, formData);
        }
        return flagCroppImg = false;
    });

    $('#impPopup').find('.close').on('click', function () {
        $('#impPopup').fadeOut(300, function () {
            $img.cropper("destroy");
        });
    });

    function handleFileSelect(e) {
        let files = e.target.files; // FileList object
        // Loop through the FileList and render image files as thumbnails.
        for (let i = 0, file; file = files[i]; i++) {
            // Only process image files.
            if (!file.type.match('image.*')) {
                continue;
            }
            let reader = new FileReader();

            // Closure to capture the file information.
            reader.onload = (function () {
                return function (e) {
                    $img.attr('src', e.target.result);
                    $("#impPopup").css('display', 'block');
                    $img.cropper({
                        aspectRatio: 1 / 1,
                        built: function () {
                            $img.cropper("setCropBoxData", {width: "100", height: "100"});
                        }
                    });
                };
            })();
            // Read in the image file as a data URL.
            reader.readAsDataURL(file);
        }
        croppUploadImg();
    }

    function croppUploadImg() {
        $('.anketa-photo').on('click', function () {

            $("#impPopup").css('display', 'block');
            $img.cropper({
                aspectRatio: 1 / 1,
                built: function () {
                    $img.cropper("setCropBoxData", {width: "100", height: "100"});
                }
            });
            return flagCroppImg = true;
        });
    }

    $('#divisions').select2();
    $('#departments').select2();
    $('#sent_date').datepicker({
        autoClose: true,
        dateFormat: 'dd.mm.yyyy'
    });

    $('.summits-title').on('click', function () {
        $(this).next('.summits-block').siblings('.summits-block').slideUp(300);
        $(this).next('.summits-block').slideToggle();
    });

    $('.summits-block .rows-tabs').on('click', 'p', function () {
        let tab = $(this).parent().data('tabs-id');
        $(this).closest('.rows-tabs').find('div').removeClass('active');
        $(this).parent().addClass('active');
        $(this).closest('.summits-block').find('.wrapp').hide();
        $(this).closest('.summits-block').find(`.wrapp-${tab}`).show();
    });

    $('.a-note, .a-sdelki').find('.editText').on('click', function () {
        $(this).toggleClass('active');
        let textArea = $(this).parent().siblings('textarea');
        if ($(this).hasClass('active')) {
            textArea.attr('readonly', false);
        } else {
            textArea.attr('readonly', true);
        }
    });
    // $('label[for="master"]').on('click', function () {
    //     let id = $('#selectResponsible').find('option:selected').val();
    //     if(id) {
    //         window.location.href = `/account/${id}`;
    //     }
    // })
})
(jQuery);