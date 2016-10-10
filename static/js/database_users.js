$(function () {
    //createUser({'master':user_id}) ;
    $('input[name="fullsearch"]').keyup(function () {

        delay(function () {
            createUser()
        }, 1500);
    });

    $('input[name="searchDep"]').keyup(function () {

        delay(function () {
            createUserDep()
        }, 1500);
    });

    document.getElementById('sort_save').addEventListener('click', function () {
        updateSettings(createUser);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });


    getDepartmentsAll();

    document.getElementById('dep_filter').addEventListener('change', function () {
        createUser()

    })
});


var ordering = {};
var parent_id = null;

function createUserInfoBySearch(data, search) {

    if (data.length == 0) {
        showPopup('По данному запросу не найдено участников');
        document.getElementById("baseUsers").innerHTML = '';
        document.querySelector(".query-none p").innerHTML = 'По запросу не найдено участников';
        document.getElementById('total_count').innerHTML = count;
        document.getElementsByClassName('preloader')[0].style.display = 'none';
        Array.prototype.forEach.call(document.querySelectorAll(".pagination"), function (el) {
            el.style.display = 'none'
        });
        document.querySelector(".element-select").innerHTML = '<p>Показано <span>' + data.length + '</span> из <span>' + count + '</span></p>';
        document.getElementsByClassName('preloader')[0].style.display = 'none';
        return;
    }

    //нагавнячив
    Array.prototype.forEach.call(document.querySelectorAll(".pagination"), function (el) {
        el.style.display = 'block'
    });

    var count = data.count;
    var page = parseInt(search.page) || 1;

    var results = data.results;

    var k;
    var value;

    var user_fields = data.user_table;

    var thead = '<thead><tr>';

    for (k in user_fields) {
        if (!user_fields.hasOwnProperty(k)) continue;
        thead += '<th data-order="' + user_fields[k]['ordering_title'] + '">' + user_fields[k]['title'] + '</th>'
    }
    thead += '</tr></thead>';

    var tbody = '<tbody>';
    results.forEach(function (field) {
        tbody += '<tr>';

        for (k in user_fields) {
            if (!user_fields.hasOwnProperty(k)) continue;
            value = getCorrectValue(field[k]);
            tbody += '<td>' + value + '</td>'
        }
        tbody += '</tr>';
    });
    tbody += '</tbody>';

    var table = '<table id="userinfo">' + thead + tbody + '</table>';

    //paginations
    var pages = Math.ceil(count / config.pagination_count);
    var paginations = '',
        elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
    if (page > 1) {
        paginations += '<div class="prev"><span class="arrow"></span></div>';
    }
    if (pages > 1) {
        paginations += '<ul class="pag">';

        if (page > 4) {
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
        if (page < pages - 3) {
            paginations += '<li class="no-pagin">&hellip;</li>';

            if (page < pages - 3) {
                paginations += '<li>' + pages + '</li>'
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
    Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function (el) {
        el.innerHTML = paginations
    });

    document.getElementById("baseUsers").innerHTML = table;
    document.querySelector(".query-none p").innerHTML = '';
    document.getElementsByClassName('preloader')[0].style.display = 'none';
    Array.prototype.forEach.call(document.querySelectorAll(" .pag li"), function (el) {
        el.addEventListener('click', function () {
            if (this.className == 'no-pagin') {
                return false;
            }
            var data = search;
            data['page'] = el.innerHTML;
            createUser(data);
        });
    });

    $('.no-pagin').unbind();

    Array.prototype.forEach.call(document.querySelectorAll(".subordinate"), function (el) {
        el.addEventListener('click', getsubordinates);
    });

    /* Navigation*/
    Array.prototype.forEach.call(document.querySelectorAll(".arrow"), function (el) {
        el.addEventListener('click', function () {
            var page;
            var data = search;
            if (this.parentElement.classList.contains('prev')) {
                page = parseInt(document.querySelector(".pag li.active").innerHTML) > 1 ? parseInt(document.querySelector(".pag li.active").innerHTML) - 1 : 1;
                data['page'] = page;
                createUser(data);
            } else {
                page = parseInt(document.querySelector(".pag li.active").innerHTML) != pages ? parseInt(document.querySelector(".pag li.active").innerHTML) + 1 : pages;
                data['page'] = page;
                createUser(data);
            }

        })
    });

    Array.prototype.forEach.call(document.querySelectorAll(".double_arrow"), function (el) {
        el.addEventListener('click', function () {
            var data = search;
            if (this.parentElement.classList.contains('prev')) {
                data['page'] = 1;
                createUser(data);
            } else {
                data['page'] = pages;
                createUser(data);
            }
        })
    });

    //Cортировка

    Array.prototype.forEach.call(document.querySelectorAll(".table-wrap th"), function (el) {
        el.addEventListener('click', function () {
            var data_order = this.getAttribute('data-order');
            var status = !!ordering[data_order];

            ordering = {};
            ordering[data_order] = status;
            data_order = status ? data_order : '-' + data_order;
            var page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1;
            var data = {
                'ordering': data_order,
                'page': page
            };
            createUser(data)
        });
    });

    document.getElementById('add').addEventListener('click', function () {
        document.querySelector('.pop-up-splash').style.display = 'block';
    })
}

function createUser(data) {
    var path = config.DOCUMENT_ROOT + 'api/nusers/?';
    data = data || {};
    var search = document.getElementsByName('fullsearch')[0].value;
    var filter = document.getElementById('filter').value;
    if (search && !data['sub']) {
        data[filter] = search;
    }

    var el = document.getElementById('dep_filter');
    var value = el.options[el.selectedIndex].value;
    if (parseInt(value)) {
        data['department__title'] = el.options[el.selectedIndex].text;
    }
    document.getElementsByClassName('preloader')[0].style.display = 'block';
    ajaxRequest(path, data, function (answer) {
        //  document.getElementsByClassName('preloader')[0].style.display = 'block'
        createUserInfoBySearch(answer, data);
    });
    /*
     function createUserDep(data) {
     var path = config.DOCUMENT_ROOT + 'api/nusers/?';
     data = data || {};
     var search = document.getElementsByName('searchDep')[0].value;
     if (search && !data['sub']) {
     data['department__title'] = search;
     }
     document.getElementsByClassName('preloader')[0].style.display = 'block';
     ajaxRequest(path, data, function (answer) {
     createUserInfoBySearch(answer, data)
     })
     }
     */
}
//Получение подчиненных
function getsubordinates(e) {
    e.preventDefault();
    document.getElementsByName('fullsearch')[0].value = '';
    var id = this.getAttribute('data-id');
    createUser({
        'master': id
    });
    window.parent_id = id;

}