$(function(){

	$(".top_block_head_left [target]").click(function(e){
		e.preventDefault();

		[].forEach.call(document.querySelectorAll(".top_block_head_left [target]"), function(el) {
			el.classList.remove('active')
		})
		this.classList.add('active');	
		 var el = this.getAttribute('target');
		 document.getElementById('partner_list').style.display = 'none';
		 document.getElementById('partner_deals').style.display = 'none';
		 document.getElementById(el).style.display = 'block';
		 
	});


	document.querySelector(".top_block_head_left [target='partner_list']").click();

	create_drobbox_father('dropbox_wrap');
})
//alert(1)

function getDeals(id){
	//var id = 2
	ajaxRequest(config.DOCUMENT_ROOT+'/api/deals/?partnership__responsible__user=' + id  , null, function(data) {
		//console.log(data);
		var results = data.results;
	  	var html = '<table><tr><td>ID</td><td>Партнер</td><td>Ответственный</td><td>Дата</td><td>Сумма</td><td>Описание</td><td>Статус</td></tr>'
	  	for(var i = 0;i<results.length;i++){
	  		html += '<tr>'
	  		var field = results[i].fields;
	  			for(var j in field){
	  				if( field[j].verbose  == 'done'){
                            var status = field[j].value ? 'Завершена'  : 'Прострочена';
                            html += '<td>' + status +'</td>'
                            break
                        }
	  				html += '<td>' + field[j].value  +'</td>'
	  			}
	  		html += '</tr>'	
	  	}
	  	html += '<table>'
	  	document.getElementById('partner_deals').innerHTML = html
	})
}
function getPartnersList(id){
	//var id = id // current id
	  ajaxRequest(config.DOCUMENT_ROOT+'/api/partnerships/?responsible__user=' + id  , null, function(data) {
	  	//console.log(data);
	  	var results = data.results;
	  	var html = '<table><tr><td>Партнер</td><td>Ответственный</td><td>Сумма сделки</td><td>К-тво завершенных сделок</td><td>К-тво просроченных сделок</td></tr>'
	  	for(var i = 0;i<results.length;i++){
	  		html += '<tr>'
	  		var field = results[i].fields;
	  			for(var j in field){
	  				//console.log( field[j]   )
	  				html += '<td>' + field[j].value  +'</td>'
	  			}
	  		html += '</tr>'	
	  	}
	  	html += '<table>'
	  	document.getElementById('partner_list').innerHTML = html
	  },'GET')
}


function create_drobbox_father(id) {

    //id - parant wrapper element select 
    ajaxRequest(config.DOCUMENT_ROOT + '/api/partnerships/?is_responsible=' + 2, null, function(data) {
    	console.log(data)
        var data = data.results;
        var html = '<div class="sandwich-wrap father "><span class="sandwich-cont">Отвественный</span>' +
            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>';
        for (var i = 0; i < data.length; i++) {
            html += '<li data-id="' + data[i].id + '"><span>' + data[i].fullname + '</span></li>';
        }
        html += '</ul></div></div>';
        document.getElementById(id).innerHTML = html;

    });

}