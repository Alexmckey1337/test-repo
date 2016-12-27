$(function () {
    //buttons events
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });

    $('.selectdb').select2();
    $('input[name="fullsearch"]').keyup(function () {
        delay(function () {
            createUser()
        }, 1500);
    });

    $('input[name="searchDep"]').keyup(function () {
        delay(function () {
            createUserDep();
        }, 1500);
    });

    document.getElementById('sort_save').addEventListener('click', function () {
        updateSettings(createUser);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    });

    document.getElementById('dep_filter').addEventListener('change', function () {
        createUser()
    });
});

function getCurrentUserSetting(data) {
    let sortFormTmpl, obj, rendered;
    obj = {};
    sortFormTmpl = document.getElementById("sortForm").innerHTML;
    obj = {};
    obj.user = data[0];
    rendered = _.template(sortFormTmpl)(obj);
    document.getElementById('sort-form').innerHTML = rendered;
}

function reversOrder(order) {
    if (order.charAt(0) == '-') {
        order = order.substring(1)
    } else {
        order = '-' + order
    }
    return order
}

let ordering = {};
let parent_id = null;

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

    let count = data.count;
    let page = parseInt(search.page) || 1;
    let ordering = search.ordering || 'last_name';
    let tordering;
    if (ordering.indexOf('-') != -1) {
        tordering = ordering.substr(1)
    } else {
        tordering = ordering
    }

    let results = data.results;

    let k,
        value;

    let user_fields = data.user_table;

    getCurrentUserSetting([['Пользователь', user_fields]]);

    //paginations
    let pages = Math.ceil(count / config.pagination_count);
    let paginations = '',
        elementSelect = '<p>Показано <span>' + results.length + '</span> из <span>' + count + '</span></p>';
    if (page > 1) {
        paginations += '<div class="prev"><span class="arrow"></span></div>';
    }
    if (pages > 1) {
        paginations += '<ul class="pag">';

        if (page > 4) {
            paginations += '<li>1</li><li class="no-pagin">&hellip;</li>'
        }

        for (let j = page - 2; j < page + 3; j++) {
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

    Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function (el) {
        el.innerHTML = paginations
    });
    
    var tmpl = document.getElementById('databaseUsers').innerHTML;
    var result = _.template(tmpl)(data);

    document.getElementById("baseUsers").innerHTML = result;

    document.querySelector(".query-none p").innerHTML = '';
    document.getElementsByClassName('preloader')[0].style.display = 'none';
    Array.prototype.forEach.call(document.querySelectorAll(" .pag li"), function (el) {
        el.addEventListener('click', function () {
            if (this.className == 'no-pagin') {
                return false;
            }
            let data = search;
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
            let page;
            let data = search;
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
            let data = search;
            if (this.parentElement.classList.contains('prev')) {
                data['page'] = 1;
                createUser(data);
            } else {
                data['page'] = pages;
                createUser(data);
            }
        })
    });

    // Cортировка
    Array.prototype.forEach.call(document.querySelectorAll(".table-wrap th"), function (el) {
        el.addEventListener('click', function () {
            let data_order = this.getAttribute('data-order');
            let status = !!ordering[data_order];

            ordering = {};
            ordering[data_order] = status;
            // data_order = status ? data_order : '-' + data_order;
            let page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1;
            let data = {
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
    let path = config.DOCUMENT_ROOT + 'api/v1.1/users/?';
    data = data || {};
    let search = document.getElementsByName('fullsearch')[0].value;
    if (search && !data['sub']) {
        data.search_fio = search;
    }
    let el = document.getElementById('dep_filter');
    let value = 0;

    if (parseInt(value)) {
        data['department'] = value;
    }
    $('.preloader').css('display', 'block');

    ajaxRequest(path, data, function (answer) {
        createUserInfoBySearch(answer, data);
    });
}
//Получение подчиненных
function getsubordinates(e) {
    e.preventDefault();
    document.getElementsByName('fullsearch')[0].value = '';
    let id = this.getAttribute('data-id');
    createUser({
        'master': id
    });
    window.parent_id = id;
}