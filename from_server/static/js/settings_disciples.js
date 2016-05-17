function createUserInfoBySearch(data, count,fullsearch,page) {
    var full = fullsearch === true ? '' : 'notfullsearch'
    //Фільтр по параметрам для відображення
    var list = data;
    var html = '<table class="tab1 search ' + full + '" id="userinfo">';
    if (data.length == 0) {
        document.querySelector(".tab_content").innerHTML = 'по запросу не найдено участников';
        return;
    }

    var titles = Object.keys(data[0].fields);
    var common_ = list[0]['common'];
    var common = Object.keys(list[0]['common']);
    html += '<tr>';

    for (var k = 0; k < titles.length; k++) {
        if (common.indexOf(titles[k]) === -1) continue
        html += '<th data-order="' + common_[titles[k]] + '">' + titles[k] + '</th>';
    }
    html += '<th></th><th></th></tr>';

    //paginations
    var paginations = '<li>Найдено '+ count +' пользователей</li>';
    var pages = Math.ceil( count/20 );
    for(var j = 1;j<pages+1;j++){
       if(j == page){
        paginations += '<li><span class="page active">  '+ j +'</span></li>'
       } else{
        paginations += '<li><span class="page">  '+ j +'</span></li>'
       }
       
    }  
    document.querySelector(".lineTabs").innerHTML = paginations;

    for (var i = 0; i < list.length; i++) {
        var id_parent_subordinate = list[i]['id'];
        var list_fields = list[i].fields;

        html += '<tr>';
        for (var prop in list_fields) {

            if (!list_fields.hasOwnProperty(prop) || prop == 'id') continue
            if (common.indexOf(prop) === -1) continue
            html += '<td  data-model="' + prop + '" data-type="' + list_fields[prop]['id'] + '">' + list_fields[prop]['value'] + '</td>'
        }
        html += '<td><a href="#" class="subordinate" data-id="' + id_parent_subordinate + '">подчиненные</a></td>';
        html += '<td><a href="http://vocrm.org/account/' + id_parent_subordinate + '" class="questionnaire" data-id="' + id_parent_subordinate + '">анкета</a></td>'

    }
    html += '</table>'
    document.querySelector(".tab_content").innerHTML = html;

   // document.querySelector(".lineTabs").innerHTML = '<li>По запросу найдено '+ list.length  +' участников</li>';

    
   [].forEach.call(document.querySelectorAll("span.page"), function(el) {
        el.addEventListener('click', function(){

            if(fullsearch){
                createUser(null, null, null,true,el.innerHTML)
            }else{
                createUser(null, null, null,null,el.innerHTML)
            }
           
        });
    });


    [].forEach.call(document.querySelectorAll(".subordinate"), function(el) {
        el.addEventListener('click', getsubordinates);
    });

    [].forEach.call(document.querySelectorAll(".tab_content .notfullsearch  th"), function(el) {
        el.addEventListener('click', function() {
            var data_order = this.getAttribute('data-order');
            if (window.location.hash) {
                var ordering = JSON.parse(window.location.hash.slice(1))
            } else {
                var ordering = {}
            }
            var status = ordering[data_order] = ordering[data_order] ? false : true
            var ordering = JSON.stringify(ordering)
            window.location.hash = ordering
            createUser(window.parent_id, data_order, status)
        });
    })

}

function getsubordinates(e) {
    e.preventDefault()
    var id = this.getAttribute('data-id');
    createUser(id);
    window.parent_id = id;

}

function createHierarhyDropBox() {
    var hierarchy_level = document.getElementsByClassName('admin_name')[0].getAttribute('data-hierarchy-level');

    ajaxRequest(config.DOCUMENT_ROOT+'api/hierarchy/', null, function(data) {
        var data = data.results;
        var html = '<div class="sandwich-wrap"><span class="sandwich-cont" data-model="master_leaderships__hierarchy">Сотник</span>' +
            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
        for (var i = 0; i < data.length; i++) {
            html += '<li data-id="' + data[i].id + '"><span>' + data[i].title + '</span></li>'
        }
        html += '</ul></div></div>';
        document.getElementById('sandwich-wrap-wrapper').innerHTML =
            document.getElementById('sandwich-wrap-wrapper').innerHTML + html;

    });

    ajaxRequest(config.DOCUMENT_ROOT+'api/departments/', null, function(data) {
        var data = data.results;
        var html = '<div class="sandwich-wrap"><span class="sandwich-cont" data-model="master_leaderships__department">Сотник</span>' +
            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
        for (var i = 0; i < data.length; i++) {
            html += '<li data-id="' + data[i].id + '"><span>' + data[i].title + '</span></li>'
        }
        html += '</ul></div></div>';
        document.getElementById('sandwich-wrap-wrapper').innerHTML =
            document.getElementById('sandwich-wrap-wrapper').innerHTML + html;

    });
}

    document.getElementById('showAll').addEventListener('click', function(e){
        e.preventDefault();
        createUser(null,null,null,true);
    })


$(".apply").click(function(e) {
    e.preventDefault();
    createUser();

});

function createUser(id, order, data_order_reverse,allUsers,page) {
    var name = document.getElementsByName('name')[0].value;
    var last_name = document.getElementsByName('surname')[0].value;
    var middle_name = document.getElementsByName('secondname')[0].value;
    var tel = document.getElementsByName('tel')[0].value;
    var email = document.getElementsByName('email')[0].value;
    var master_id = id || document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
    var page = page || 1 
    var fullsearch = false
/*
    var is_staff = false //document.getElementsByClassName('admin_name')[0].getAttribute('data-staff-status');
    if (is_staff && !id) {
        var path = config.DOCUMENT_ROOT+'api/users/'
    } else {
        var path = config.DOCUMENT_ROOT+'api/users/?master=' + master_id;
    }
*/
    var path  =config.DOCUMENT_ROOT+'api/users/?master=' + master_id;
    if (order) {
        var path = config.DOCUMENT_ROOT+'api/users/?master=' + master_id + '&ordering=' + order;
        if (data_order_reverse) {
            var path = config.DOCUMENT_ROOT+'api/users/?master=' + master_id + '&ordering=-' + order;
        } 
    }
    path = path + '&page=' + page;
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
    if( name || last_name || tel || email ){
    	  path = config.DOCUMENT_ROOT+'api/users/' + '?page=' + page
          //fullsearch = true
    }
    if(  allUsers ){
         path = config.DOCUMENT_ROOT+'api/users/all' + '?page=' + page;
         fullsearch = true
    }

    [].forEach.call(document.querySelectorAll(".search_cont input"), function(el) {
        el.value = '';
    });
    ajaxRequest(path, data, function(answer) {
        createUserInfoBySearch(answer.results,answer.count,fullsearch,page)
    })
}


