function init(user_id) {
    let id = getParameterByName('id');
    if (!id) {
        showPopup('Некоректный ID events');

        setTimeout(function () {
            window.location.href = 'events.html'
        }, 5000);
        return
    }
    $('body').on('click', '#carousel li span', function () {
        $('#carousel li').removeClass('active');
        $(this).parent().addClass('active')
    });

    getEventsListByID(id);
    let title = getParameterByName('title') || '';
    document.querySelector("span[title]").innerHTML = title;

    $('input[name="fullsearch"]').keyup(function () {

        delay(function () {
            //master ID
            createSubordinateList()
        }, 1500);
    });
    $("#done_datepicker_from").datepicker({
        dateFormat: "yy-mm-dd",
        maxDate: new Date(),
        onSelect: function (date) {
            getEventsListByID(id)
        }
    }).datepicker("setDate", '-1m');

    $("#done_datepicker_to").datepicker({
        dateFormat: "yy-mm-dd",
        onSelect: function (date) {
            getEventsListByID(id)
        }
    }).datepicker("setDate", '+2m');

    document.getElementById('sort_save').addEventListener('click', function () {
        updateSettings(createSubordinateList);
        $(".table-sorting").animate({
            right: '-300px'
        }, 10, 'linear')
    })
}

function createSubordinateList(data, event_id) {
    //переробить master_id
    data = data || {};
    let master_id = data['master_id'] || config.user_id;
    event_id = event_id || document.querySelector(".active span").getAttribute('data-event-id');
    //Для кожного  event_id свій
    let page = data['page'] || 1;

    let search = document.getElementsByName('fullsearch')[0].value;

    if (search && !data['sub']) {
        data['search'] = search;
        master_id = '';
    }
    document.getElementsByClassName('preloader')[0].style.display = 'block';

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/participations/disciples/?event=' + event_id +
        '&user__user__master=' + master_id, data, function (answer) {
        let html_sub = '';
        let results = answer.results;
        if (!results.length) {
            showPopup('По запросу нету пользователей');
            //document.getElementById('rows-list').innerHTML = 'Нету подчиненных'


            setTimeout(function () {
                //window.location.href = 'events.html'
                // window.location.reload();
            }, 5000);
            return
        }
        createUserInfoBySearch(answer, data);
        document.getElementsByClassName('preloader')[0].style.display = 'none';
    })
}

function createHierarchyChain(data) {
    let html = '';

    let index;
    for (index = data.length - 1; index >= 1; --index) {

        let current = data[index]['id'] == config.user_id ? 'is_current' : '';

        html += (index == 1) ? '<li class="active ' + current + '" data-id="' + data[index]['id'] + '"><h5>' + data[index]['value'] + '</h5></li>' :
            '<li class="' + current + '" data-id="' + data[index]['id'] + '"><h5>' + data[index]['value'] + '</h5></li>'
    }

    document.querySelector('.tabs-names ul').innerHTML = html;

    $('.is_current').prev().hide();

    Array.prototype.forEach.call(document.querySelectorAll(".tabs-names [data-id]"), function (el) {
        el.addEventListener('click', function () {
            let id = this.getAttribute('data-id');
            createSubordinateList({
                'master_id': id,
                'sub': true
            })
        })
    })
}

function getEventsListByID(id) {

    if (!id) {
        return
    }
    let data = {};

    let from_date = document.getElementById('done_datepicker_from').value;
    let to_date = document.getElementById('done_datepicker_to').value;
    data['to_date'] = to_date;
    data['from_date'] = from_date;

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/events/?event_type=' + id, data, function (data) {

        //Обработка если нету events
        let results = data.results;

        if (!results.length) {
            showPopup('У данного события не созданные встречи за данный период');
            setTimeout(function () {
                window.location.href = '/events/'
            }, 5000);
            return;
            //Слайдер перерисовать
        }

        createSliderEvent(results);
        //createVisitors()
    })
}

