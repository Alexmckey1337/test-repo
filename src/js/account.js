function updateUser(id, data, success = null) {
    let url = `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/${id}/`;
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
        let errObj = JSON.parse(data);
        let msg = "";
        for (let key in errObj) {
            msg += key;
            msg += ': ';
            errObj[key].forEach(function (item) {
                msg += item;
                msg += ' ';
            });
            msg += '; ';
        }
        showPopup(msg);
    });
}

function makeResponsibleList(department, status) {
    let $selectResponsible = $('#selectResponsible');
    let activeMaster = $selectResponsible.val();
    getResponsible(department, status).then(function (data) {
        let rendered = [];
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

$('.b-red').on('click', function () {
    window.location.href = `/account_edit/${ID}/`;
});
$('.hard-login').on('click', function () {
    let user = $(this).data('user-id');
    setCookie('hard_user_id', user, {path: '/'});
    window.location.reload();
});
$("#tabs1 li").on('click', function () {
    let id_tab = $(this).attr('data-tab');
    $('[data-tab-content]').hide();
    $('[data-tab-content="' + id_tab + '"]').show();
});

$('#send_need').on('click', function () {
    let need_text = $('#id_need_text').val();
    let url = CONFIG.DOCUMENT_ROOT + `api/v1.1/partnerships/${$(this).data('partner')}/update_need/`;
    let need = JSON.stringify({'need_text': need_text});
    ajaxRequest(url, need, function () {
        showPopup('Нужда сохранена.');
    }, 'PUT', true, {
        'Content-Type': 'application/json'
    })
});
$('#sendNote').on('click', function () {
    let _self = this;
    let id = $(_self).data('id');
    let resData = new FormData();
    resData.append('description', $('#id_note_text').val());
    updateUser(id, resData);
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
        let url = CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/';

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
$("#send_note").on('click', function (e) {
    e.preventDefault();
    let box = $(this).closest(".note-box");
    let text_field = box.find('.js-add_note');
    let text = text_field.val();
    let anket_id = text_field.data('anket-id');
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

$('#yes').click(function () {
    let id = $(this).attr('data-id');
    deleteUser(id);
    $('#deletePopup').hide();
});

function deleteUser(id) {
    let data = {
        "id": id
    };
    let json = JSON.stringify(data);
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/delete_user/', json, function (JSONobj) {
        if (JSONobj.status) {
            showPopup('Пользователь успешно удален');
            window.location.href = "/"
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function create_payment(id, sum, description, rate, currency) {
    let data = {
        "sum": sum,
        "description": description,
        "rate": rate,
        "currency": currency
    };

    let json = JSON.stringify(data);

    ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.1/partnerships/${id}/create_payment/`, json, function (JSONobj) {
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

function sendNote(anket_id, text, box) {
    let data = {
        "text": text
    };
    let summit_type = box.data('summit-id');
    let json = JSON.stringify(data);
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/' + anket_id + '/create_note/', json, function (note) {
        box.before(function () {
            return '<div class="rows" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 6px;"><p>' + note.text + ' — ' + moment(note.date_created).format("DD.MM.YYYY HH:mm:ss")
                + ' — Author: ' + note.owner_name
                + '</p></div></div>'
        });
        showPopup('Примечание добавлено');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function changeLessonStatus(lesson_id, anket_id, checked) {
    let data = {
        "anket_id": anket_id
    };
    let url;
    if (checked) {
        url = CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_lessons/' + lesson_id + '/add_viewer/';
    } else {
        url = CONFIG.DOCUMENT_ROOT + 'api/v1.0/summit_lessons/' + lesson_id + '/del_viewer/';
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
            showPopup(data.message);
            $('#lesson' + data.lesson_id).prop('checked', data.checked);
        }
    });
}

(function ($) {
    let $img = $(".crArea img");

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

    makeHomeGroupsList().then(function (data) {
        if (!results) {
            return null
        }
        let homeGroupsID = $('#home_groups_list').val();
        let results = data.results;
        let options = [];
        let option = document.createElement('option');
        $(option).val('').text('Выберите домашнюю группу').attr('selected', true).attr('disabled', true);
        options.push(option);
        results.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.get_title);
            if (homeGroupsID == item.id) {
                $(option).attr('selected', true);
            }
            options.push(option);
        });
        $('#home_groups_list').html(options);
    });

    function makeChurches() {
        let departmentID = $selectDepartment.val();
        if (departmentID && typeof parseInt(departmentID) == "number") {
            getChurchesINDepartament(departmentID).then(function (data) {
                let selectedChurchID = $(church_list).val();
                let results = data.results;
                let options = [];
                let option = document.createElement('option');
                $(option).val('').text('Выберите домашнюю группу').attr('selected', true).attr('disabled', true);
                options.push(option);
                results.forEach(function (item) {
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
                            let options = [];
                            let option = document.createElement('option');
                            $(option).val('').text('Выберите домашнюю группу').attr('selected', true).attr('disabled', true);
                            options.push(option);
                            data.forEach(function (item) {
                                let option = document.createElement('option');
                                $(option).val(item.id).text(item.get_title);
                                options.push(option);
                            });
                            $('#home_groups_list').html(options);
                        });
                    }
                });
            });
        }
    }

    $selectDepartment.on('change', function () {
        let option = document.createElement('option');
        $(option).val('').text('Выберите домашнюю группу').attr('selected', true);
        makeChurches();
        $('#home_groups_list').html(option);
    });
    makeChurches();
    $('.edit').on('click', function (e) {
        e.preventDefault();
        let $edit = $('.edit');
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
                                    formData.append('image', blob);
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
                if (hidden) {
                    let editBtn = $(_self).closest('.hidden').data('edit');
                    setTimeout(function () {
                        $('#' + editBtn).trigger('click');
                    }, 1500)
                }
                $('#fullName').text(data.fullname);
                $('#searchName').text(data.search_name);
            });
        } else if (action == 'update-church') {
            let $existBlock = $('#editChurches').find('ul');
            let exist = $existBlock.hasClass('exists');
            let church_id = $('#church_list').val();
            let home_groups_id = $('#home_groups_list').val();
            if (!!home_groups_id) {
                addUserToHomeGroup(ID, home_groups_id, exist).then(function (data) {
                    let success = $(_self).closest('.right-info__block').find('.success__block');
                    $(success).text('Сохранено');
                    setTimeout(function () {
                        $(success).text('');
                        $('.no_church_in').text('');
                    }, 3000);
                }).catch(function (data) {
                    showPopup(JSON.parse(data.responseText));
                });
            } else if (!!church_id) {
                addUserToChurch(ID, church_id, exist).then(function (data) {
                    let success = $(_self).closest('.right-info__block').find('.success__block');
                    $(success).text('Сохранено');
                    setTimeout(function () {
                        $(success).text('');
                        $('.no_church_in').text('');
                    }, 3000);
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

    initLocationSelect({
        country: 'selectCountry',
        region: 'selectRegion',
        city: 'selectCity'
    });
    $('.datepicker-here').datepicker({
        autoClose: true
    });
    $('#departments').on('change', function () {
        let status = $('#selectHierarchy').val();
        let department = $(this).val();
        makeResponsibleList(department, status);
    });
    // after fix
    makeResponsibleList($('#departments').val(), $('#selectHierarchy').val());
    $('#selectHierarchy').on('change', function () {
        let department = $('#selectDepartment').val();
        let status = $(this).val();
        makeResponsibleList(department, status);
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
        imgUrl = $img.cropper('crop').cropper('getCroppedCanvas').toDataURL('image/jpeg');
        $('#impPopup').fadeOut();
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
        $('.anketa-photo').html('<img src="' + imgUrl + '" />');
        $img.cropper("destroy");
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
    }

    $('#divisions').select2();
    $('#departments').select2();
    $('#sent_date').datepicker({
        autoClose: true,
        dateFormat: 'dd.mm.yyyy'
    })
})
(jQuery);