$(document).ready(function(){

    if (document.getElementById('summits')) {
        create_summit_buttons('summits');
    }		

	$('body').on('click', '#summit_buttons li', function(){
		$(this).addClass('active');
		var summit_id = $(this).attr('data-id');
		createSummits({'summit' : summit_id})
		window.summit = summit_id;
	});

    $('input[name="fullsearch"]').keyup(function() {
        delay(function() {
            var data = {};
            data['summit'] = summit_id;
            getUsersList(data);
        }, 1500);
    });

    $('#searchUsers').keyup(function() {
            getUnregisteredUsers();
    });

    $('body').on('click', '#carousel li span', function(){
        $('#carousel li').removeClass('active');
        $(this).parent().addClass('active')
    })

    if(document.getElementById('sort_save')) {
        document.getElementById('sort_save').addEventListener('click', function() {
            updateSettings(getUsersList);
            $(".table-sorting").animate({
                right: '-300px'
            }, 10, 'linear')
        })
    }

    if (document.querySelector('.table-wrap')) {

    document.querySelector(".add").addEventListener('click', function() {
        document.querySelector('.add-user-wrap').style.display = 'block';
    })



    document.querySelector("#popup h3 span").addEventListener('click', function() {
        document.querySelector('#popup').style.display = 'none';
        document.querySelector('.choose-user-wrap').style.display = 'block';
    })

    document.querySelector("#close").addEventListener('click', function() {
        document.querySelector('#popup').style.display = 'none';
        document.querySelector('.choose-user-wrap').style.display = 'block';
    })

    document.querySelector("#closeDelete").addEventListener('click', function() {
        document.querySelector('#popupDelete').style.display = 'none';
    })

    document.querySelector(".add-user-wrap .top-text span").addEventListener('click', function() {
        document.querySelector('.add-user-wrap').style.display = '';
    })

    document.querySelector(".add-user-wrap").addEventListener('click', function(el) {
        if (el.target !== this) {
            return;
        }
        document.querySelector('.add-user-wrap').style.display = '';
    })

    document.querySelector("#popupDelete").addEventListener('click', function(el) {
        if (el.target !== this) {
            return;
        }
        document.querySelector('#popupDelete').style.display = '';
    })

    document.querySelector("#popupDelete .top-text span").addEventListener('click', function(el) {
        document.querySelector('#popupDelete').style.display = '';
    })

    document.querySelector(".choose-user-wrap").addEventListener('click', function(el) {
        if (el.target !== this) {
            return;
        }
        document.querySelector('.choose-user-wrap').style.display = '';
        document.getElementById('searchUsers').value = '';
        document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
    })

    document.querySelector(".choose-user-wrap .top-text > span").addEventListener('click', function() {
        document.getElementById('searchUsers').value = '';
        document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
        document.querySelector('.choose-user-wrap').style.display = '';
    })

    document.getElementById('choose').addEventListener('click', function() {
        document.querySelector('.choose-user-wrap').style.display = 'block';
        document.querySelector('.add-user-wrap').style.display = '';
    })

    document.querySelector('.choose-user-wrap h3 span').addEventListener('click', function() {
        document.getElementById('searchUsers').value = '';
        document.querySelector('.choose-user-wrap .splash-screen').classList.remove('active');
        document.querySelector('.choose-user-wrap').style.display = '';
        document.querySelector('.add-user-wrap').style.display = 'block';
    })

    document.getElementById('add_new').addEventListener('click',function(){
        document.querySelector('.pop-up-splash-add').style.display = 'block';
    })

    document.getElementById('changeSum').addEventListener('click', function() {
        document.getElementById('summit-value').removeAttribute('readonly');
        document.getElementById('summit-value').focus();
    })

    document.getElementById('changeSumDelete').addEventListener('click', function() {
        document.getElementById('summit-valueDelete').removeAttribute('readonly');
        document.getElementById('summit-valueDelete').focus();
    })

    document.getElementById('deleteAnket').addEventListener('click', function() {
        var summitAnket = this.getAttribute('data-anket');
        unsubscribe(summitAnket);
    })

    document.getElementById('completeDelete').addEventListener('click', function() {
        var id = this.getAttribute('data-id'),
            money = document.getElementById('summit-valueDelete').value,
            description = document.querySelector('#popupDelete textarea').value;
        registerUser(id,summit_id,money,description);
        document.querySelector('#popupDelete').style.display = 'none';
    })

    document.getElementById('complete').addEventListener('click', function() {
        var id = this.getAttribute('data-id'),
            money = document.getElementById('summit-value').value,
            description = document.querySelector('#popup textarea').value;
        registerUser(id,summit_id,money,description);
        document.querySelector('#popup').style.display = 'none';
        document.querySelector('.choose-user-wrap').style.display = 'block';
    })

    addSummitInfo();
}
});

