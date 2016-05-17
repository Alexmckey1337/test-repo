function createUserInfoBySearch(data, flag) {
    var html = '<table class="tab1 search" id="userinfo">';
    if (!data.results.length) {
        document.querySelector(".tab_content").innerHTML = '<span class="empty_list">нет подчиненныx пользвателей</span>';
        return;
    }
    var my_reports = data.results[0].my_reports;
    var titles = Object.keys(my_reports)
    html += '<tr>';

    for (var k = 0; k < titles.length; k++) {
        if (titles[k] == 'url' || titles[k] == 'id') continue
        html += '<th>' + titles[k] + '</th>';
    }
    html += '<th>Подчиненные</th><th>Анкеты</th></tr>'
    for (var i = 0; i < data.results.length; i++) {

        html += '<tr data-id="' + data.results[i]['id'] + '">';
        for (var prop in data.results[i].my_reports) {
            html += '<td>' + data.results[i].my_reports[prop]['value'] + '</td>'

        }
        html += '<td><a href="#" class="subordinate">подчиненные</a></td><td><a href="http://vocrm.org/account/' + data.results[i]['id'] + '" class="report_id">анкета</a></td>'
        html += '</tr>';
    }
    html += '</table>'

    document.querySelector(".tab_content").innerHTML = html;
    //Фільтр по параметрам для відображення


    [].forEach.call(document.querySelectorAll(".subordinate"), function(el) {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            var id = $(this).parents('tr').attr('data-id');
            createUser(id)
        });
    });

}


$(".apply").click(function(e) {
    e.preventDefault();
    createUser();

});

function createUser(id) {
    var name = document.getElementsByName('name')[0].value;
    var last_name = document.getElementsByName('surname')[0].value;
    var middle_name = document.getElementsByName('secondname')[0].value;
    var tel = document.getElementsByName('tel')[0].value;
    var email = document.getElementsByName('email')[0].value;
    var master_id = id || document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
    var is_staff = document.getElementsByClassName('admin_name')[0].getAttribute('data-staff-status');

    /*
    if(is_staff && !id){
    	 var path  = config.DOCUMENT_ROOT+'api/users/'
    }else{
    		var path  =config.DOCUMENT_ROOT+'api/users/?master=' + master_id;
    }
    */
    var path = config.DOCUMENT_ROOT+'api/users/?master=' + master_id;
    var data = {}
    if (name) {
        data['first_name'] = name;
    }
    if (last_name) {
        data['last_name'] = last_name
    }
    if (middle_name) {
        data['middle_name'] = middle_name
    }
    if (tel) {
        data['phone_number'] = tel;
    }
    if (email) {
        data['email'] = email;
    }
    ajaxRequest(path, data, function(answer) {
        createUserInfoBySearch(answer)
    })
}