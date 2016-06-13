$(function() {
    //createUser({'master':user_id}) ;
    $('input[name="fullsearch"]').keyup(function() {

        delay(function() {
            createUser()
        }, 1500);
    });

    $('input[name="searchDep"]').keyup(function() {

        delay(function() {
            createUserDep()
        }, 1500);
    });

    document.getElementById('sort_save').addEventListener('click', function() {
        updateSettings(createUser);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    })

    


});


var ordering = {}
var parent_id = null

function createUserInfoBySearch(data, search) {

    var count = data.count;
    var data = data.results;
    var tbody = '';
    var page = parseInt(search.page) || 1;
    var list = data;
    var html = '<table id="userinfo">';
    if (data.length == 0) {

        showPopup('По данному запросу не найдено участников')
        document.getElementById("baseUsers").innerHTML = '';
        document.querySelector(".query-none p").innerHTML = 'По запросу не найдено участников';
        document.getElementById('total_count').innerHTML = count;
        document.getElementsByClassName('preloader')[0].style.display = 'none'
        Array.prototype.forEach.call(document.querySelectorAll(".pagination"), function(el) {
            el.style.display = 'none'
        })
        document.querySelector(".element-select").innerHTML = elementSelect = '<p>Показано <span>' + data.length + '</span> из <span>' + count + '</span></p>';
        document.getElementsByClassName('preloader')[0].style.display = 'none';
        return;
    }

    //нагавнячив
    Array.prototype.forEach.call(document.querySelectorAll(".pagination"), function(el) {
        el.style.display = 'block'
    })

    html += '<thead>';
    var common = config['column_table']
    for (var title in config['column_table']) {
        if (!config['column_table'][title]['active'] && config['column_table'][title]['editable']) continue

        var blue_icon = typeof  ordering[config['column_table'][title]['ordering_title']]  == 'undefined' ? '' : 'blue_icon_active'  
   // console.log(typeof  ordering[config['column_table'][title]['ordering_title']]  == 'undefined')

        if (ordering[config['column_table'][title]['ordering_title']]) {
            html += '<th data-order="' + config['column_table'][title]['ordering_title'] + '" class="down"><span>' + config['column_table'][title]['title'] + '</span><span class="ups '+ blue_icon  +'"></span></th>';
        } else {
            html += '<th data-order="' + config['column_table'][title]['ordering_title'] + '"    class="up"><span>' + config['column_table'][title]['title'] + '</span><span class="ups ups-active '+ blue_icon +'"></span></th>';
        }
    }
  //  html += '<th>Подчиненные</th><th>Анкета</th></thead>';

    //paginations
    var pages = Math.ceil(count / config.pagination_count);
    var paginations = '',
    elementSelect = '<p>Показано <span>' + data.length + '</span> из <span>' + count + '</span></p>';
    if (page > 1) {
        paginations += '<div class="prev"><span class="arrow"></span></div>';
    }
    if (pages > 1) {
        paginations += '<ul class="pag">'

        if( page > 4){
                     paginations += '<li>1</li><li class="no-pagin">&hellip;</li>'
                }

        for (var j = page - 2; j < page + 3; j++) {

             

            if (j == page) {
                paginations += '<li class="active">' + j + '</li>'
            } else {
                if (j > 0 && j < pages + 1) {
                    paginations += '<li>' + j + '</li>'
                }
            }

        }
                     if( page < pages - 3){
                     paginations += '<li class="no-pagin">&hellip;</li>'

                     if(  page <pages-3  ){
                        paginations += '<li>'+ pages +'</li>'
                     }

                    
                }
        paginations += '</ul>'
    }

    if (page < pages) {
        paginations += '</ul><div class="next"><span class="arrow"></span></div>'
    }
    document.querySelector(".element-select").innerHTML = elementSelect;
    document.getElementById('total_count').innerHTML = count;

    // document.getElementById("pag").innerHTML = paginations;
    Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function(el) {
        el.innerHTML = paginations
    })

    html += '<tbody>'
    for (var i = 0; i < list.length; i++) {
        var id_parent_subordinate = list[i]['id'];
        var list_fields = list[i].fields;
        if (!list_fields) continue
        if (typeof list_fields === 'undefined') {
            console.log('Нету fields для  ID:  ' + id_parent_subordinate)
        }
        tbody += '<tr data-id="'+ id_parent_subordinate  +'">';
        for (var prop in config['column_table']) {
            if (prop in list_fields) {
                if (prop == 'social' && config['column_table']['social'] && config['column_table']['social']['active']) {   
                        tbody += '<td>';                                      
                        for (var p in list_fields[prop]) {
                            if (list_fields[prop][p] == '') {
                                continue
                            } else {
                                switch (p) {
                                  case 'skype':
                                    tbody += '<a href="skype:'+list_fields[prop].skype+'?chat"><i class="fa fa-skype"></i></a>';
                                    break;
                                  case 'vkontakte':
                                    tbody += '<a href="'+list_fields[prop].vkontakte+'"><i class="fa fa-vk"></i></a>';
                                    break;
                                  case 'facebook':
                                    tbody += '<a href="'+list_fields[prop].facebook+'"><i class="fa fa-facebook"></i></a>';
                                    break;
                                  case 'odnoklassniki':
                                    tbody += '<a href="'+list_fields[prop].odnoklassniki+'"><i class="fa fa-odnoklassniki" aria-hidden="true"></i></a>';
                                    break;
                                } 
                            }
                        }
                        tbody += '</td>';                                                                      
                    } else if ((!config['column_table'][prop]['active'] && config['column_table'][prop]['editable'])) {
                        continue;
                    } else if (prop == 'fullname') {
                        tbody += '<td><a href="/account/'+id_parent_subordinate+'">' + list_fields[prop]['value'] + '</a></td>'
                    } else {
                        tbody += '<td>' + list_fields[prop]['value'] + '</td>';  
                    }
               }
        }
    }
    html += '</tbody>'
    html += '</table>';

    document.getElementById("baseUsers").innerHTML = html;
    document.querySelector("#baseUsers tbody").innerHTML = tbody;
    document.querySelector(".query-none p").innerHTML = ''
    document.getElementsByClassName('preloader')[0].style.display = 'none'
    Array.prototype.forEach.call(document.querySelectorAll(" .pag li"), function(el) {
        el.addEventListener('click', function() {
            if (this.className == 'no-pagin') {
                return false;
            }
            var data = search;
            data['page'] = el.innerHTML;
            createUser(data);
        });
    });

    $('.no-pagin').unbind();

    Array.prototype.forEach.call(document.querySelectorAll(".subordinate"), function(el) {
        el.addEventListener('click', getsubordinates);
    });

    /* Navigation*/

    Array.prototype.forEach.call(document.querySelectorAll(".arrow"), function(el) {
        el.addEventListener('click', function() {
            var page
            var data = search;
            if (this.parentElement.classList.contains('prev')) {
                page = parseInt(document.querySelector(".pag li.active").innerHTML) > 1 ? parseInt(document.querySelector(".pag li.active").innerHTML) - 1 : 1
                data['page'] = page
                createUser(data);
            } else {
                page = parseInt(document.querySelector(".pag li.active").innerHTML) != pages ? parseInt(document.querySelector(".pag li.active").innerHTML) + 1 : pages
                data['page'] = page
                createUser(data);
            }

        })
    });

    Array.prototype.forEach.call(document.querySelectorAll(".double_arrow"), function(el) {
        el.addEventListener('click', function() {
            var data = search;
            if (this.parentElement.classList.contains('prev')) {
                data['page'] = 1
                createUser(data);
            } else {
                data['page'] = pages
                createUser(data);
            }
        })
    });

    //Cортировка


    Array.prototype.forEach.call(document.querySelectorAll(".table-wrap   th"), function(el) {
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
            var page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1
            var data = {
                'ordering': data_order,
                'page': page
            }
            createUser(data)
        });
    })




