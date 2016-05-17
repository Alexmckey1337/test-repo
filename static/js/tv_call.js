var findData = {}

ajaxRequest(config.DOCUMENT_ROOT + 'api/tv_call/check_tv_consultant/',null ,function(answer) {

		if (answer.is_consultant == 'false'){
			window.findData['user__master__id'] = answer.user_id
		}else{
			document.getElementById('statistic').style.display = 'block'; 
		}
	})

function initialRequestSubordinate(page){
	var data = {}
	var page = page || 1
	data['page'] = parseInt(page) ;
	
	if(  window.findData['user__department'] || window.findData['search'] ){

		var data = Object.create(window.findData);
		data['page'] = parseInt(page) ;
		var url = window.UrlData ?  '/api/tv_call_stat/' : 'api/tv_call/'
		ajaxRequest(config.DOCUMENT_ROOT + url ,data ,function(answer) {
			createTvCallTable(answer,page)
		})
		return 
	}
	
	var url = window.UrlData ?  '/api/tv_call_stat/' : 'api/tv_call/subordinate/'
	ajaxRequest(config.DOCUMENT_ROOT + url ,data ,function(answer) {
		createTvCallTable(answer,page)
	})
} 

initialRequestSubordinate()

function createTvCallTable(data,page){
	var count = data.count;
	var data = data.results; 

    //paginations
    var paginations = '<li>Найдено ' + count + ' пользователей</li>';
    var pages = Math.ceil(count / config.pagination_count);
    if (pages > 1) {
        for (var j = 1; j < pages + 1; j++) {
            if (j == page) {
                paginations += '<li><span class="page active">  ' + j + '</span></li>'
            } else {
                paginations += '<li><span class="page">  ' + j + '</span></li>'
            }

        }
    }
    document.querySelector(".lineTabs").innerHTML = paginations;


    //Переключение пагинации
    [].forEach.call(document.querySelectorAll("span.page"), function(el) {
        el.addEventListener('click', function() {

           var page  = el.innerHTML;
           if(  window.user__master__id) {
           		showReports(window.user__master__id,page)
           }else{
           	initialRequestSubordinate(page)
           }
           


        });
    });

	var html = ''
	if ( data.length>0){
		//html += '<button  id="prev_home" class="prev_home">Моя таблица</button>';
		html += '<table class="tab1" id="userinfo">'
		html += createAtributes(data[0].attrs)
		for(var i = 0; i<data.length; i++){
			if( window.UrlData ){
				html += createRowFullStatistic(data[i])
				//html += createRow(data[i])
			}else{
				html += createRow(data[i])
			}
			
		}
		html += '</table>'
	}else{
		//html = '<button  id="prev_home" class="prev_home">Моя таблица</button>';
		html += '<span class="empty_list">По такому поиску результатов нет.</span>'
	}
	document.querySelector(".tab_content").innerHTML = html;
 


}

function createRow(data){

	var html = '<tr>'
		html +='<td>' + data.user_info.master_full_name + '</td>'
		html +='<td>' + data.user_info.user_fullname + '</td>'
		html +='<td>' + data.user_info.department + '</td>'		
		html +='<td>' + data.user_info.city + '</td>'
		html +='<td>' + data.user_info.hierarchy + '</td>'
		var date = new Date(data.date)
		var monthNames = ['января', 'февраля', 'марта', 'апреля',
			'мая', 'июня', 'июля', 'августа', 'сентября',
			'октября', 'ноября', 'декабря'
		]
		html +='<td>' + date.getDate() + " " + monthNames[date.getMonth()] + ' ' + date.getFullYear() + '</td>'
		html +='<td>' + data.user_info.phone_number + '</td>'
		html +='<td><input type="text" value="' + data.last_responce + '" onblur="updateLastCallResponce(this)" data-id="' + data.user_info.user_id + '"></td>';
		html += '<td><a href="'+ config.DOCUMENT_ROOT + 'account/'+ data.user_info.user_id + '" class="questionnaire" data-id="' + data.user_info.user_id + '">анкета</a></td>'
		html +='</tr>'
		return html
}