function createSliderEvent(data) {
    let html = '';
    for (let i = 0; i < data.length; i++) {
        if (i == 0) {
            html += '<li class="active"><span data-event-id=' + data[i].id + '>' + data[i].time + '</span></li>';
        } else {
            html += '<li><span data-event-id=' + data[i].id + '>' + data[i].time + '</span></li>';
        }

    }
    document.getElementById('date').innerHTML = html;
    //document.getElementById('summit-title').innerHTML = '<a href="summits_New.html">САММИТЫ | </a><span>' + data[0].title + '</span>';
    let width = 150,
        count = 1,
        carousel = document.getElementById('carousel'),
        list = carousel.querySelector('ul'),
        listElems = carousel.querySelectorAll('li'),
        position = 0;
    carousel.querySelector('.arrow-left').onclick = function () {
        position = Math.min(position + width * count, 0);
        list.style.marginLeft = position + 'px';
    };
    carousel.querySelector('.arrow-right').onclick = function () {
        if (listElems.length <= 3) {
            position = Math.max(position - width * count, -width * (listElems.length - listElems.length));
        } else {
            position = Math.max(position - width * count, -width * (listElems.length - 3));
        }
        list.style.marginLeft = position + 'px';
    };
    let butt = document.querySelectorAll('#carousel li span');
    for (let z = 0; z < butt.length; z++) {
        butt[z].addEventListener('click', function () {
            //let data = {};
            let id = this.getAttribute('data-event-id');
            createSubordinateList(null, id)
        })
    }
    document.querySelector("[data-event-id]").click()
}

let ordering = {};

