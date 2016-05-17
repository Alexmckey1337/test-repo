	function init(id) {

	    var id = id || document.location.href.split('/')[document.location.href.split('/').length - 2]
	    ajaxRequest(config.DOCUMENT_ROOT+'api/users/' + id, null, function(data) {
	        var profile = '';
	        var user_hierarchy = '';
	        var user_status = '';
	        var status_name = [];
	        for (var prop in data.fields) {
	            if (!data.fields.hasOwnProperty(prop)) continue

	            if (data.fields[prop]['type'] == 's') {
	                if (data.fields[prop].verbose == 'born_date') {
	                    profile += '<input type="text"  id="datepicker"  style="cursor:pointer;"  name="' +
	                        data.fields[prop].verbose + '" value="' + data.fields[prop]['value'] + '">';
	                } else {
	                    profile += '<li><p>' + prop + '*</p><input type="text" name="' + data.fields[prop].verbose + '" value="' + data.fields[prop]['value'] + '"></li>';
	                }
	            }
	            if (data.fields[prop]['type'] == 'h') {
	                user_hierarchy += '<li><p>' + prop + '*</p><span>' + data.fields[prop]['value'] + '</span></li>';
	            }
	            if (data.fields[prop]['type'] == 'b') {
	                var is_checked = data.fields[prop]['value'] ? 'checked' : '';
	                if (is_checked) {
	                    status_name.push(prop);
	                }
	            }
	            if (data.fields[prop]['type'] == 't') {
	                profile += '<li><p>' + prop + '*</p><textarea rows = "3" >' + data.fields[prop]['value'] + '</textarea>';
	            }
	        }
	        getStatus(status_name);
	        document.getElementById('user-info').innerHTML = profile;
	        document.getElementById('status').innerHTML = user_hierarchy;
	        $("#datepicker").datepicker({
	            dateFormat: "yy-mm-dd"
	        });
	    })

	}

	//Получение иерархий пользователя
	function changeHierarhy(el) {
	    createHierarhyDropBox();
	   	el.style.display = 'none'
	}

	function createHierarhyDropBox() {

	    ajaxRequest(config.DOCUMENT_ROOT+'api/departments/', null, function(data) {
	        var data = data.results;
	        var html = '<div class="sandwich-wrap department-wrap"><span class="sandwich-cont">Отдел</span>' +
	            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" ><span>' + data[i].title + '</span></li>'
	        }
	        html += '</ul></div></div>';
	        document.getElementById('dropbox_wrap').innerHTML = html;
	        createHierarhyDropBox_low();
	        createHierarhyDropBox_low();
	    });

	}


	function createHierarhyDropBox_low() {

	    ajaxRequest(config.DOCUMENT_ROOT+'api/hierarchy/', null, function(data) {
	        var data = data.results;
	        var html = '<div class="sandwich-wrap hierarchy-wrap"><span class="sandwich-cont">Ранг</span>' +
	            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>';
	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" data-level="' + data[i].level + '"><span>' + data[i].title + '</span></li>';
	        }
	        html += '</ul></div></div>';
	        document.getElementById('dropbox_wrap').innerHTML =
	            document.getElementById('dropbox_wrap').innerHTML + html;

	    });
	}


	function createHierarhyDropBox_last(id, level) {


	    ajaxRequest(config.DOCUMENT_ROOT+'api/users/?department=' + id + '&hierarchy=' + level, null, function(data) {
	        var data = data.results;
	        var html = '<div class="sandwich-wrap hierarchy__level"><span class="sandwich-cont">Отвественный</span>' +
	            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" data-last="true"><span>' + data[i].fullname + '</span></li>'
	        }
	        html += '</ul></div></div>';
	        document.getElementById('dropbox_wrap').innerHTML =
	            document.getElementById('dropbox_wrap').innerHTML + html;

	    });

	}

	function updateUser() {

	    var email = document.querySelector("input[name='email']").value;
	    var first_name = document.querySelector("input[name='first_name']").value;
	    var last_name = document.querySelector("input[name='last_name']").value;
	    var middle_name = document.querySelector("input[name='middle_name']").value;
	    var phone_number = document.querySelector("input[name='phone_number']").value;
	    var facebook = document.querySelector("input[name='facebook']").value;
	    var vkontakte = document.querySelector("input[name='vkontakte']").value;
	    var skype = document.querySelector("input[name='skype']").value;
	    var address = document.querySelector("input[name='address']").value;
	    var description = document.querySelector("textarea").value;
	    var date = document.querySelector("#datepicker").value;

	    var region = document.querySelector("input[name='region']").value;
	    var district = document.querySelector("input[name='district']").value;

	    if (!email || !first_name || !last_name || !middle_name || !phone_number) {
	        showPopup('Заполните пустые поля');
	        return
	    }

/*
	    if (!document.querySelectorAll(".user-status span.active").length) {
	        showPopup('Выберите статус');
	        return
	    }
*/
	    var statuses = [];
	    [].forEach.call(document.querySelectorAll(".user-status span.active"), function(el) {
	        statuses.push(el.getAttribute('id'))
	    });

	    /*
	    if(  !isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont"))  
	    	//&&  document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id')
	    	){
	    	showPopup('Выбирите подчиненного');
	    	return
	    }

	    if(  !document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id') ){
	    	showPopup('Выбирите подчиненного в последнем меню');
	    	return
	    }
	     */


	    var data = {
	        "id": document.location.href.split('/')[document.location.href.split('/').length - 2],
	        "email": email,
	        "first_name": first_name,
	        "last_name": last_name,
	        "middle_name": middle_name,
	        "born_date": date,
	        "phone_number": phone_number,
	        "vkontakte": vkontakte,
	        "facebook": facebook,
	        "address": address,
	        "description": description,
	        "skype": skype,
	        "statuses": statuses,

	       	"district":district,
	        "region" :region
	    }

	    if (isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont")) &&
	        document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id')) {
	        data['master'] = document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id');
	        data['department'] = document.querySelector(".sandwich-wrap.department-wrap .sandwich-cont").getAttribute('data-id');
	        data['hierarchy'] = document.querySelector(".sandwich-wrap.hierarchy-wrap .sandwich-cont").getAttribute('data-id');
	    }

	    var json = JSON.stringify(data);

	    ajaxRequest(config.DOCUMENT_ROOT+'api/create_user/', json, function(data) {
	        showPopup(data.message);
	        if (data.redirect) {
	            setTimeout(function() {
	                window.location.href = '/account/' + data.id;
	            }, 1000);
	        }

	        [].forEach.call(document.querySelectorAll("#user-info input:not([type='button']"), function(el) {
	            //	el.value = '';
	        });
	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });


	}

	//Получение статусов пользователя ..Левит	
	function getStatus(statuses) {

	    ajaxRequest(config.DOCUMENT_ROOT+'api/statuses/', null, function(data) {
	        var data = data.results;
	        var html = '<ul>';
	        for (var i = 0; i < data.length; i++) {
	            html += '<li class="item_user clearfix"><i data-title="' + data[i].title + '">' +
	                data[i].title + '</i><span class="checkbox" id ="' + data[i].id + '" ></span></li>';
	        }
	        html += '</ul>';
	        document.getElementsByClassName('user-status')[0].innerHTML = html;
	        for (var j = 0; j < statuses.length; j++) {
	            $(" i[data-title='" + statuses[j] + "'] ").next().addClass('active');
	        }


	        [].forEach.call(document.querySelectorAll(".user-status span"), function(el) {
	            el.addEventListener('click', function() {
	                this.classList.toggle('active');
	            })

	        });

	    });
	}

	$(function() {
	    init();
	})