function createRowFullStatistic(data){


	var html = '<tr>'
		html +='<td>' + data.fullname + '</td>'
		html +='<td>' + data.department_title + '</td>'		
		html +='<td>' + data.city + '</td>'
		html +='<td>' + data.phone_number + '</td>'
		/*var date = new Date(data.date)
		var monthNames = ['января', 'февраля', 'марта', 'апреля',
			'мая', 'июня', 'июля', 'августа', 'сентября',
			'октября', 'ноября', 'декабря'
		]
		html +='<td>' + date.getDate() + " " + monthNames[date.getMonth()] + ' ' + date.getFullYear() + '</td>'
		*/
		html +='<td>' + data.last_week_calls + '</td>'
		html += '<td><a href="#" class="showReports" data-id="' + data.id + '" onclick="showReports('+data.id+')">статистика</a></td>'
		html += '<td><a href="'+ config.DOCUMENT_ROOT + 'account/'+ data.id + '" class="questionnaire" data-id="' + data.id + '">анкета</a></td>'

		html +='</tr>'
		return html

}

function showReports(id,page){

	var page = page || 1
	var url = 'api/tv_call/?user__department=&user__master__id=' + id +'&page=' + page;
	ajaxRequest(config.DOCUMENT_ROOT + url ,null ,function(answer) {
		window.UrlData = false;
		window.user__master__id  = id //GAVNO CODE!!!

		createTvCallTable(answer)
	})

}
function createAtributes(data){
	var html = '<tr>'
		for (var i=0; i<data.length; i++){
			html +='<th>' + data[i] + '</th>'
		}
		html +='<th>Анкеты</th></tr>'

		return html
}

function updateLastCallResponce(val){
	var id = val.getAttribute('data-id')
	var lastCallResponce = val.value
		postLastCallRequest(id, lastCallResponce)
}

function postLastCallRequest(id, text){
	ajaxRequest(config.DOCUMENT_ROOT+'api/update_last_call/',{'id':id, 'text_responce':text},function(answer) {
		console.log(answer)
	}, 'POST')
}

function findFormRequest(data){
	/*var data = {
		'user__first_name':'',
		'user__master':'',
		'user__hierarchy':'',
		'user__master__first_name':'',
		'user__phone_number':'',
		'user__city':'',
	}*/
	ajaxRequest(config.DOCUMENT_ROOT+'api/tv_call/',data,function(answer) {
		createTvCallTable(answer.results)
	})
}

//document.querySelector('.apply_find_tv').addEventListener("click", findInfo);
document.querySelector('#prev_home').addEventListener("click", function(){ 
	window.findData = {};
	window.user__master__id = null
	window.UrlData = false;
	initialRequestSubordinate()
});


document.querySelector('#statistic').addEventListener("click", function(){ 
	window.findData = {};
	window.UrlData = true;
	window.user__master__id = null
	initialRequestSubordinate()
});


/*function findInfo(e){
	findFormRequest(collectFindValue(e))
}

function collectFindValue(e){
	e.preventDefault()
	var data = {}
	var name = document.getElementsByName('name')[0].value;
	var last_name = document.getElementsByName('surname')[0].value;
	var middle_name = document.getElementsByName('secondname')[0].value;
	var tel = document.getElementsByName('tel')[0].value;
	var city = document.getElementsByName('city')[0].value;
		data['user__first_name'] =  name
		data['user__phone_number'] = tel
		data['user__city'] = city
		data['user__last_name'] = last_name
		data['user__middle_name'] = middle_name
		return data
}
*/
function getAllDepartments(){
	ajaxRequest(config.DOCUMENT_ROOT+'api/departments/',null ,function(answer) {
		document.getElementById('sandwich-find-form').innerHTML += createDropBoxDeapartment(answer.results)
	})
}

function createDropBoxDeapartment(data){
	var html = ''
		html +='<div class="sandwich-wrap" ><span class="sandwich-cont">Выберите отдел</span><span class="sandwich-button"></span><div class="sandwich-block"><ul>'
		for (var i=0; i<data.length;i++){
			html +='<li data-id="' + data[i].id + '"" onclick="filterDepartment(this)"><span>' + data[i].title + '</span><li>'
		}
		html +='</ul></div></div>'
		return html
	}

getAllDepartments()

function searchTableInfo(searchText){
	if (searchText.length>0){
		window.findData['search'] = searchText
		getFindINformation()
	}else{
		window.findData['search'] = ''
		getFindINformation()
	}
}

function filterDepartment(val){
	var id = val.getAttribute('data-id');
	if( window.UrlData  ){
		window.findData['department'] = id
	}else{
		window.findData['user__department'] = id
	}
	getFindINformation()
}

function getFindINformation(){
 
   if( window.UrlData  ){
   		ajaxRequest(config.DOCUMENT_ROOT+'api/tv_call_stat/',window.findData ,function(answer) {
			createTvCallTable(answer)
		});
   	return
   }
	ajaxRequest(config.DOCUMENT_ROOT+'api/tv_call/',window.findData ,function(answer) {
			createTvCallTable(answer)
		});
}

