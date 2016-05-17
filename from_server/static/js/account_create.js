	//Получение иерархий пользователя
	function createHierarhyDropBox() {

	    ajaxRequest(config.DOCUMENT_ROOT+'api/departments/', null, function(data) {
	        var data = data.results
	        var html = '<div class="sandwich-wrap department-wrap"><span class="sandwich-cont">Отдел</span>' +
	            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" ><span>' + data[i].title + '</span></li>'
	        }
	        html += '</ul></div></div>';
	        document.getElementById('dropbox_wrap').innerHTML =
	            document.getElementById('dropbox_wrap').innerHTML + html;
	        createHierarhyDropBox_low();
	        createHierarhyDropBox_low();
	    });

	}


	function createHierarhyDropBox_low() {

	    ajaxRequest(config.DOCUMENT_ROOT+'api/hierarchy/', null, function(data) {
	        var data = data.results;
	        var html = '<div class="sandwich-wrap hierarchy-wrap"><span class="sandwich-cont">Ранг</span>' +
	            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
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

	//Получение статусов пользователя ..Левит	
	function getStatus() {

	    ajaxRequest(config.DOCUMENT_ROOT+'api/statuses/', null, function(data) {
	        var data = data.results;
	        var html = '<ul>';
	        for (var i = 0; i < data.length; i++) {
	            html += '<li class="item_user clearfix">' + data[i].title + '<span class="checkbox" id ="' + data[i].id + '" ></span></li>';
	        }
	        html += '</ul>';
	        document.getElementsByClassName('user-status')[0].innerHTML = html;


	        [].forEach.call(document.querySelectorAll(".user-status span"), function(el) {
	            el.addEventListener('click', function() {
	                this.classList.toggle('active');
	            })

	        });

	    })
	}

	//создать пользователя	
	function AddNewUser() {

	    var email = document.querySelector("input[name='email']").value;
	    var first_name = document.querySelector("input[name='first_name']").value;
	    var last_name = document.querySelector("input[name='last_name']").value;
	    var middle_name = document.querySelector("input[name='middle_name']").value;
	    var phone_number = document.querySelector("input[name='phone_number']").value;
	    var facebook = document.querySelector("input[name='fb']").value;
	    var vkontakte = document.querySelector("input[name='vk']").value;
	    var skype = document.querySelector("input[name='skype']").value;
	    var address = document.querySelector("input[name='address']").value;
	    var description = document.querySelector("textarea").value;
	    var date = document.querySelector("#datepicker").value;

	   	var city = document.querySelector("input[name='city']").value;
	    var country = document.querySelector("input[name='country']").value;

	    var region = document.querySelector("input[name='region']").value;
	    var district = document.querySelector("input[name='district']").value;


	    if (/*!email ||*/ !first_name || !last_name /*|| !phone_number*/) {
	        showPopup('Заполните пустые поля');
	        return
	    }

	    /*
	    if(  !document.querySelectorAll(".user-status span.active").length ){
	    	showPopup('Выбирите статус');
	    	return
	    }
	    */

	    var statuses = [];
	    [].forEach.call(document.querySelectorAll(".user-status span.active"), function(el) {
	        statuses.push(el.getAttribute('id'))
	    });

	    if( !document.querySelector(".sandwich-wrap.department-wrap .sandwich-cont").getAttribute('data-id') || 
	    	!document.querySelector(".sandwich-wrap.hierarchy-wrap .sandwich-cont").getAttribute('data-id')  ){
	    	showPopup('Выбирите отдел и ранг');
	        return
	    }

/*
	    if (!isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont"))
	        //&&  document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id')
	    ) {
	        showPopup('Выбирите отдел и ранг');
	        return
	    }
*/
/*
	    if (!document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id')) {
	        showPopup('Выбирите отвественного');
	        return
	    }
*/
	    var data = {

	        "email": email,
	        "first_name": first_name,
	        "last_name": last_name,
	        "middle_name": middle_name,
	        "born_date": date,
	        "phone_number": phone_number,
	        //"master": document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id'),
	        "vkontakte": vkontakte,
	        "facebook": facebook,
	        "address": address,
	        "description": description,
	        "skype": skype,
	        "statuses": statuses,
	        "country": country,
	        "city": city,

	        "district":district,
	        "region" :region

	    }


	    console.log(data);
	    debugger

	    if(  isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont")) 
	    	&& document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id') ){
	    	data['master']  = document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id');
	    }
	    data['department'] = document.querySelector(".sandwich-wrap.department-wrap .sandwich-cont").getAttribute('data-id');
	    data['hierarchy'] = document.querySelector(".sandwich-wrap.hierarchy-wrap .sandwich-cont").getAttribute('data-id');
	    var json = JSON.stringify(data);

	    ajaxRequest(config.DOCUMENT_ROOT+'api/create_user/', json, function(data) {
	        showPopup(data.message);
	        if (data.redirect) {
	            setTimeout(function() {
	                window.location.href = '/account/' + data.id;
	            }, 1000);
	        }
	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });
	}

	$(function() {
	    $("#datepicker").datepicker({
	        dateFormat: "yy-mm-dd",
	        defaultDate: '-15y'
	    })
	    getStatus();
	    createHierarhyDropBox();
	});