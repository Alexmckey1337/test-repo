 var ordering = {};


$("document").ready(function() {
    createDepartmentsDropBox();
    createHierarhyDropBox();

    
    $('input[name="fullsearch"]').keyup(function() {

        delay(function() {
            createUser()
        }, 2500);



    });

    document.getElementById('showAll').addEventListener('click', function(e) {
        document.getElementsByName('fullsearch')[0].value = ''
        document.querySelector(".tab_content").innerHTML = ''
        e.preventDefault();
        document.getElementById('dropbox_wrap').innerHTML ='';
        createDepartmentsDropBox(); //???
        createHierarhyDropBox() //??
        createUser();
    })

        // createUser({'id':id})   
})

//Получение иерархий пользователя
function createDepartmentsDropBox() {

    ajaxRequest(config.DOCUMENT_ROOT + 'api/departments/', null, function(data) {
        var data = data.results
        var html = '<div class="sandwich-wrap department-wrap"><span class="sandwich-cont">Отдел</span>' +
            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
            html += '<li data-id=0 ><span>Все департаменти</span></li>'
        for (var i = 0; i < data.length; i++) {
            html += '<li data-id="' + data[i].id + '" ><span>' + data[i].title + '</span></li>'
        }
        html += '</ul></div></div>';
        document.getElementById('dropbox_wrap').innerHTML =
            document.getElementById('dropbox_wrap').innerHTML + html;
    });

}


function createHierarhyDropBox() {

    ajaxRequest(config.DOCUMENT_ROOT + 'api/hierarchy/', null, function(data) {
        var data = data.results;
        var html = '<div class="sandwich-wrap hierarchy-wrap"><span class="sandwich-cont">Ранг</span>' +
            '<span class="sandwich-button"></span><div class="sandwich-block"><ul>'
            html += '<li data-id=0 ><span>Все ранги</span></li>'
        for (var i = 0; i < data.length; i++) {
            html += '<li data-id="' + data[i].id + '" data-level="' + data[i].level + '"><span>' + data[i].title + '</span></li>';
        }
        html += '</ul></div></div>';
        document.getElementById('dropbox_wrap').innerHTML =
            document.getElementById('dropbox_wrap').innerHTML + html;

    });
}