function createUserInfoBySearch(data, search) {

    let count = data.count;

    let journal_table = Object.keys(data.common_table);

    data = data.results;
    let tbody = '';

    let page = parseInt(search.page) || 1;
    let list = data;
    let html = '<table id="userinfo">';
    if (data.length == 0) {
        showPopup('По данному запросу не найдено участников');
        document.querySelector(".table-wrap .table").innerHTML = '';
        document.querySelector(".query-none span[status]").innerHTML = 'По запросу не найдено участников';
        document.getElementById('total_count').innerHTML = '';
        document.getElementsByClassName('preloader')[0].style.display = 'none';
        Array.prototype.forEach.call(document.querySelectorAll(".pagination"), function (el) {
            el.style.display = 'none'
        });
        return;
    }

    let hierarchy_chain = data[0]['hierarchy_chain'];
    createHierarchyChain(hierarchy_chain);

    //нагавнячив
    Array.prototype.forEach.call(document.querySelectorAll(".pagination"), function (el) {
        el.style.display = 'block'
    });

    html += '<thead>';
    let common = config['column_table'];
    html += '<th>Присутсвие</th>';
    for (let title in config['column_table']) {
        if (!config['column_table'][title]['active'] && config['column_table'][title]['editable']) continue;

        let blue_icon = typeof  ordering['user__user__' + config['column_table'][title]['ordering_title']] == 'undefined' ? '' : 'blue_icon_active';

        if (ordering['user__user__' + config['column_table'][title]['ordering_title']]) {
            html += '<th data-order="user__user__' + config['column_table'][title]['ordering_title'] + '" ><span>' + config['column_table'][title]['title'] + '</span><span class="ups ' + blue_icon + '"></span></th>';
        } else {
            html += '<th data-order="user__user__' + config['column_table'][title]['ordering_title'] + '"  ><span>' + config['column_table'][title]['title'] + '</span><span class="ups ups-active ' + blue_icon + '"></span></th>';
        }
        if (title == 'fullname') {
            html += '<th class="title_sum">Сумма</th>';
        }
    }
    //html += '<th>Подчиненные</th><th>Анкета</th></thead>';

    //paginations
    let pages = Math.ceil(count / config.pagination_count);
    let paginations = '';
    if (page > 1) {
        paginations += '<div class="prev"></span><span class="arrow"></span></div>';
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

    document.getElementById('total_count').innerHTML = count;

    // document.getElementById("pag").innerHTML = paginations;
    Array.prototype.forEach.call(document.querySelectorAll(" .pag-wrap"), function (el) {
        el.innerHTML = paginations
    });

    html += '<tbody>';
    let html_sub = '';
    let cash = 0;
    for (let i = 0; i < list.length; i++) {
        let has_disciples = list[i].has_disciples ? 'has_disciples' : 'no_disciples';

        let id_parent_subordinate = list[i]['id'];
        let list_fields = list[i].fields;
        let id_sub = list[i].uid;
        let check = list[i].check ? 'checked' : '';
        if (!list_fields) continue;
        if (typeof list_fields === 'undefined') {
            console.log('Нету fields для  ID:  ' + id_parent_subordinate)
        }
        cash = list_fields['value'].value || 0;

        html_sub += '<div class="rows-wrap">'
            + '<button ' + has_disciples + ' data-id-sub=' + id_sub + ' >Подчинённые</button>' +
            '<div class="rows"><div class="col">' +
            '<p><span data-id="' + id_sub + '"><a href="/account/' + id_sub + '/">' + list_fields[journal_table[0]]["value"] + ' </a></span></p></div>' +
            '<div class="col">' +
            '<p>Пришло:<i class="total_visit">' + list_fields[journal_table[1]]["value"] + '</i>человек</p> ' +
            '<p>Сумма:<input type="text" maxlength="4" onkeypress="return event.charCode >= 48 && event.charCode <= 57" disabled data-value="' + cash + '" data-id="' + id_parent_subordinate + '" class="upd_sum" type="text" value="' + cash + '"></p>' + '<span class="change"></span><span class="x"></span><span class="y"></span></div></div></div>';
        tbody += '<tr >';
        //  tbody += '<td><input type="checkbox" ' + check + ' class="update_visit" data-id="' + id_parent_subordinate + '"></td>'

        tbody += '<td style="text-align:center;"><input id="visits_' + id_sub + '" type="checkbox"   ' + check + ' class="update_visit" data-id="' + id_parent_subordinate + '"><label for="visits_' + id_sub + '" class="check"></label></td>';

        for (let prop in config['column_table']) {
            if (prop in list_fields) {
                if (prop == 'social' && config['column_table']['social'] && config['column_table']['social']['active']) {
                    tbody += '<td>';
                    for (let pr in list_fields[prop]) {
                        if (list_fields[prop][pr] == '') {
                            continue
                        } else {
                            switch (pr) {
                                case 'skype':
                                    tbody += '<a href="skype:' + list_fields[prop].skype + '?chat"><i class="fa fa-skype"></i></a>';
                                    break;
                                case 'vkontakte':
                                    tbody += '<a href="' + list_fields[prop].vkontakte + '"><i class="fa fa-vk"></i></a>';
                                    break;
                                case 'facebook':
                                    tbody += '<a href="' + list_fields[prop].facebook + '"><i class="fa fa-facebook"></i></a>';
                                    break;
                                case 'odnoklassniki':
                                    tbody += '<a href="' + list_fields[prop].odnoklassniki + '"><i class="fa fa-odnoklassniki" aria-hidden="true"></i></a>';
                                    break;
                            }
                        }
                    }
                    tbody += '</td>';
                } else if ((!config['column_table'][prop]['active'] && config['column_table'][prop]['editable'])) {
                    continue;
                } else if (prop == 'fullname') {
                    tbody += '<td><a href="/account/' + list_fields['id']['value'] + '">' + list_fields[prop]['value'] + '</a>' + '<span title="Подчиненные" ' + has_disciples + ' data-id-sub="' + id_sub + '" class="pod"></span>' + '</td><td><div style="position:relative" class="col"><input type="text" maxlength="4" onkeypress="return event.charCode >= 48 && event.charCode <= 57" disabled data-value="' + cash + '" data-id="' + id_parent_subordinate + '" class="upd_sum" type="text" value="' + cash + '"></p>' + '<span class="change"></span><span class="x"></span><span class="y"></span></div></td>';
                } else {
                    tbody += '<td>' + list_fields[prop]['value'] + '</td>';
                }
            }
        }
    }
    html += '</tbody>';
    html += '</table>';

    //document.getElementById('rows-list').innerHTML = html_sub

    document.getElementById("event_id_wrap").innerHTML = html;
    document.querySelector("#event_id_wrap tbody").innerHTML = tbody;
    //document.querySelector(".query-none p").innerHTML = ''
    document.getElementsByClassName('preloader')[0].style.display = 'none';


    Array.prototype.forEach.call(document.querySelectorAll(" .pag li"), function (el) {
        el.addEventListener('click', function () {
            if (this.className == 'no-pagin') {
                return false;
            }
            let data = search;
            data['page'] = el.innerHTML;
            createSubordinateList(data)
        });
    });

    Array.prototype.forEach.call(document.querySelectorAll(" .update_visit"), function (el) {
        el.addEventListener('click', function () {
            let id = parseInt(this.getAttribute('data-id'));
            let checked = !!this.checked;
            let data = {
                'id': id,
                'check': checked
            };
            update_visit(data)
        })
    });
    // Navigation/

    Array.prototype.forEach.call(document.querySelectorAll(".arrow"), function (el) {
        el.addEventListener('click', function () {
            let page;
            let data = search;
            if (this.parentElement.classList.contains('prev')) {
                page = parseInt(document.querySelector(".pag li.active").innerHTML) > 1 ? parseInt(document.querySelector(".pag li.active").innerHTML) - 1 : 1;
                data['page'] = page;
                createSubordinateList(data)
            } else {
                page = parseInt(document.querySelector(".pag li.active").innerHTML) != pages ? parseInt(document.querySelector(".pag li.active").innerHTML) + 1 : pages;
                data['page'] = page;
                createSubordinateList(data)
            }

        })
    });

    Array.prototype.forEach.call(document.querySelectorAll(".double_arrow"), function (el) {
        el.addEventListener('click', function () {
            let data = search;
            if (this.parentElement.classList.contains('prev')) {
                data['page'] = 1;
                createSubordinateList(data)
            } else {
                data['page'] = pages;
                createSubordinateList(data)
            }
        })
    });

    Array.prototype.forEach.call(document.querySelectorAll("[data-id-sub][has_disciples]"), function (el) {
        el.addEventListener('click', function () {
            let id = this.getAttribute('data-id-sub');
            createSubordinateList({
                'master_id': id,
                'sub': true
            })
        });
    });

    /*Edit value */
    Array.prototype.forEach.call(document.querySelectorAll(".change"), function (el) {
        el.addEventListener('click', function () {
            this.style.display = 'none';
            this.nextElementSibling.style.display = 'block';
            this.nextElementSibling.nextElementSibling.style.display = 'block';
            this.parentElement.querySelector("input").removeAttribute('disabled')
        });
    });

    Array.prototype.forEach.call(document.querySelectorAll(".x"), function (el) {
        el.addEventListener('click', function () {

            this.previousElementSibling.style.display = 'block';
            this.nextElementSibling.style.display = 'none';
            this.style.display = 'none'
            this.parentElement.querySelector("input").setAttribute('disabled', 'disabled');
            this.parentElement.querySelector("input").value = this.parentElement.querySelector("input").getAttribute('data-value');
        });
    });

    Array.prototype.forEach.call(document.querySelectorAll(".y"), function (el) {
        el.addEventListener('click', function () {

            this.previousElementSibling.style.display = 'none';
            this.previousElementSibling.previousElementSibling.style.display = 'block';
            this.style.display = 'none';
            this.parentElement.querySelector("input").setAttribute('disabled', 'disabled');
            //this.parentElement.querySelector("input").value= this.parentElement.querySelector("input").getAttribute('data-value');
            this.parentElement.querySelector("input").setAttribute('data-value', this.parentElement.querySelector("input").value);


            let id = parseInt(this.parentElement.querySelector("input").getAttribute('data-id'));
            let value = parseInt(this.parentElement.querySelector("input").value);
            let data = {
                'id': id,
                'value': value
            };
            update_visit(data)

        });
    });

    //Cортировка

    Array.prototype.forEach.call(document.querySelectorAll(".table-wrap   th"), function (el) {
        el.addEventListener('click', function () {
            let data_order = this.getAttribute('data-order');
            //  let status = ordering[data_order] = ordering[data_order] ? false : true
            let status = false;
            if (ordering[data_order]) {
                status = false;
            } else {
                status = true
            }
            ordering = {};
            ordering[data_order] = status;
            data_order = status ? data_order : '-' + data_order;
            let page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1;
            let data = {
                'ordering': data_order,
                'master_id': parseInt(document.querySelector(".tabs-names li.active").getAttribute('data-id'))
            };
            createSubordinateList(data)
        });
    })
}

function update_visit(data) {

    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/update_participations/', json, function (JSONobj) {

    }, 'POST', true, {
        'Content-Type': 'application/json'
    });

}