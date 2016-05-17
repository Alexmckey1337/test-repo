function createNewEvent(data) {

    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/create_event/', json, function(JSONobj) {
        document.querySelector("#create_general_event input").value = ''
        document.querySelector("#create_special_event input").value = ''
        $('.checkbox-wrap span').removeClass('active');
        showPopup(JSONobj.message);
        getAllEvents();
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function deleteEvent(id) {
    var data = {
        "id": id
    }
    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/delete_event/', json, function(data) {
        showPopup(data.message);
        getAllEvents();
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });

}

function createDepartment(input) {
    var data = {
        "title": input
    }
    var json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'api/create_department/', json, function(data) {
        showPopup(data.message);
        getAllDepartments();
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function updateDepartment(id, title) {
    var data = {
        "id": id,
        "title": title
    }
    var json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'api/update_department/', json, function(data) {
        showPopup(data.message);
        getAllDepartments();
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

function getAllEvents() {

    ajaxRequest(config.DOCUMENT_ROOT + 'api/events/', null, function(data) {

        var list = data.results;
        var general_events = '<ul>';
        var special_events = '<ul>'
        for (var i = 0; i < list.length; i++) {
            //Полученые события разпихаем на две колонки по календарю и дням недели....
            if (list[i].date) {

                special_events += '<li class="clearfix">' + list[i].title + '<div data-id="' +
                    list[i].id + '" class="table-button"><i class="table-edit"></i><i class="table-delete"></i></div>' +


                    '<div class="updateEvent_wrap hidden"><input type="text" placeholder="Введите название события" value="' + list[i].title + '">' +
                    '<input type="text" class="datepicker" value="' + list[i].date + '"></input>' +
                    '<a href="#" class="green-button" data-id="' + list[i].id + '" data-date="' + list[i].date +
                    '" data-day="' + list[i].day + '"    data-title="' + list[i].title + '">Сохранить</a>' +

                    '</div></li>'
            } else {
                general_events += '<li class="clearfix">' + list[i].title + '<div data-id="' +
                    list[i].id + '" class="table-button"><i class="table-edit"></i><i class="table-delete"></i></div>' +

                    '<div class="updateEvent_wrap hidden"  data-day="' + list[i].day + '"><input type="text" placeholder="Введите название события"  value="' +
                    list[i].title + '">' +

                    '<div class="checkbox-wrap">' +
                    '<ul>' +
                    '<li><span class="checkbox" data-day="1">Пн</span></li>' +
                    '<li><span class="checkbox" data-day="2">Вт</span></li>' +
                    '<li><span class="checkbox" data-day="3">Ср</span></li>' +
                    '<li><span class="checkbox" data-day="4">Чт</span></li>' +
                    '<li><span class="checkbox" data-day="5">Пт</span></li>' +
                    '<li><span class="checkbox" data-day="6">Сб</span></li>' +
                    '<li><span class="checkbox" data-day="7">Нд</span></li>' +
                    '</ul>' +
                    '</div>' +


                    '<a href="#" class="green-button" data-id="' + list[i].id + '" data-date="' + list[i].date +
                    '" data-day="' + list[i].day + '"    data-title="' + list[i].title + '">Сохранить</a>' +

                    '</div></li>'
            }
        }
        special_events += '</ul>';
        general_events += '</ul>';
        document.getElementById('special_events').innerHTML = special_events;
        document.getElementById('general_events').innerHTML = general_events;


        $(".datepicker").datepicker({
            dateFormat: "yy-mm-dd",
            onSelect: function(data) {
                this.nextElementSibling.setAttribute('data-date', data)
            }
        });


        EventsListenersInit();

    })
}
//Обработчики событий пользователя
function EventsListenersInit(){
        /*Подсветка текущего дня*/
        [].forEach.call(document.querySelectorAll("#general_events .updateEvent_wrap"), function(el) {
            var day = el.getAttribute('data-day');
            el.getElementsByClassName('checkbox')[day - 1].classList.add('active');
        });
        /*Cмена текущего дня*/
        [].forEach.call(document.querySelectorAll(' #general_events .updateEvent_wrap .checkbox-wrap span'), function(el) {
            el.addEventListener('click', function() {

                //Придумать другую логику ???
                $(this).parent().parent().find("span.checkbox").removeClass('active')
                this.classList.add('active');
                $(this).parents(".updateEvent_wrap").find(".green-button").attr('data-day', this.getAttribute('data-day'))
            });
        });
        /*Cмена название event*/
        [].forEach.call(document.querySelectorAll('.updateEvent_wrap input[placeholder]'), function(el) {
            el.addEventListener('blur', function() {
                $(this).parents(".updateEvent_wrap").find(".green-button").attr('data-title', this.value)
            })
        });
        /*Оновление event*/
        [].forEach.call(document.querySelectorAll('.updateEvent_wrap .green-button'), function(el) {
            el.addEventListener('click', function() {
                var data = {}
                data.day = parseInt(this.getAttribute('data-day'));
                //data.cyclic = false;
                data.title = this.getAttribute('data-title');
                data.date = this.getAttribute('data-date') == 'null' ? null : this.getAttribute('data-date');
                data.id = parseInt(this.getAttribute('data-id'));
                data.cyclic = false
                createNewEvent(data)
            })
        });
        /*Редактирование events*/
        [].forEach.call(document.querySelectorAll("#wrapper_event .table-edit"), function(el) {

            el.addEventListener('click', function() {
                this.parentNode.nextElementSibling.classList.toggle('hidden');
            })
        });

        /*Удаление events*/
        [].forEach.call(document.querySelectorAll("#wrapper_event .table-delete"), function(el) {

            el.addEventListener('click', function() {
                var id = this.parentNode.getAttribute('data-id');
                deleteEvent(id);
            })

        });
}
function getAllDepartments() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/departments/', null, function(data) {
        var data = data.results;
        var html = '<ul><li>Cписок существующих отделов:</li>'
        for (var i = 0; i < data.length; i++) {
            html += '<li ><span>' + data[i].title + '</span>' +

                '<div data-id="' +
                data[i].id + '" class="table-button"><i class="table-edit"></i><!--<i class="table-delete"></i>--></div>' +
                '<p class="hidden"><input  data-id="' +
                data[i].id + '" type="text" value="' + data[i].title + '" ><button value="Обновить"  data-id="' +
                data[i].id + '" class="update">Обновить</button></p></li>'
        }
        html += '</ul>';
        html += '<div>Добавить новый департамент : <p><input type="text" value="" placeholder="Название департамента" >' +
            '<button value="Добавить" class="added">Добавить</button></p></div>'
        document.getElementById('wrapper_list').innerHTML = html;

        document.querySelector("#wrapper_list button.added").addEventListener('click', function() {

            var input = this.previousElementSibling.value
            if (!input.length) {
                showPopup('введите название  департамента');
                return '';
            } else {

                createDepartment(input);


            }

        });



        //Удаление департамента ..... удаляет сразу и юзера привязаного к нему с базы

        /*
                [].forEach.call(document.querySelectorAll("#wrapper_list .table-delete"),function(el){
                    
                    el.addEventListener('click',function(){
                        var id = this.parentNode.getAttribute('data-id');
                        var data = {
                                "id": id
                            }
                        var json = JSON.stringify(data);
                        ajaxRequest(config.DOCUMENT_ROOT+'api/delete_department/', json, function(data) {
                                showPopup(data.message);
                                getAllDepartments();
                            }, 'POST', true, {
                                'Content-Type': 'application/json'
                        });

                    })
                    
                });
        */
        [].forEach.call(document.querySelectorAll("#wrapper_list .table-edit"), function(el) {
            el.addEventListener('click', function() {
                this.parentNode.nextElementSibling.classList.toggle('hidden');
            })
        });

        //Оновление департамента...

        [].forEach.call(document.querySelectorAll("#wrapper_list .update"), function(el) {
            el.addEventListener('click', function() {

                var id = this.getAttribute('data-id')

                var title = this.previousElementSibling.value;
                if (!title.length) {
                    showPopup('введите название  департамента');
                    return '';
                }

                updateDepartment(id, title)

            })
        })


    });
}

$(function() {

    //Инициализация  табов
    [].forEach.call(document.querySelectorAll('.top_block_head_left li a'), function(el) {

        el.addEventListener('click', function(e) {
            e.preventDefault();
            [].forEach.call(document.querySelectorAll('.top_block_head_left li a'), function(el) {
                el.classList.remove('active');
            });
            this.classList.add('active');
            document.getElementById('wrapper_event').style.display = 'none';
            document.getElementById('wrapper_list').style.display = 'none';
            var el = this.getAttribute('target');
            document.getElementById(el).style.display = 'block';
        })
    })
    getAllDepartments();
    getAllEvents();

    //Смена дня проведения event
    [].forEach.call(document.querySelectorAll('.checkbox-wrap span'), function(el) {
        el.addEventListener('click', function() {
            [].forEach.call(document.querySelectorAll('.checkbox-wrap span'), function(el) {
                el.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    //Инициализация календаря

    $(".datepicker").datepicker({
        dateFormat: "yy-mm-dd"
    });
    $(".datepicker").datepicker('setDate', new Date());
    $('.datepicker').datepicker('option', $.datepicker.regional["ru"]);

    //Добавить событие  
    [].forEach.call(document.getElementsByClassName('addEvent'), function(el) {

        el.addEventListener('click', function() {
            var data = {};
            //data.active = true
            if (this.getAttribute('data-cyclic') === 'regular') {
                var tittle = document.querySelector("#create_general_event input");
                if (!tittle.value.length) {
                    tittle.classList.add('emptyField');
                    showPopup('введите название  события');
                    return '';
                } else {
                    tittle.classList.remove('emptyField');
                }
                var checkboxes = document.querySelector("#create_general_event span.active");
                if (!isElementExists(checkboxes)) {
                    showPopup('выбирите день проведения события');
                    return '';
                }
                data.day = $("#create_general_event span").index(checkboxes) + 1;
                data.cyclic = true;
                data.title = tittle.value;
                data.date = null
            } else {
                var tittle = document.querySelector("#create_special_event input");
                if (!tittle.value.length) {
                    tittle.classList.add('emptyField');
                    showPopup('введите название  события');
                    return '';
                } else {
                    tittle.classList.remove('emptyField');
                }
                data.day = null;
                data.cyclic = false;
                data.title = tittle.value;
                data.date = document.getElementById('datepicker').value;
            }
            createNewEvent(data);
        })
    });
});