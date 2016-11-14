$(document).ready(function () {
    init();
    getUserDeals();
    getUserSummitInfo();

    $('#deleteUser').click(function () {
        var id = $(this).attr('data-id');
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

    $('#deletePopup .top-text span').click(function () {
        $('#deletePopup').hide();
    });

    $('#yes').click(function () {
        var id = $(this).attr('data-id');
        deleteUser(id);
        $('#deletePopup').hide();
    });

});


function init(id) {
    var id = parseInt(id || getLastId());


    if (!id) {
        return
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/users/' + id + '/', null, function (data) {
        var date = data.fields.coming_date.value.replace(/\-/g, '.');

        if (data.image) {
            document.querySelector(".anketa-photo img").src = data.image
        }
        if (!data.fields) {
            return
        }
        if (data.fields.coming_date.value) {
            document.getElementById('coming_date').innerHTML = date;
            console.log(date);
        }
        $('#deleteUser').attr('data-id', data.id);
        var fullname;
        var social = data.fields.social;
        var repentance_date = data.fields.repentance_date;


        var status = repentance_date.value ? '<span class="green1">Покаялся: ' + repentance_date.value.replace(/\-/g, '.') + '</span>' : '<span class="reds">Не покаялся</span>';

        document.getElementById('repentance_status').innerHTML = status;

        var main_phone = data.fields.phone_number.value;
        var additional_phone = data.fields.additional_phone.value;
        var phone = main_phone;
        if (additional_phone) {
            phone = phone + ', ' + additional_phone;
        }
        document.getElementById('phone_number').innerHTML = phone || ' ';

        for (var prop in data.fields) {
            if (!data.fields.hasOwnProperty(prop)) continue;

            if (prop == 'social') {


                for (var soc in social) {


                    if (soc == 'skype') {
                        document.getElementById('skype').innerHTML = social[soc];
                        continue
                    }


                    if (document.querySelector("[data-soc = '" + soc + "']")) {
                        if (social[soc]) {
                            document.querySelector("[data-soc = '" + soc + "']").setAttribute('data-href', social[soc])
                        }

                    }
                }


                continue
            }

            if (prop == 'fullname') {

                fullname = data.fields[prop]['value'].split(' ');

                if (document.getElementById(prop)) {
                    document.getElementById(prop).innerHTML = fullname[0] + '<br>' + fullname[1] + ' ' + fullname[2]
                }


                continue
            }
            if (prop == 'divisions') {
                var divisions = data.fields[prop]['value'].split(',').join(', ');
                document.getElementById(prop).innerHTML = divisions;
                continue
            }
            if (prop == 'additional_phone' || prop == 'phone_number') {
                continue
            }

            if (document.getElementById(prop)) {
                document.getElementById(prop).innerHTML = data.fields[prop]['value'] || ' '
            }


        }

        Array.prototype.forEach.call(document.querySelectorAll(".a-socials"), function (el) {
            el.addEventListener('click', function () {
                var href = this.getAttribute('data-href');
                if (href) {
                    window.location = href
                }

            });
        });


        document.getElementsByClassName('b-red')[0].addEventListener('click', function () {
            window.location.href = '/account_edit/' + id + '/'
        })

    })
}


function getUserDeals() {
    var id = parseInt(id || getLastId());
    if (!id) {
        return
    }
    var url = config.DOCUMENT_ROOT + 'api/v1.0/partnerships/?user=' + id;

    ajaxRequest(url, null, function (data) {
            data = data.results[0];

            document.getElementById('parntership_info').style.display = 'block';

            if (!data) {
                document.getElementsByClassName('tab-status')[0].innerHTML = 'На данном пользователе нету сделок';
                document.getElementsByClassName('a-sdelki')[0].style.display = 'none';
                document.getElementById('parntership_info').style.display = 'none';
                return;
            }

            document.getElementById('id_need_text').value = data.need_text;
            var deal_fields = data.deal_fields,
                responsible = data.responsible,
                date = data.date.replace(/\-/g, '.');



            document.getElementById('incomplete-count').innerHTML = parseInt(data.undone_deals_count) || "0";
            document.getElementById('overdue-count').innerHTML = parseInt(data.expired_deals_count) || "0";
            document.getElementById('completed-count').innerHTML = parseInt(data.done_deals_count) || "0";

            document.getElementById('responsible').innerHTML = responsible;
            document.getElementById('partner_val').innerHTML = data.value;
            document.getElementById('coming_date_').innerHTML = date;


            if (!deal_fields || deal_fields.length == 0) {
                // document.getElementById('partner_table').innerHTML = '' //'Нету deal_fields';
                document.getElementsByClassName('tab-status')[0].innerHTML = 'На данном пользователе нету сделок';
                document.getElementsByClassName('a-sdelki')[0].style.display = 'none';
                document.getElementById('parntership_info').style.display = 'none';
                return ''
            }

            document.getElementsByClassName('a-sdelki')[0].style.display = 'block';


            Array.prototype.forEach.call(document.querySelectorAll("#tabs1 li"), function (el) {
                el.addEventListener('click', function () {
                    var id_tab = this.getAttribute('data-tab');
                    $('[data-tab-content]').hide();
                    $('[data-tab-content="' + id_tab + '"]').show();

                });
            });

            $('#send_need').on('click', function (el) {
                var need_text = document.getElementById('id_need_text').value;
                var url = config.DOCUMENT_ROOT + 'api/v1.1/partnerships/' + data.id + '/update_need/';
                var need = JSON.stringify({'need_text': need_text});
                ajaxRequest(url, need, function (data) {
                    showPopup('Нужда сохранена.');

                }, 'PUT', true, {
                    'Content-Type': 'application/json'
                })
            });

            $('#send_new_deal').on('click', function (el) {
                var description = document.getElementById('id_deal_description').value;
                var value = document.getElementById('id_deal_value').value;
                var date = document.getElementById('id_deal_date').value;

                if (description && value && date) {
                    var url = config.DOCUMENT_ROOT + 'api/v1.0/deals/';

                    var deal = JSON.stringify({
                        'date': date,
                        'date_created': date,
                        'value': value,
                        'description': description,
                        'done': true,
                        'partnership': data.id
                    });
                    ajaxRequest(url, deal, function (data) {
                        showPopup('Сделка создана.');

                        document.getElementById('id_deal_description').value = '';
                        document.getElementById('id_deal_value').value = '';
                        document.getElementById('id_deal_date').value = '';

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


            var done_deals = '';
            var expired_deals = '';
            var undone_deals = '';
            for (var i = 0; i < deal_fields.length; i++) {
                //console.log(  deal_fields[i].status )

                switch (deal_fields[i].status.value) {
                    case   'done':
                        //console.log('done');
                        done_deals += '<div class="rows"><div class="col">' +
                            '<p><span>' + deal_fields[i].fullname.value + '</span></p>' +
                            '</div><div class="col">' +
                            '<p>Последняя сделка:<span>' + deal_fields[i].date.value + '</span></p>' +
                            '<p>Сумма<span>' + deal_fields[i].value.value + '₴</span></p></div></div>';
                        break;
                    case  'expired' :
                        expired_deals += '<div class="rows"><div class="col">' +
                            '<p><span>' + deal_fields[i].fullname.value + '</span></p>' +
                            '</div><div class="col">' +
                            '<p>Последняя сделка:<span>' + deal_fields[i].date.value + '</span></p>' +
                            '<p>Сумма<span>' + deal_fields[i].value.value + '₴</span></p></div></div>';
                        break;
                    case 'undone':
                        undone_deals += '<div class="rows"><div class="col">' +
                            '<p><span>' + deal_fields[i].fullname.value + '</span></p>' +
                            '</div><div class="col">' +
                            '<p>Последняя сделка:<span>' + deal_fields[i].date.value + '</span></p>' +
                            '<p>Сумма<span>' + deal_fields[i].value.value + '₴</span></p></div></div>';
                        break;
                    default :
                        break;
                }


            }

            document.querySelector('[data-tab-content="3"]').innerHTML = done_deals;
            document.querySelector('[data-tab-content="2"]').innerHTML = expired_deals;
            document.querySelector('[data-tab-content="1"]').innerHTML = undone_deals;

            document.querySelector("#tabs1 li").click()

            $("#id_deal_date").datepicker({
                dateFormat: "yy-mm-dd",
                maxDate: new Date(),
                yearRange: '2010:+0',
                onSelect: function (date) {

                }
            }).mousedown(function () {
                $('#ui-datepicker-div').toggle();
            });

        }, 'GET', true, {'Content-Type': 'application/json'},
        {
            403: function (data) {
                document.getElementsByClassName('tab-status')[0].innerHTML = 'На данном пользователе нету сделок';
                document.getElementsByClassName('a-sdelki')[0].style.display = 'none';
                document.getElementById('parntership_info').style.display = 'none';
            }
        })
}

function deleteUser(id) {
    var data = {
        "id": id
    };
    var json = JSON.stringify(data);
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
    var data = {
        "text": text
    };
    var summit_type = box.data('summit-id');
    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/' + anket_id + '/create_note/', json, function (note) {
        box.before(function () {
            return '<div class="rows" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 6px;"><p>' + note.text + ' — ' + note.date_created
                + ' — Author: ' + note.owner_name
                + '</p></div></div>'
        });
        showPopup('Примечание добавлено');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function changeLessonStatus(lesson_id, anket_id, checked) {
    var data = {
        "anket_id": anket_id
    };
    var url;
    if (checked) {
        url = config.DOCUMENT_ROOT + 'api/v1.0/summit_lessons/' + lesson_id + '/add_viewer/';
    } else {
        url = config.DOCUMENT_ROOT + 'api/v1.0/summit_lessons/' + lesson_id + '/del_viewer/';
    }
    var json = JSON.stringify(data);
    ajaxRequest(url, json, function (data) {
        if (data.checked) {
            showPopup('Урок ' + data.lesson + ' просмотрен.');
        } else {
            showPopup('Урок ' + data.lesson + ' не просмотрен.');
        }
        $('#lesson' + data.lesson_id).prop('checked', data.checked);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}


function getUserSummitInfo() {


    var id = parseInt(id || getLastId());
    if (!id) {
        return
    }
    var url = config.DOCUMENT_ROOT + 'api/v1.0/users/' + id + '/summit_info/';

    ajaxRequest(url, null, function (results) {
        if (!results.length) {
            document.getElementsByClassName('a-sammits')[0].style.display = 'none';
            return
        }

        var tab_title = [];
        var menu_summit = '';
        var body_summit = '';

        results.forEach(function (summit_type) {
            tab_title.push(summit_type.id);
            menu_summit += '<li data-tab=' + summit_type.id + '><a href="#" >' + summit_type.name + '</a></li>';
            summit_type.summits.forEach(function (summit) {
                body_summit += '<div class="rows" data-summit-id = "' + summit_type.id + '" style="border-bottom: 2px solid #000"><div class="col"><p>' + summit.name + '</p> </div><div class="col">';
                if (summit.description != "") {
                    body_summit += '<p>' + summit.description + '</p>';
                } else {
                    body_summit += '<p>Комментарий не указан</p>';
                }

                body_summit += '<p>Сумма<span> ' + summit.value + ' ₴</span></p>' +
                    '</div></div>';

                // NOTES
                body_summit += '<div class="rows" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 15px;"><p>Примечания</p></div></div>';
                summit.notes.forEach(function (note) {
                    body_summit += '<div class="rows" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 6px;"><p>' + note.text + ' — ' + note.date_created
                        + ' — Author: ' + note.owner_name
                        + '</p></div></div>';
                });

                body_summit += '<div class="rows note-box" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 15px;">' +
                    '<p>Написать примечание</p><p><textarea name="add_note" data-anket-id="' + summit.anket_id + '" class="js-add_note" cols="30" rows="10"></textarea></p>' +
                    '<p><button id="send_note">Отправить примечание</button></p></div></div>';

                // LESSONS
                if (summit.lessons.length) {
                    body_summit += '<div class="rows" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 15px;"><p>Уроки</p></div></div>';
                }
                summit.lessons.forEach(function (lesson) {
                    body_summit += '<div class="rows" data-summit-id = "' + summit_type.id + '" ><div style="padding:10px 6px;"><p>';
                    if (lesson.is_view) {
                        body_summit += '<input id="lesson' + lesson.id + '" class="js-lesson" type="checkbox" data-anket-id="' + summit.anket_id + '" data-lesson-id="' + lesson.id + '" checked>';
                    } else {
                        body_summit += '<input id="lesson' + lesson.id + '" class="js-lesson" type="checkbox" data-anket-id="' + summit.anket_id + '" data-lesson-id="' + lesson.id + '">';
                    }
                    body_summit += lesson.name + '</p></div></div>';
                });
            });
        });


        document.getElementsByClassName('summit_wrapper')[0].innerHTML = body_summit;
        document.getElementById('tabs2').innerHTML = menu_summit;

        Array.prototype.forEach.call(document.querySelectorAll("#send_note"), function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                var box = $(this).closest(".note-box");
                var text_field = box.find('.js-add_note');
                var text = text_field.val();
                var anket_id = text_field.data('anket-id');
                console.log(text, anket_id);
                sendNote(anket_id, text, box);
                text_field.val('');
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll(".js-lesson"), function (el) {
            el.addEventListener('click', function (e) {
                var lesson_id = $(this).data("lesson-id");
                var anket_id = $(this).data('anket-id');
                var checked = $(this).is(':checked');
                console.log(lesson_id, anket_id, checked);
                changeLessonStatus(lesson_id, anket_id, checked);
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll("#tabs2 li"), function (el) {
            el.addEventListener('click', function (e) {
                e.preventDefault();
                var id_tab = this.getAttribute('data-tab');
                $('[data-summit-id]').hide();
                $('[data-summit-id="' + id_tab + '"]').show();

            });
        });

        if (document.querySelector("#tabs2 li")) {
            document.getElementsByClassName('a-sammits')[0].style.display = 'block';
            document.querySelector("#tabs2 li").click()
        } else {
            document.getElementsByClassName('a-sammits')[0].style.display = 'none';
            return
        }
    })


}