document.getElementById('add').addEventListener('click',function(){
    document.querySelector('.pop-up-splash').style.display = 'block';
})

}

function createUser(data) {
    var path = config.DOCUMENT_ROOT + 'api/users/?'
    var data = data || {}
    var search = document.getElementsByName('fullsearch')[0].value;
    if (search && !data['sub']) {
        data['search'] = search;
    }
    document.getElementsByClassName('preloader')[0].style.display = 'block'
    ajaxRequest(path, data, function(answer) {
        //  document.getElementsByClassName('preloader')[0].style.display = 'block'
        createUserInfoBySearch(answer, data)
    })
}

function createUserDep(data) {
    var path = config.DOCUMENT_ROOT + 'api/users/?'
    var data = data || {}
    var search = document.getElementsByName('searchDep')[0].value;
    if (search && !data['sub']) {
        data['department__title'] = search;
    }
    document.getElementsByClassName('preloader')[0].style.display = 'block'
    ajaxRequest(path, data, function(answer) {
        //  document.getElementsByClassName('preloader')[0].style.display = 'block'
        createUserInfoBySearch(answer, data)
    })
}

//Получение подчиненных
function getsubordinates(e) {
    e.preventDefault();
    document.getElementsByName('fullsearch')[0].value = ''
    var id = this.getAttribute('data-id');
    createUser({
        'master': id
    });
    window.parent_id = id;

}
