function getNotifications () {
	ajaxRequest(config.DOCUMENT_ROOT+'api/notifications/', null, createAllNotifications);
}

function createAllNotifications(data){
	var html = ''
		html += '<ul>'
		for(var i = 0; i < data.results.length; i++){
			html += createUniqueNotification(data.results[i])
			}
		html += '</ul>'
		document.getElementById('notifications').innerHTML = html
	}

function createUniqueNotification(obj){
	var html =''
		html += '<li><strong class="topic_event">' + obj.theme + '</strong>';
		html += '<ul class="event_info"><li><span class="left_info">Описание</span><span class="right_info">' + obj.description + '</span></li>'
		html += createDateOrDate(obj) + '</ul></li>'
		return html
	}

function createPeriodNames(periodType){
	var array = new Array()
		if (periodType == 'week_days'){
			array[0] = "Пн";
			array[1] = "Вт";
			array[2] = "Ср";
			array[3] = "Чт";
			array[4] = "Пт";
			array[5] = "Сб";
			array[6] = "Вс";
		}else if (periodType == 'year_months'){
			array[0] = "Январь";
			array[1] = "Февраль";
			array[2] = "Март";
			array[3] = "Апрель";
			array[4] = "Май";
			array[5] = "Июнь";
			array[6] = "Июль";
			array[7] = "Август";
			array[8] = "Сентябрь";
			array[9] = "Октябрь";
			array[10] = "Ноябрь";
			array[11] = "Декабрь";
		}
		return array;
	}

function createDateOrDate(obj){
	var html = ''
	var week = createPeriodNames('week_days')
		if(obj.date){
			html = '<li><span class="left_info">Дата</span><span class="right_info ">' + obj.date + '</span></li>'
		}else if(obj.date === null & obj.day.length>0){
			html =  '<li><span class="left_info">День</span><span class="right_info ">' + week(obj.date-1) + '</span></li>'
		}
		return html
	}

	getNotifications()