var summit_id;
var ordering = {};
var order;

function unsubscribe(id) {
    var data = {
                "id": id
            }
    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT+'api/summit_ankets/delete_anket/', json, function(JSONobj) {
            if(JSONobj.status){
                var data = {};
                data['summit'] = summit_id;
                getUsersList(data);
                document.querySelector('#popupDelete').style.display = 'none';
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
}

function registerUser(id,summit_id,money, description) {
      var data = {
                "user_id": id,
                "summit_id": summit_id,
                "value": money,
                "description": description
            }
        var json = JSON.stringify(data);
        ajaxRequest(config.DOCUMENT_ROOT+'api/summit_ankets/post_anket/', json, function(JSONobj) {
            if(JSONobj.status){
                var data = {};
                data['summit'] = summit_id;
                getUsersList(data);
                getUnregisteredUsers();
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
}

function getUnregisteredUsers(parameters) {
    var param = parameters || {};
    var search = document.getElementById('searchUsers').value;
    if (search) {
        param['search'] = search;
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/summit_search/?summit_id!=' + summit_id, param, function(data) {
        var html = '';
        for (var i = 0; i < data.length; i++) {
            html += '<div class="rows-wrap"><button data-master="' + data[i].master_short_fullname + '" data-name="' + data[i].fullname + '" data-id="' + data[i].id + '">Выбрать</button><div class="rows"><div class="col"><p><span><a href="/account/'+ data[i].id +'">' + data[i].fullname + '</a></span></p></div><div class="col"><p><span>' + data[i].country + '</span>,<span> ' + data[i].city + '</span></p></div></div></div>';
        }
        if (data.length > 0) {
            document.getElementById('searchedUsers').innerHTML = html;
        } else {
            document.getElementById('searchedUsers').innerHTML = '<div class="rows-wrap"><div class="rows"><p>По запросу не найдено учасников</p></div></div>';
        }
        document.querySelector('.choose-user-wrap .splash-screen').classList.add('active');  
        var but = document.querySelectorAll('.rows-wrap button');
        for (var j = 0; j < but.length; j++) {
            but[j].addEventListener('click', function() {
                var id = this.getAttribute('data-id'),
                    name = this.getAttribute('data-name'),
                    master = this.getAttribute('data-master')
                document.getElementById('summit-value').value = "0";
                document.getElementById('summit-value').setAttribute('readonly','readonly');
                document.querySelector('#popup textarea').value = "";
                getDataForPopup(id, name, master);
                document.getElementById('popup').style.display = 'block';
                document.querySelector('.choose-user-wrap').style.display = 'none';
            })
        } 
    });
}

function getDataForPopup(id, name, master) {
    document.getElementById('complete').setAttribute('data-id', id);
    document.getElementById('client-name').innerHTML = name;
    document.getElementById('responsible-name').innerHTML = master;
}

function create_summit_buttons(id){
        ajaxRequest(config.DOCUMENT_ROOT + 'api/summit_types/', null, function(data) {
            var data = data.results;
            var html = '';
            for (var i = 0; i < data.length; i++) {
                html += '<div><img data-id="' + data[i].id + '" src="'  + data[i].image + '" alt="" /></div>';
            }
            html += '</ul></div>';
            document.getElementById(id).innerHTML = html;
            var img = document.querySelectorAll('#summits img');
    		for (var i = 0; i < img.length; i++) {
    			img[i].addEventListener( "click" , function() {
    				location.href = '/summit_info/' + this.getAttribute('data-id');
    			});
    		}
        });    
	}

function addSummitInfo() {
	var id = document.location.href.split('/')[document.location.href.split('/').length - 2];
	ajaxRequest(config.DOCUMENT_ROOT + 'api/summit/?type=' + id, null, function(data) {
        var data = data.results,
        	html = '';        	
        for (var i = 0; i < data.length; i++) { 
        	if (i == 0) {
        		html += '<li class="active"><span data-id='+data[i].id+'>' + data[i].start_date + '</span></li>';
        	} else {
        		html += '<li><span data-id='+data[i].id+'>' + data[i].start_date + '</span></li>';
        	}
        	
        }
        document.getElementById('date').innerHTML = html;
        document.getElementById('summit-title').innerHTML = '<a href="/summits">САММИТЫ | </a><span>' + data[0].title + '</span>'; 
        var width = 150,
    		count = 1,
    		carousel = document.getElementById('carousel'),
    		list = carousel.querySelector('ul'),
    		listElems = carousel.querySelectorAll('li'),
    		position = 0;         
    	carousel.querySelector('.arrow-left').onclick = function() {
    		position = Math.min(position + width * count, 0)
      		list.style.marginLeft = position + 'px';
    	};
    	carousel.querySelector('.arrow-right').onclick = function() {
      		position = Math.max(position - width * count, -width * (listElems.length - 3));
      		list.style.marginLeft = position + 'px';
    	};   
    	var butt = document.querySelectorAll('#carousel li span');
        for (var z = 0; z < butt.length; z++) {
        	butt[z].addEventListener('click', function(){
        		var data = {};
        		data['summit'] = this.getAttribute('data-id');
                window.summit_id = data['summit'];
        		getUsersList(data);
        	})
        } 	
    });
}

function getUsersList(param) {
    var param = param || {};
    var path = config.DOCUMENT_ROOT + 'api/summit_ankets/?'
    var search = document.getElementsByName('fullsearch')[0].value;
    if (search) {
        param['search'] = search;
    }
    param['summit'] = summit_id;
    document.getElementsByClassName('preloader')[0].style.display = 'block';
    ajaxRequest(path, param, function(data) {

        var results = data.results;
        var count = data.count;
        if (results.length == 0) {
            document.getElementById('users_list').innerHTML = 'По запросу не найдено учасников';
            document.querySelector(".element-select").innerHTML = elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
            document.getElementsByClassName('preloader')[0].style.display = 'none';
            return;
        }
        var common_fields = results[0].common;
        var html = '';
        var thead = '<table><thead><tr>';
        var common = config['column_table'];
        
        for (var title in config['column_table']) {
            if (!config['column_table'][title]['active'] && config['column_table'][title]['editable']) continue
            var blue_icon = typeof  ordering[config['column_table'][title]['ordering_title']]  == 'undefined' ? '' : 'blue_icon_active'
            if (ordering[config['column_table'][title]['ordering_title']]) {
                thead += '<th data-order="' + config['column_table'][title]['ordering_title'] + '" class="down"><span>' + config['column_table'][title]['title'] + '</span><span class="ups '+ blue_icon  +'"></span></th>';;
            } else {
                thead += '<th data-order="' + config['column_table'][title]['ordering_title'] + '" class="up"><span>' + config['column_table'][title]['title'] + '</span><span class="ups ups-active '+ blue_icon +'"></span></th>';
            }
        }
        for (var x in common_fields) {
            thead += '<th data-order="' + common_fields[x] + '"    class="up"><span>' + x + '</span></th>';
        }
        
        for (var i = 0; i < results.length; i++) {
            var list_fields = results[i].info;
            if (!list_fields) continue
            html += '<tr data-anketId=' + list_fields.money_info.summit_anket_id + ' data-value=' + list_fields.money_info.value + ' data-comment=' + list_fields.money_info.description + '>';
            for (var prop in config['column_table']) {
                if (prop in list_fields) {                    
                    if (prop == 'social' && config['column_table']['social'] && config['column_table']['social']['active']) {   
                        html += '<td>';                                      
                        for (var p in list_fields[prop]) {
                            if (list_fields[prop][p] == '') {
                                continue
                            } else {
                                switch (p) {
                                  case 'skype':
                                    html += '<a href="skype:'+list_fields[prop].skype+'?chat"><i class="fa fa-skype"></i></a>';
                                    break;
                                  case 'vkontakte':
                                    html += '<a target="_blank" href="'+list_fields[prop].vkontakte+'"><i class="fa fa-vk"></i></a>';
                                    break;
                                  case 'facebook':
                                    html += '<a href="'+list_fields[prop].facebook+'"><i class="fa fa-facebook"></i></a>';
                                    break;
                                  case 'odnoklassniki':
                                    html += '<a href="'+list_fields[prop].odnoklassniki+'"><i class="fa fa-odnoklassniki" aria-hidden="true"></i></a>';
                                    break;
                                } 
                            }
                        }
                        html += '</td>';                                                                      
                    } else if ((!config['column_table'][prop]['active'] && config['column_table'][prop]['editable'])) {
                        continue;
                    } else if (prop == 'fullname') {
                        html += '<td><a href="/account/'+list_fields['id']['value']+'">' + list_fields[prop]['value'] + '</td>'
                    } else {
                        html += '<td>' + list_fields[prop]['value'] + '</td>';  
                    }                   
                    
                                 
                }                                
            }
            for (var z in common_fields) {
                for (var s in list_fields) {
                    if (common_fields[z] == list_fields[s].verbose) {
                        html += '<td>' + list_fields[s].value + '</td>';                            
                    }
                }
            }
            html += '</tr>';
        }

        thead += '</thead><tbody></tbody></table>';

        var page = parseInt(param['page']) || 1,
            pages = Math.ceil(count / config.pagination_count),
            paginations = '',
            elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
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

        document.getElementById('users_list').innerHTML = thead;
        document.querySelector("#users_list tbody").innerHTML = html;
        document.querySelector(".element-select").innerHTML = elementSelect;
        document.getElementsByClassName('preloader')[0].style.display = 'none';
        Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function(el) {
            el.innerHTML = paginations;
        });

        $('#users_list tr').click(function(el){
            if (el.target.nodeName == 'A') {
                return;
            }
            var id = $(this).children().children('a').attr('href').split('/')[2],
                usr = $(this).children().children('a').html(),
                anketa = $(this).attr('data-anketId'),
                val = $(this).attr('data-value'),
                comment = $(this).attr('data-comment');
            $('#completeDelete').attr('data-id',id);
            $('#deleteAnket').attr('data-anket',anketa);
            $('#summit-valueDelete').val(val);
            $('#popupDelete textarea').val(comment);
            $('#popupDelete h3').html(usr);
            document.querySelector('#popupDelete').style.display = 'block';
        })

        Array.prototype.forEach.call(document.querySelectorAll(" .pag li"), function(el) {
            el.addEventListener('click', function() {
                if (this.className == 'no-pagin') {
                    return false;
                }
                var data = {};
                data['summit'] = summit_id;
                data['page'] = el.innerHTML;
                data['ordering'] = order;
                getUsersList(data);
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll(".pag-wrap p > span"), function(el) {
            el.addEventListener('click', function() {
                var data = {};
                data['summit'] = summit_id;
                data['page'] = el.innerHTML;
                data['ordering'] = order;
                getUsersList(data);
            });
        });       

        /* Navigation*/

        Array.prototype.forEach.call(document.querySelectorAll(".arrow"), function(el) {
            el.addEventListener('click', function() {
                var page;
                var data = {};
                if (this.parentElement.classList.contains('prev')) {
                    page = parseInt(document.querySelector(".pag li.active").innerHTML) > 1 ? parseInt(document.querySelector(".pag li.active").innerHTML) - 1 : 1;
                    data['page'] = page;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    getUsersList(data);
                } else {

                    page = parseInt(document.querySelector(".pag li.active").innerHTML) != pages ? parseInt(document.querySelector(".pag li.active").innerHTML) + 1 : pages;
                    data['page'] = page;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    getUsersList(data);
                }
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll(".double_arrow"), function(el) {
            el.addEventListener('click', function() {
                var data = {};
                if (this.parentElement.classList.contains('prev')) {
                    data['page'] = 1;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    getUsersList(data);
                } else {
                    data['page'] = pages;
                    data['summit'] = summit_id;
                    data['ordering'] = order;
                    getUsersList(data);
                }
            });
        });

        Array.prototype.forEach.call(document.querySelectorAll(".table-wrap   th"), function(el) {
        el.addEventListener('click', function() {
            var data_order = this.getAttribute('data-order');
            var status = false;
            if (ordering[data_order]) {
                status = false;
            } else {
                status = true
            }
            ordering = {};
            ordering[data_order] = status
            data_order = status ? 'user__' + data_order : '-' + 'user__' + data_order;
            window.order = data_order;
            var page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1
            var data = {
                'ordering': data_order,
                'page': page,
                'summit': summit_id
            }
            getUsersList(data)
            });
        })
    });
}
    