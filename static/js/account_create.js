	//Получение иерархий пользователя
	function createHierarhyDropBox() {

	    ajaxRequest(config.DOCUMENT_ROOT + 'api/departments/', null, function(data) {
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

	    ajaxRequest(config.DOCUMENT_ROOT + 'api/hierarchy/', null, function(data) {
	        var data = data.results;
	        var html = '<div class="sandwich-wrap hierarchy-wrap"><span class="sandwich-cont">Ранг</span>' +
	            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" data-level="' + data[i].level + '"><span>' + data[i].title + '</span></li>';
	        }
	        html += '</ul></div>';
	        document.getElementById('dropbox_wrap').innerHTML =
	            document.getElementById('dropbox_wrap').innerHTML + html;

	    });
	}

	//постройка последнего DropBox  на основе двух выбраных ранее 
	/*
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
	*/

	function createHierarhyDropBox_last(id, level, page) {
	    var page = page || 1;

	    ajaxRequest(config.DOCUMENT_ROOT + 'api/short_users/?department=' + id + '&hierarchy=' + level + '&page=' + page, null, function(data) {

	        var count = data.count; //Количество всех пользователей ?
	        var data = data.results;
	        var html = '';
	        var el_id = 'dep_1';
	        //paginations
	        html += '<p>Найдено ' + count + ' пользователей</p><p>Вибирите отвественного</p>';
	        html += '<ul class="lineTabs">';
	        var pages = Math.ceil(count / config.pagination_mini_count);

	        //if (pages > 1) {
	        for (var j = 1; j < pages + 1; j++) {
	            if (j == page) {
	                html += '<li><span class="page active">  ' + j + '</span></li>'
	            } else {
	                html += '<li><span class="page">  ' + j + '</span></li>'
	            }

	        }


	        html += '</ul>';
	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" class="item_user">' +
	                '<span class="checkbox" data-id ="' + data[i].id + '" ></span>' + data[i].fullname +
	                '</li>'
	        }


	        removePopups(el_id)
	        createPopups(el_id, html, function() {

	            [].forEach.call(document.getElementById(el_id).querySelectorAll("span.page"), function(el) {
	                el.addEventListener('click', function() {

	                    var page = el.innerHTML;
	                    createHierarhyDropBox_last(id, level, page)

	                });
	            });
 

	            [].forEach.call(document.querySelectorAll(".pop_cont span.checkbox"), function(tag) {



	                tag.addEventListener('click', function() {

	                    [].forEach.call(document.querySelectorAll(".pop_cont span.checkbox"), function(tag) {
	                        tag.classList.remove('active');
	                    })
	                    this.classList.toggle('active');

	                    document.getElementById('status').innerHTML = '<li>Ваш отвественный :' + this.nextSibling.textContent +
	                        '<input type="button"  value = "Сменить наставника"></li>';

	                    document.querySelector("#status input").addEventListener('click', function() {
	                        showPopupById(el_id);
	                    })


	                })


	            });
	            showPopupById(el_id);
	        });


	    });

	}

	//Получение статусов пользователя ..Левит	
	function getStatus() {

	    ajaxRequest(config.DOCUMENT_ROOT + 'api/statuses/', null, function(data) {
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



		function handleFileSelect(evt) {
	
		    var files = evt.target.files; // FileList object

		    // Loop through the FileList and render image files as thumbnails.
		    for (var i = 0, f; f = files[i]; i++) {

		      // Only process image files.
		      if (!f.type.match('image.*')) {
		        continue;
		      }

		      var reader = new FileReader();

		      // Closure to capture the file information.
		      reader.onload = (function(theFile) {
		        return function(e) {
	
		          document.querySelector(".user-photo img").src= e.target.result
		        };
		      })(f);

		      // Read in the image file as a data URL.
		      reader.readAsDataURL(f);
		    }
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


	    if ( /*!email ||*/ !first_name || !last_name /*|| !phone_number*/ ) {
	        showPopup('Заполните пустые поля');
	        return
	    }


	    var url =config.DOCUMENT_ROOT + '/api/short_users/?search=' + first_name +'+' + last_name;

	    ajaxRequest( url, null, function(data) {

	    	if(data.results.length){
	    		 var id  = data.results[0].id;
	    		 showPopup('Такой пользователей есть уже в БД');

	    		 setTimeout(function() {
                    window.location.href = '/account/' + id ;
                }, 1500);
	    		 return 
	    	}
	    })
	  
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

	    if (!document.querySelector(".sandwich-wrap.department-wrap .sandwich-cont").getAttribute('data-id') ||
	        !document.querySelector(".sandwich-wrap.hierarchy-wrap .sandwich-cont").getAttribute('data-id')) {
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
	        "vkontakte": vkontakte,
	        "facebook": facebook,
	        "address": address,
	        "description": description,
	        "skype": skype,
	        "statuses": statuses,
	        "country": country,
	        "city": city,
	        "district": district,
	        "region": region

	    }

	    /*
	    	    if(  isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont")) 
	    	    	&& document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id') ){
	    	    	data['master']  = document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont").getAttribute('data-id');
	    	    }

	    */

	    if (document.getElementById('dep_1') && document.querySelector("#dep_1 .checkbox.active")) {
	        data['master'] = document.querySelector("#dep_1 .checkbox.active").getAttribute('data-id')
	    }
        
	    /*division*/
	    if (document.getElementById('divisions_1') && document.querySelector("#divisions_1 .checkbox.active")) {
	        //document.querySelector("#divisions_1 .checkbox.active").getAttribute('data-id')

	        	var  arr = [];   
	        	$( "#divisions_1 .checkbox.active").each(function(){arr.push(this.getAttribute('data-id'))});
	        	data['divisions'] = arr
	    }



	    data['department'] = document.querySelector(".sandwich-wrap.department-wrap .sandwich-cont").getAttribute('data-id');
	    data['hierarchy'] = document.querySelector(".sandwich-wrap.hierarchy-wrap .sandwich-cont").getAttribute('data-id');
	    var json = JSON.stringify(data);



	    ajaxRequest(config.DOCUMENT_ROOT + 'api/create_user/', json, function(data) {
	        showPopup(data.message);
	      //  console.log(data)
	        if (data.redirect) {

	        	//console.log(data.id)
	        	var fd = new FormData();    
				fd.append( 'file', $('input[type=file]')[0].files[0] );
				fd.append('id' , data.id)
				var xhr = new XMLHttpRequest();
				xhr.withCredentials = true;
				    xhr.open('POST',config.DOCUMENT_ROOT + 'api/create_user/', true);
				  //  xhr.setRequestHeader('Content-Type', 'application/json');
				    xhr.onload = function(answer){
			
				    	var answer = JSON.parse(answer.currentTarget.response)
	
				    	//showPopup(answer.message);
				       if (answer.redirect) {
					            setTimeout(function() {
					                window.location.href = '/account/' + answer.id;
					            }, 1000);
					        }
				    };
				    xhr.send(fd);
								




	
	        }
	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });


	
	 
	    
/*
var fd = new FormData();    
fd.append( 'file', $('input[type=file]')[0].files[0] );



for(prop in data){
	fd.append(prop,data[prop]);
}

for(var s =0 ; s< statuses.length ; s++){
	fd.append('statuses[]',statuses[s])
}


var xhr = new XMLHttpRequest();
xhr.withCredentials = true;
    xhr.open('POST',config.DOCUMENT_ROOT + 'api/create_user/', true);
  //  xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function(answer){
    	//debugger
    	var answer = JSON.parse(answer.currentTarget.response)

    	showPopup(answer.message);
       if (answer.redirect) {
	            setTimeout(function() {
	                window.location.href = '/account/' + answer.id;
	            }, 1000);
	        }
    };
    xhr.send(fd);


	   */
	}




	function createDivisions() {
	    

	    ajaxRequest(config.DOCUMENT_ROOT + 'api/divisions/', null, function(data) {

	        
	        var data = data.results;
	        var html = '';
	        var el_id = 'divisions_1';
	      

	        for (var i = 0; i < data.length; i++) {
	            html += '<li data-id="' + data[i].id + '" class="item_user">' +
	                '<span class="checkbox" data-id ="' + data[i].id + '" ></span>' + data[i].title +
	                '</li>'
	        }


	        removePopups(el_id)
	        createPopups(el_id, html, function() {

	           

	            [].forEach.call(document.querySelectorAll("#divisions_1 span.checkbox"), function(tag) {



	                tag.addEventListener('click', function() {
	                	/*
	                    [].forEach.call(document.querySelectorAll("#divisions_1 span.checkbox"), function(tag) {
	                        tag.classList.remove('active');
	                    })
	*/
	                    this.classList.toggle('active');

	                })


	            });
	            showPopupById(el_id);
	        });


	    });

	}


	$(function() {
	    $("#datepicker").datepicker({
	        dateFormat: "yy-mm-dd",
	        defaultDate: '-15y'
	    })
	    getStatus();
	    createHierarhyDropBox();


	    document.getElementsByName('f')[0].addEventListener('change', handleFileSelect, false);

	    document.getElementById('division').addEventListener('click',function(){

			   createDivisions()


	    })
	});