let id = getLastId();
    // init();
    $('.b-red').on('click', function () {
        window.location.href = `/account_edit/${id}/`;
    });
    $("#tabs1 li").on('click', function () {
        let id_tab = $(this).attr('data-tab');
        $('[data-tab-content]').hide();
        $('[data-tab-content="' + id_tab + '"]').show();
    });

    $('#send_need').on('click', function (el) {
        let need_text = $('#id_need_text').val();
        let url = config.DOCUMENT_ROOT + `api/v1.1/partnerships/${$(this).data('partner')}/update_need/`;
        let need = JSON.stringify({'need_text': need_text});
        ajaxRequest(url, need, function (data) {
            showPopup('Нужда сохранена.');

        }, 'PUT', true, {
            'Content-Type': 'application/json'
        })
    });

    $('#send_new_deal').on('click', function (el) {
        let description = $('#id_deal_description').val();
        let value = $('#id_deal_value').val();
        let date = $('#id_deal_date').val();

        if (description && value && date) {
            let url = config.DOCUMENT_ROOT + 'api/v1.0/deals/';

            let deal = JSON.stringify({
                'date': date,
                'date_created': date,
                'value': value,
                'description': description,
                'done': true,
                'partnership': $(this).data('partner')
            });
            ajaxRequest(url, deal, function (data) {
                showPopup('Сделка создана.');

                $('#id_deal_description').val('');
                $('#id_deal_value').val('');
                $('#id_deal_date').val('');

            }, 'POST', true, {
                'Content-Type': 'application/json'
            }, {
                403: function (data) {
                    data = data.responseJSON;
                    showPopup(data.detail)
                }
            })
        } else {
            showPopup('Заполните все поля.');
        }
    });

    $("#tabs1 li").click();

    $("#id_deal_date").datepicker({
        dateFormat: "yy-mm-dd",
        maxDate: new Date(),
        yearRange: '2010:+0',
        onSelect: function (date) {
        }
    }).mousedown(function () {
        $('#ui-datepicker-div').toggle();
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
        $('#yes').attr('data-id', id);
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
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/delete_user/', json, function (JSONobj) {
        if (JSONobj.status) {
            showPopup('Пользователь успешно удален');
            window.location.href = "/"
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function sendNote(anket_id, text, box) {
    let data = {
        "text": text
    };
    let summit_type = box.data('summit-id');
    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/' + anket_id + '/create_note/', json, function (note) {
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
        url = config.DOCUMENT_ROOT + 'api/v1.0/summit_lessons/' + lesson_id + '/add_viewer/';
    } else {
        url = config.DOCUMENT_ROOT + 'api/v1.0/summit_lessons/' + lesson_id + '/del_viewer/';
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
