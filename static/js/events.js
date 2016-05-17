var ordering = {};
	//Оновление примечания и явки
	function updateVerbose() {

	    var value = this.value || !this.classList.contains('active');
	    this.classList.toggle('active');
	    var id = $(this).parents("tr").attr('data-id');
	    var verbose = this.getAttribute('data-model')
	    var data = {
	        "id": id
	    }
	    data[verbose] = value
	    var json = JSON.stringify(data);
	    ajaxRequest(config.DOCUMENT_ROOT + 'api/update_participation/', json, function() {

	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });

	}

	//Постройка Таблиц участников для события
	function viewBodyTableUsers(list) {
	    var html = ''
	    var common_titles = Object.keys(list[0]['common'])

	    for (var i = 0; i < list.length; i++) {
	        //id_ для передачи для получение анкеты и подчиненных
	        var id_ = list[i].fields.id;
	        html += '<tr data-id="' + list[i]["id"] + '">';
	        //Загрузка полей данных пользователя
	        for (var prop in list[i].fields) {
	            //Фильтрация полей 
	            if (common_titles.indexOf(prop) === -1) continue
	            if (!list[i].fields.hasOwnProperty(prop)) continue
	            var type = list[i].fields[prop]['type'];
	            var is_checked = type == 'b' ? true : false;
	            var is_edit = list[i].fields[prop]['change']
	            var verbose = list[i].fields[prop]['verbose']
	            for (var item in list[i].fields[prop]) {

	                if (item !== 'value') continue
	                if (list[i].fields[prop][item] === null) {
	                    html += '<td is_null data-model-name="' + prop + '" data-model="' + verbose + '">&nbsp;</td>'
	                } else {

	                    if (is_checked) {
	                        var is_active = list[i].fields[prop][item] ? ' active' : '';
	                        html += '<td  data-model-name="' + prop + '" data-model="' + verbose +
	                            '" data-checkbox ="true">' +
	                            '<span class="checkbox ' + is_active + '" data-model="' + verbose + '" value="' + list[i].fields[prop]['value'] + '"></span>' + '</td>';
	                    } else {
	                        if (is_edit) {
	                            html += '<td  data-model-name="' + prop + '" data-model="' + verbose + '" >' +
	                                '<input type="text"  class="updatemodel" data-model="' + verbose + '"value="' + list[i].fields[prop][item] + '"></td>';
	                        } else {
	                            html += '<td   data-model-name="' + prop + '" data-model="' + verbose + '" >' +
	                                list[i].fields[prop][item] + '</td>';
	                        }

	                    }
	                }

	            }

	        }
	        html += '<td><a href="#" class="subordinate" data-id="' + id_ + '">подчиненные</a></td>';
	        html += '<td><a href="' + config.DOCUMENT_ROOT + 'account/' + id_ + '" class="questionnaire" data-id="' + id_ + '">анкета</a></td>'
	    }
	    return html;
	}

	//Генерация таблицы собитий и учасников привязаных к ним
	function view(data) {
	    var list = data.results;
	    var html = '<button  id="prev">К списку событий</button>';
	    html += '<button  id="prev_home">Моя таблица</button>';

	    // var user_id = [];
	    // var common;
	    if (!list.length) {
	        html += '<span class="empty_list">У этого события нет учасников. Нажмите "Добавить участника" что бы добавить ваших пользвателей</span>';
	    } else {

	        if (!data['isSearch']) {


	            html += '<ul class="lineTabs">'
	                //Пагинация
	            var page = 1;
	            html += '<li>Найдено ' + data['count'] + ' пользователей</li>';
	            var pages = Math.ceil(data['count'] / config.pagination_count);
	            for (var j = 1; j < pages + 1; j++) {

	                if (j == page) {
	                    html += '<li><span class="page active">  ' + j + '</span></li>'
	                } else {
	                    html += '<li><span class="page">  ' + j + '</span></li>'
	                }
	            }
	            html += '</ul>'
	                //document.querySelector(".lineTabs").innerHTML = paginations;
	        }
	        if (!data['isSearch']) {
	            html += '<table class="tab1 notfullsearch" id="userinfo">';
	        } else {
	            html += '<table class="tab1" id="userinfo">';
	        }
	        //Построение шапки 
	        var titles = Object.keys(data.results[0].fields);
	        var common_ = list[0]['common']
	        var common_titles = Object.keys(list[0]['common'])
	        html += '<tr>';
	        for (var k = 0; k < titles.length; k++) {
	            if (common_titles.indexOf(titles[k]) === -1) continue

	            if (ordering[common_[titles[k]]]) {
	                html += '<th data-order="' + common_[titles[k]] + '" class="low"><span>' + titles[k] + '</span></th>';
	            } else {
	                html += '<th data-order="' + common_[titles[k]] + '"><span>' + titles[k] + '</span></th>';
	            }
	        }
	        html += '</th><th></th><th></th></tr>';

	        html += viewBodyTableUsers(list);

	    }
	    html += '</table>';
	    return html;
	}

	function createUserInfo(data) {
	    var html = view(data);
	    document.querySelector(".tab_content").innerHTML = html;

	    //Listeners
	    //Сортировка
	    [].forEach.call(document.querySelectorAll(".tab_content .notfullsearch th"), function(el) {
	        el.addEventListener('click', function() {
	            var data_order = this.getAttribute('data-order');
	            var status = false;
	            if (ordering[data_order]) {
	                status = false;
	            } else {
	                status = true
	            }
	            ordering = {};
	            ordering[data_order] = status
	                // showEventsDataSort(data_order, status, window.parent_id)

	            var data = {}
	            data['event'] = document.getElementsByClassName('current_view')[0].getAttribute('data-event-id');
	            data['user__master'] = window.parent_id || document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	            data['ordering'] = status ? data_order : '-' + data_order;
	            //console.log(data);
	            showEventsData(data);



	        });
	    });

	    //подчиненные
	    [].forEach.call(document.querySelectorAll(".subordinate"), function(el) {
	        el.addEventListener('click', function(e) {
	            var id = $(this).attr('data-id');
	            window.parent_id = id;
	            init(id)
	        });
	    });

	    //Обновление примечания и отмечалки
	    [].forEach.call(document.querySelectorAll("#userinfo .updatemodel"), function(el) {
	        el.addEventListener('change', updateVerbose);
	    });


	    [].forEach.call(document.querySelectorAll("#userinfo span.checkbox"), function(el) {
	        el.addEventListener('click', updateVerbose);

	    });

	    //Вернутся "Моя таблица" и "к списку событий"
	    document.getElementById('prev').addEventListener('click', function() {
	        var user_id = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	        window.parent_id = user_id;
	        document.querySelector(".tab_content").innerHTML = '';
	        document.getElementById('events_links').style.display = 'block';
	        document.querySelector(".evelopments_content_table.tab_content").style.display = 'none';
	    });

	    document.getElementById('prev_home').addEventListener('click', function() {
	        var user_id = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	        window.parent_id = user_id;
	        init(user_id);

	    });

	    //Пагинация
	    [].forEach.call(document.querySelectorAll("span.page"), function(el) {
	        el.addEventListener('click', function() {

	            var data = {}
	            data['event'] = document.getElementsByClassName('current_view')[0].getAttribute('data-event-id');
	            data['user__master'] = window.parent_id || document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	            data['page'] = el.innerHTML;
	            showEventsData(data);

	            [].forEach.call(document.querySelectorAll("span.page"), function(el) {
	                el.classList.remove('active')
	            });

	            this.classList.add('active')

	        });
	    });


	    document.getElementById('events_links').style.display = 'none';

	}

	function searchEvents(value) {
	    document.querySelector(".tab_content").innerHTML = '';
	    var data = ['search=' + value];
	    var search = {
	        search: value
	    };
	    if (value.length == 0) {
	        //data = NaN;
	        return;
	    } else {
	        ajaxRequest(config.DOCUMENT_ROOT + 'api/events/', search, createEventsLink)
	    }
	}

	function showEventsData(data) {

	    var path = config.DOCUMENT_ROOT + 'api/participations/?'
	    ajaxRequest(path, data, createUserInfo);
	    document.querySelector(".evelopments_content_table.tab_content").style.display = 'inline-block';
	}


	//Постройка списка событий
	function createEventsLink(array) {
	    var array = array.results;
	    var links = document.getElementById('events_links');
	    var html = ''
	        //var week = createPeriodNames('week_days')
	    if (array.length == 0) {
	        html += '<p>Событий нет. Выберите иной период для поиска. </p>';
	    } else {
	        for (var i = 0; i < array.length; i++) {
	            html += '<li data-event-id="' + array[i]['id'] + '">';
	            html += '<span >'
	            html += array[i]['title'] + " ";
	            if (array[i]['date']) {
	                html += '<p>' + array[i]['date'] + '</p>';
	            } else {
	                //html += '<p>' + week[array[i]['day']-1] + '</p>';
	            }
	            html += '</span></li>';
	        }
	    }
	    links.innerHTML = html;
	}

	/*Переключалко по периодам кроме календаря*/
	$("#date_events.top_block_head_left li a").on('click', function() {

	    if (document.getElementById('prev')) {
	        document.getElementById('prev').click();
	    };

	    [].forEach.call(document.querySelectorAll(".top_block_head_left li a"), function(el) {
	        el.classList.remove('active');
	    });

	    this.classList.add('active');
	    var period = this.getAttribute('data-period');
	    var path = config.DOCUMENT_ROOT + 'api/events/' + period;

	    ajaxRequest(path, null, createEventsLink);

	});

	//Поиск по названию event
	$('input.search_cont').keyup(function() {

	    delay(function() {
	        searchEvents(document.querySelector('.search_cont').value);
	    }, 1000);

	});

	//Загрузка данных для конкретного event
	live('click', "li[data-event-id]", function() {
	    var data = {}
	    data['event'] = this.getAttribute('data-event-id');
	    data['user__master'] = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	    showEventsData(data);

	    [].forEach.call(document.querySelectorAll("li[data-event-id]"), function(el) {
	        el.classList.remove('current_view');
	    });
	    this.classList.add('current_view');
	});

	function updateUserInfo(data) {
	    ajaxRequest(config.DOCUMENT_ROOT + 'api/patch_participation', data, function() {}, 'POST', true, {
	        'Content-Type': 'application/json'
	    });
	}

	function init(id) {
	    //Флаг использование поиска при выгрузке данных
	    var isSearch = false;
	    var data = {};
	    [].forEach.call(document.querySelectorAll(".search_cont input"), function(el) {

	        if (el.value) {
	            data[el.getAttribute('name')] = el.value;
	            el.value = '';
	            isSearch = true
	        }
	    });

	    var path = config.DOCUMENT_ROOT + 'api/participations/';
	    if (id) {
	        data['user__master'] = id
	    }

	    if (document.getElementsByClassName('current_view').length) {
	        var event_id = document.getElementsByClassName('current_view')[0].getAttribute('data-event-id');
	        data['event'] = event_id;

	        ajaxRequest(path, data, function(answer) {
	            answer['isSearch'] = isSearch //HACK GOVNO CODE
	            createUserInfo(answer);
	        });

	    } else {
	        showPopup('Виберите событие');
	    }
	}


	$(function() {
	    $("#datepicker").datepicker({
	        dateFormat: "yy-mm-dd",
	        onSelect: function(data, t) {
	            $("#date_events.top_block_head_left li a").removeClass('active');
	            var path = config.DOCUMENT_ROOT + 'api/events/?date=' + data;
	            ajaxRequest(path, null, createEventsLink)
	        }
	    }).datepicker("setDate", new Date());

	    document.getElementsByClassName('apply_event')[0].addEventListener('click', function(e) {
	        e.preventDefault();
	        var id = window.parent_id || document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	        init(id);
	        document.querySelector('div.search_cont').style.display = 'none';
	    });

	    //инициализация приложения
	    document.querySelector(".top_block_head_left li a[data-period='today']").click();
	});