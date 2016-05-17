$('.sandwich-data span').click(function() {
    $(this).toggleClass('button_rotate')
    $(this).parents().siblings('.edit-data').toggle();
});

function createNewEvent(data) {

    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT +'api/create_event/', json, function(JSONobj) {
        document.querySelector("#create_general_event input").value = ''
        document.querySelector("#create_special_event input").value = ''
        $('.checkbox-wrap span').removeClass('active');
        showPopup(JSONobj.message);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}
/*
//Удаление и оновление в старом функционале
 function deleteEvent(id){
		 var xhr = new XMLHttpRequest();
		var data = {
		    "id": id,
		}
		var json = JSON.stringify(data);
		xhr.open("POST", 'http://5.101.121.49:8002/api/delete_event/', true)
		xhr.setRequestHeader('Content-Type', 'application/json');
		xhr.withCredentials = true;
		xhr.onreadystatechange = function() {
		    if (xhr.readyState == 4) {
		    if(xhr.status == 200) {
		        console.log(xhr.responseText);
		        }        
		    }
		}
		xhr.send(json);
 }

function updateEvent(data){
	var xhr = new XMLHttpRequest();
	var data = {
	    "title": "Ивент02",
	    "date": null,
	    "day": 3,
	    "active": true,
	    "cyclic": true
	}
	var json = JSON.stringify(data);
	xhr.open("PATCH", 'http://5.101.121.49:8002/api/events/1/', true)
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.withCredentials = true;
	xhr.onreadystatechange = function() {
	    if (xhr.readyState == 4) {
	    if(xhr.status == 200) {
	        console.log(xhr.responseText);
	        }        
	    }
	}
	xhr.send(json);
}
*/
$(function() {

    [].forEach.call(document.querySelectorAll('.checkbox-wrap span'), function(el) {
        el.addEventListener('click', function() {
            [].forEach.call(document.querySelectorAll('.checkbox-wrap span'), function(el) {
                el.classList.remove('active');
            });
            this.classList.add('active');
        });
    });  

    $(".datepicker").datepicker({
        dateFormat: "yy-mm-dd"
    });
    $(".datepicker").datepicker('setDate', new Date());
    $('.datepicker').datepicker('option', $.datepicker.regional["ru"]);

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