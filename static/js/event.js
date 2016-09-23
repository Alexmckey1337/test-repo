$(document).ready(function(){
	getEventsList();
});


function getEventsList(){
	ajaxRequest(config.DOCUMENT_ROOT + 'api/event_types/', null, function (data) {
	 	//console.log(data)
	 	var result = data.results;
	 	var html = '';
	 	var last_date_event;
	 	for(var i =0 ; i<result.length;i++){


	 		last_date_event = result[i].last_event_date ? '<p>Последнее событие: <span>'+result[i].last_event_date + '</span></p>'  : '';
	 		html +=	'<div class="event-i"  data-id="'+ result[i].id  +'"  data-tittle="'+ result[i].title  +'" data-url="'+  result[i].image +'" style="background:url('+ result[i].image   +')  "><span>'+ result[i].title +'</span><div class="event-hover">'+
						'<h3>' +  result[i].title  +'</h3>'+ last_date_event+
						'<p>Всего событий: <span>'+  result[i].event_count  +'</span>	</p><button>Перейти</button>' +
					'</div></div>'
	 	}
	 	document.querySelector(".events-wrap").innerHTML = html;
/*
		 Array.prototype.forEach.call(document.querySelectorAll('button[data-id]'), function(el) {
		        el.addEventListener('click', function() {
		        	var id =   this.getAttribute('data-id') ;
		        	var title= document.querySelector(".events-wrap h3").innerHTML 
		            document.location.href = '/event_info?id=' + id +'&title=' + title
		        })
    	});
*/
		 Array.prototype.forEach.call(document.querySelectorAll('.event-hover'), function(el) {
		        el.addEventListener('click', function() {
		        	var id =   this.parentElement.getAttribute('data-id') 
		        	var title= this.parentElement.getAttribute('data-tittle') 
		            document.location.href = '/event_info?id=' + id +'&title=' + title
		        })
    	});
	 })
}