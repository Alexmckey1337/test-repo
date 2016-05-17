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
	    ajaxRequest(config.DOCUMENT_ROOT+'api/update_participation/', json, function() {

	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });

	}

	function createNewUsers(data) {
	    var data = JSON.parse(data);
	    var html = '<ul>';
	    for (var i = 0; i < data.length; i++) {
	        html += '<li class="item_user clearfix">' + data[i].fullname + '<span class="checkbox" id ="' + data[i].id + '" ></span></li>';
	    }
	    html += '</ul>';
	    document.getElementById('wrap_user').innerHTML = html;
	    [].forEach.call(document.querySelectorAll("#wrap_user span"), function(el) {
	        el.addEventListener('click', function(elem) {
	            this.classList.toggle('active');
	        })
	    })
	};

	//Генерация таблицы собитий и учасников привязаных к ним
	function view(data) {
	    var list = data.results;
	    var html = '<button  id="prev">К списку событий</button>';
	    html += '<button  id="prev_home">Моя таблица</button>';
	    var user_id = [];
	    var common;
	    if (!list.length) {
	        html += '<span class="empty_list">У этого события нет учасников. Нажмите "Добавить участника" что бы добавить ваших пользвателей</span>';
	    } else {
	        html += '<table class="tab1" id="userinfo">';
	        var titles = Object.keys(data.results[0].fields);
	        var common_ = list[0]['common']
	        var common_titles = Object.keys(list[0]['common'])
	        html += '<tr>';
	        for (var k = 0; k < titles.length; k++) {
	            if (common_titles.indexOf(titles[k]) === -1) continue
	            html += '<th data-order="' + common_[titles[k]] + '">' + titles[k] + '</th>';
	        }
	        html += '</th><th></th><th></th></tr>';

	        for (var i = 0; i < list.length; i++) {
	            var id = list[i]['id'];
	            var id_ = list[i].fields.id;
	            var common = list[i].common;
	            html += '<tr data-id="' + list[i]["id"] + '">';
	            user_id.push(list[i]["uid"]);
	            for (var prop in list[i].fields) {
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
	            html += '<td><a href="http://vocrm.org/account/' + id_ + '" class="questionnaire" data-id="' + id_ + '">анкета</a></td>'
	        }
	    }
	    html += '</table>';
	    return html;
	}

	function createUserInfo(data) {

	    var html = view(data);
	    document.querySelector(".tab_content").innerHTML = html;

	    //Listeners
	    [].forEach.call(document.querySelectorAll(".tab_content th"), function(el) {
	        el.addEventListener('click', function() {
	            var data_order = this.getAttribute('data-order');
	            if (window.location.hash) {
	                var ordering = JSON.parse(window.location.hash.slice(1))
	            } else {
	                var ordering = {}
	            }
	            var status = ordering[data_order] = ordering[data_order] ? false : true
	            var ordering = JSON.stringify(ordering)
	            window.location.hash = ordering
	            showEventsDataSort(data_order, status, window.parent_id)

	        });
	    });

	    [].forEach.call(document.querySelectorAll(".subordinate"), function(el) {
	        el.addEventListener('click', function(e) {
	            var id = $(this).attr('data-id');
	            window.parent_id = id;
	            init(id)
	        });
	    });

	    [].forEach.call(document.querySelectorAll("#userinfo .updatemodel"), function(el) {
	        el.addEventListener('change', updateVerbose);
	    });


	    [].forEach.call(document.querySelectorAll("#userinfo span.checkbox"), function(el) {
	        el.addEventListener('click', updateVerbose);

	    });

	    document.getElementById('prev').addEventListener('click', function() {
	        document.querySelector(".tab_content").innerHTML = '';
	        document.getElementById('events_links').style.display = 'block';
	        document.querySelector(".evelopments_content_table.tab_content").style.display = 'none';
	    });

	    document.getElementById('prev_home').addEventListener('click', function() {
	        var user_id = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	        init(user_id);

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
	        ajaxRequest(config.DOCUMENT_ROOT+'api/events/', search, createEventsLink)
	    }
	}

	function showEventsData() {

	    var event_id = this.getAttribute('data-event-id');
	    var master_id = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	    var path = config.DOCUMENT_ROOT+'api/participations/?event=' + event_id + '&user__master=' + master_id;

	    ajaxRequest(path, null, createUserInfo);

	    [].forEach.call(document.querySelectorAll("li[data-event-id]"), function(el) {
	        el.classList.remove('current_view');
	    });
	    this.classList.add('current_view');
	    document.querySelector(".evelopments_content_table.tab_content").style.display = 'inline-block';
	}


	function showEventsDataSort(order, data_order_reverse, master_id) {

	    var event_id = document.getElementsByClassName('current_view')[0].getAttribute('data-event-id');
	    var master_id = master_id || document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
	    var path = config.DOCUMENT_ROOT+'api/participations/?event=' + event_id + '&user__master=' + master_id;
	    if (order) {
	        var path = config.DOCUMENT_ROOT+'api/participations/?event=' + event_id + '&user__master=' + master_id + '&ordering=' + order;
	        if (data_order_reverse) {
	            var path = config.DOCUMENT_ROOT+'api/participations/?event=' + event_id + '&user__master=' + master_id + '&ordering=-' + order;
	        }
	    }

	    ajaxRequest(path, null, createUserInfo);
	}


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

	
	$("#date_events.top_block_head_left li a").on('click', function() {

	    if (document.getElementById('prev')) {
	        document.getElementById('prev').click();
	    };

	    [].forEach.call(document.querySelectorAll(".top_block_head_left li a"), function(el) {
	        el.classList.remove('active');
	    });

	    this.classList.add('active');
	    var period = this.getAttribute('data-period');
	    var path = config.DOCUMENT_ROOT+'api/events/' + period;

	    ajaxRequest(path, null, createEventsLink);

	});


	$('input.search_cont').keyup(function() {

	    delay(function() {
	        searchEvents(document.querySelector('.search_cont').value);
	    }, 1000);
	});

	$(function() {
	    $("#datepicker").datepicker({
	        dateFormat: "yy-mm-dd",
	        onSelect: function(data, t) {
	            $("#date_events.top_block_head_left li a").removeClass('active');
	            var path = config.DOCUMENT_ROOT+'api/events/?date=' + data;
	            ajaxRequest(path, null, createEventsLink)
	        }
	    }).datepicker("setDate", new Date());

	    document.querySelector(".top_block_head_left li a[data-period='today']").click();
	});

	live('click', "li[data-event-id]", showEventsData);

	function updateUserInfo(data) {


	    ajaxRequest(config.DOCUMENT_ROOT+'api/patch_participation', data, function() {}, 'POST', true, {
	        'Content-Type': 'application/json'
	    });

	}

	function createHierarhyDropBox() {
	    var hierarchy_level = document.getElementsByClassName('admin_name')[0].getAttribute('data-hierarchy-level');
	    while (hierarchy_level > 1) {

	        ajaxRequest(config.DOCUMENT_ROOT+'api/users/?hierarchy__level=' + hierarchy_level, null, function(data) {
	            var data = data.results;
	            var html = '<div class="sandwich-wrap"><span class="sandwich-cont">Сотник</span>' +
	                '<span class="sandwich-button"></span><div class="sandwich-block"><ul>';
	            for (var i = 0; i < data.length; i++) {
	                html += '<li data-id="' + data[i].id + '"><span>' + data[i].fullname + '</span></li>'
	            }
	            html += '</ul></div></div>';
	            document.getElementById('hierarhy_dropbox_wrapper').innerHTML =
	                document.getElementById('hierarhy_dropbox_wrapper').innerHTML + html;

	        });
	        hierarchy_level--
	    }
	}

	function createHierarhyDropBoxes(id) {
	    ajaxRequest(config.DOCUMENT_ROOT+'api/users/?master=' + id, null, function(data) {})
	}

	function init(id) {

	    var name = document.getElementsByName('name')[0].value;
	    var last_name = document.getElementsByName('surname')[0].value;
	    var middle_name = document.getElementsByName('secondname')[0].value;
	    var tel = document.getElementsByName('tel')[0].value;
	    var email = document.getElementsByName('email')[0].value;
	    var data = {}
	    if (name) {
	        data['user__first_name'] = name;
	    }
	    if (last_name) {
	        data['user__last_name'] = last_name
	    }
	    if (middle_name) {
	        data['user__middle_name'] = middle_name
	    }
	    if (tel) {
	        data['user__phone_number'] = tel;
	    }
	    if (email) {
	        data['user__email'] = email;
	    }
	    var path = config.DOCUMENT_ROOT+'api/participations/';
	   // data['user__master'] = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');

	    if (id) {
	        data['user__master'] = id
	    }

	    if (document.getElementsByClassName('current_view').length) {
	        var event_id = document.getElementsByClassName('current_view')[0].getAttribute('data-event-id');
	        data['event'] = event_id;

	        [].forEach.call(document.querySelectorAll(".search_cont input"), function(el) {
	            el.value = '';
	        });

	        ajaxRequest(path, data, function(answer) {
	            createUserInfo(answer);
	        });

	    } else {
	        showPopup('Виберите событие');
	    }

	}
	$(function() {
	    document.getElementsByClassName('apply_event')[0].addEventListener('click', function(e) {
	        e.preventDefault();
	        init();
	        document.querySelector('div.search_cont').style.display = 'none';
	    });
	});