function createUserInfoBySearch(data, search) {

    var count = data.count;
    var data = data.results;
    var tbody = '';

    var fullsearch = search.fullsearch;
    var page = search.page || 1;
    // var full = fullsearch === true ? '' : 'notfullsearch'
    var full = ''
    //Фільтр по параметрам для відображення
    var list = data;
    var html = '<table class="tab1 search ' + full + '" id="userinfo">';
    if (data.length == 0) {
        document.querySelector(".tab_content").innerHTML = 'по запросу не найдено участников';
        document.querySelector(".lineTabs").innerHTML = '';
        return;
    }

    var titles = Object.keys(data[0].fields);
    var common_ = list[0]['common']
    var common = Object.keys(list[0]['common']);
    html += '<thead>';

    for (var k = 0; k < titles.length; k++) {
        if (common.indexOf(titles[k]) === -1) continue

        if (ordering[common_[titles[k]]]) {
            html += '<th data-order="' + common_[titles[k]] + '" class="low"><span>' + titles[k] + '</span></th>';
        } else {
            html += '<th data-order="' + common_[titles[k]] + '"><span>' + titles[k] + '</span></th>';
        }

        //html += '<th data-order="' + common_[titles[k]] + '">' + titles[k] + '</th>';   
    }
    html += '<th></th><th></th></thead>';

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

    html += '<tbody>'
    for (var i = 0; i < list.length; i++) {
        var id_parent_subordinate = list[i]['id'];
        var list_fields = list[i].fields;

        tbody += '<tr>';
        for (var prop in list_fields) {


            if (prop == 'Facebook') {
                if (list_fields[prop]['value']) {
                    tbody += '<td><a class="facebook" href="' + list_fields[prop]['value'] + '">facebook</a></td>'
                } else {
                    tbody += '<td>&nbsp;</td>'
                }

            }
            if (!list_fields.hasOwnProperty(prop) || prop == 'id' || prop == 'Facebook') continue
            if (common.indexOf(prop) === -1) continue
            tbody += '<td  data-model="' + prop + '" data-type="' + list_fields[prop]['id'] + '">' + list_fields[prop]['value'] + '</td>';

        }
        tbody += '<td><a href="#" class="subordinate" data-id="' + id_parent_subordinate + '">подчиненные</a></td>';
        tbody += '<td><a href="' + config.DOCUMENT_ROOT + '/account/' + id_parent_subordinate + '" class="questionnaire" data-id="' + id_parent_subordinate + '">анкета</a></td>'

    }
    html += '</tbody>'
    html += '</table>';

    //Динамическая подгрузка
    /*
        if( page < pages  ){
           // html += '<input type="button" class="showMore"  data-page ="' + page +'" value="Показать больше">' 
        }

        
        if(  document.querySelector(".tab_content tbody")   ){
            var tbody =   document.querySelector(".tab_content tbody").innerHTML  + tbody;
        }
        */
    document.querySelector(".tab_content").innerHTML = html;
    document.querySelector(".tab_content tbody").innerHTML = tbody;


    [].forEach.call(document.querySelectorAll("span.page"), function(el) {
        el.addEventListener('click', function() {

            var data = search;
            data['page'] = el.innerHTML;
            data.fullsearch ? createUser(data, true) : createUser(data);


        });
    });
    //Показать больше
    /*
          [].forEach.call(document.querySelectorAll(".showMore"), function(el) {
            el.addEventListener('click', function(){

                var data = search;
                if( parseInt(el.getAttribute('data-page')) < pages  ){
                    data['page'] = parseInt(el.getAttribute('data-page')) + 1;
                    data.fullsearch ? createUser(data,true) : createUser(data);
                }

            });
        });
    */



    [].forEach.call(document.querySelectorAll(".subordinate"), function(el) {
        el.addEventListener('click', getsubordinates);
    });




    //Переробить сортировку

/*
    [].forEach.call(document.querySelectorAll(".tab_content .notfullsearch  th"), function(el) {
        el.addEventListener('click', function() {
            var data_order = this.getAttribute('data-order');
            //  var status = ordering[data_order] = ordering[data_order] ? false : true
            var status = false;
            if (ordering[data_order]) {
                status = false;
            } else {
                status = true
            }
            ordering = {};
            ordering[data_order] = status

            data_order = status ? data_order : '-' + data_order;
            createUser({
                'id': window.parent_id,
                'ordering': data_order
            })
        });
    })
*/
 
}

function createUser(data){
    var path = config.DOCUMENT_ROOT + 'api/users/?'
    var data = data ||  {}

    if( !data['sub'] &&  document.querySelector(" .hierarchy-wrap .sandwich-cont") && document.querySelector(".department-wrap .sandwich-cont")  ){
            var hierarchy = parseInt(document.querySelector(" .hierarchy-wrap .sandwich-cont").getAttribute('data-id')); 
            if(hierarchy){
                data['hierarchy'] = hierarchy
            }
            var department = parseInt(document.querySelector(".department-wrap .sandwich-cont").getAttribute('data-id'));
            if (department) {
                        data['department'] = department;
             }            
    }


    var search = document.getElementsByName('fullsearch')[0].value;
    if(search && !data['sub']){
        data['search'] = search;
    }
    ajaxRequest(path, data, function(answer) {
        createUserInfoBySearch(answer, data)
    })
}


function getsubordinates(e) {
    e.preventDefault();
    //Добавить очистку dropbox

    document.querySelector(".search_cont input").value = ''
    var id = this.getAttribute('data-id');
    createUser({
        'master': id,'sub':true
    });
    window.parent_id = id;

}
 
$(document).on('click', '.hierarchy-wrap .sandwich-block ul li span', function() {
  createUser()
})

$(document).on('click', '.department-wrap .sandwich-block ul li span', function() {
  createUser()
})