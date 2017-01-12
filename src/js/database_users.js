$('document').ready(function () {
    //buttons events
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });
    $('.popap').on('click', function () {
        $(this).css('display', 'none');
    });
    $('#quickEditCartPopup').find('.close').on('click', function () {
        let $input = $(this).closest('.pop_cont').find('input');
        let $select = $(this).closest('.pop_cont').find('select');
        let $button = $(this).closest('.pop_cont').find('.save-user');
        let $info = $(this).closest('.pop_cont').find('.info');
        $button.css('display', 'inline-block');
        $button.removeAttr('disabled');
        $button.text('Сохранить');
        $info.each(function () {
            $(this).css('display', 'none');
        });
        $input.each(function () {
            $(this).removeAttr('readonly');
        });
        $select.each(function () {
            $(this).removeAttr('disabled');
        });
        getStatuses.then(function (data) {
            data = data.results;
            let hierarchySelect = $('#hierarchySelect').val();
            let html = "";
            for (let i = 0; i < data.length; i++) {
                if(hierarchySelect === data[i].title || hierarchySelect == data[i].id) {
                    html += '<option value="' + data[i].id + '"' + 'selected' + '>' + data[i].title + '</option>';
                } else {
                    html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
                }
            }
            $('#hierarchySelect').html(html);
        });
        getDepartments.then(function (data) {
            data = data.results;
            let departmentSelect = $('#departmentSelect').val();
            let html = "";
            for (let i = 0; i < data.length; i++) {
                if( departmentSelect == data[i].title || departmentSelect == data[i].id) {
                    html += '<option value="' + data[i].id + '"' + 'selected' + '>' + data[i].title + '</option>';
                } else {
                    html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
                }
            }
            $('#departmentSelect').html(html);
        });
        $("#repentance_date").datepicker({
            dateFormat: "yy-mm-dd"
        })
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
});

function getCurrentUserSetting(data) {
    let sortFormTmpl, obj, rendered;
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

$('#sort_save').on('click', function () {
    updateSettings(createUser);
});

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
    var rendered = _.template(tmpl)(data);

    // quick edit event
    setTimeout(function () {
        var timer = 0;
        var delay = 200;
        var prevent = false;
        $('.quick-edit')
            .on('click', function () {
                var _self = this;
                makeQuickEditCart(_self);
            })
    }, 1000);

    document.getElementById("baseUsers").innerHTML = rendered;


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
    var orderTable = (function () {
        function addListener() {
            $(".table-wrap th").on('click', function () {
                let dataOrder;
                let data_order = this.getAttribute('data-order');
                var revers = (sessionStorage.getItem('revers')) ? sessionStorage.getItem('revers') : "+";
                var order = (sessionStorage.getItem('order')) ? sessionStorage.getItem('order') : '';
                if (order != '') {
                    dataOrder = (order == data_order && revers == "+") ? '-' + data_order : data_order;
                } else {
                    dataOrder = '-' + data_order;
                }
                ordering = {};
                ordering[data_order] = dataOrder;
                let page = document.querySelector(".pag li.active") ? parseInt(document.querySelector(".pag li.active").innerHTML) : 1;
                let data = {
                    'ordering': dataOrder,
                    'page': page
                };
                if (order == data_order) {
                    revers = (revers == '+') ? '-' : '+';
                } else {
                    revers = "+"
                }
                sessionStorage.setItem('revers', revers);
                sessionStorage.setItem('order', data_order);

                createUser(data);
            });
        }

        return {
            addListener: addListener
        }
    })();
    orderTable.addListener();
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
    let extendData = $.extend({}, data, filterParam());

    $('.preloader').css('display', 'block');

    ajaxRequest(path, extendData, function (answer) {
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
