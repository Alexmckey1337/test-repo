$(function(){
	init();
})
function init(){
	SynopsisList();
	live('click', "li[data-event-id]", showReportData);
	live('change', "#synopsis_info input", updateSynopsis);
}
function SynopsisList(){
	ajaxRequest(config.DOCUMENT_ROOT+'/api/synopsis/', null, function(data){
			var results = data.results;
			if(results.length == 0){
				document.getElementById('synopsys_container').innerHTML = 'список пуст'
				return
			}
			var html = ''
			//var html = '<ul id="synopsis_links">'
			for( var i = 0; i< results.length; i++){
				//console.log(results[i])
				html += '<li data-event-id="' + results[i].id  + '" ><span>' + results[i].date +' </span>' +
				 /*'<div data-id="' +
                    results[i].id + '" class="table-button"><i class="table-edit"></i><i class="table-delete"></i></div>'+
                    */
                    '</li>'
			}
			html +='<li style="border:none"><a href="#" class="add-button green-button">Добавить cинопсис</a></li>'
			//html += '</ul>'
			document.getElementById('synopsis_links').innerHTML = html;


			document.querySelector(".add-button").addEventListener('click',function(){
				document.getElementById('synopsys_container').style.display = 'none';
				document.getElementById('create_sypopsys').style.display = 'block';
				
			})

	});
}
//Отрисовка отдельного синопсиса
function showReportData(){
	var id = this.getAttribute('data-event-id');
	var path = config.DOCUMENT_ROOT + 'api/synopsis/'+ id;
	ajaxRequest(path, null, function(data){
	//	var common = data.common;
		var html = '<table>'
		var fields = data.fields;
		var id = data.id;

		for(  var prop in fields){
			    var is_edit = fields[prop]['change']
	            var verbose = fields[prop]['verbose']
	            var value = fields[prop]['value']
	            if(is_edit){
	            	html += '<tr><td>' + prop + '</td><td><input   data-model="'+verbose +'" data-id ="' + id + '" type="text" value="' + value + '"></td></tr>'
	            }else{
	            	html += '<tr><td>' + prop + '</td><td><input  disabled data-model="'+verbose +'" data-id ="' + id + '" type="text" value="' + value + '"></td></tr>'
	            }
		}
		html +='</table>'
		document.getElementById('synopsis_info').innerHTML = html
	});

	[].forEach.call(document.querySelectorAll("li[data-event-id]"), function(el) {
	        el.classList.remove('current_view');
	    });
	this.classList.add('current_view');
}

function updateSynopsis(){
	var id = this.getAttribute('data-id') ;
	var prop  =  this.getAttribute('data-model') ;
		var data = {
			id:parseInt(id)
		};


		 [].forEach.call(document.querySelectorAll("#synopsis_info input"), function(el) {
         //   data[el.getAttribute('data-model')] = el.value;
        });

		data[prop] = this.value
	 var json = JSON.stringify(data);
	    ajaxRequest(config.DOCUMENT_ROOT+'api/synopsis/post_data/', json, function() {

	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });
}


function createSynonsis(){
	var data ={};
	var history_description = document.getElementsByName('history_description')[0].value
	var hero = document.getElementsByName('hero')[0].value
	var tel = document.getElementsByName('phone_number')[0].value

	if( !history_description || !hero || !tel ){
		//showPopup('Заполните необходимые поля');
		//return 
	}

	[].forEach.call(document.querySelectorAll("#user-info input"), function(el) {
            data[el.getAttribute('name')] = el.value;
           // el.value = ''
        });


	 var json = JSON.stringify(data);
	    ajaxRequest(config.DOCUMENT_ROOT+'api/synopsis/post_data/', json, function(data) {

	    	console.log(data.status);
	    	console.log(data.message);

	    	if (data.status == true){
	    		showPopup(data.message);
	    		init();
	    		document.getElementById('synopsys_container').style.display = 'block';
				document.getElementById('create_sypopsys').style.display = 'none';
	    	}else{
	    		showPopup(data.message);
	    	} 

 			
            


	    }, 'POST', true, {
	        'Content-Type': 'application/json'
	    });
}
