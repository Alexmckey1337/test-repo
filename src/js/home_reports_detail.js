(function ($) {
    let $databaseHomeReportsForm = $('#databaseHomeReportsForm');
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];
    $('.preloader').hide();
    function makeHomeReportDetailTable(data) {
        let tmpl = $('#databaseHomeReports').html();
        let rendered = _.template(tmpl)(data);
        $('#homeReports').html(rendered);
        // makeSortForm(data.table_columns);
    }

    function getHomeReportDetailData(config = {}) {
        return new Promise(function (resolve, reject) {
            let data = {
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/${REPORTS_ID}`,
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: config
            };
            let status = {
                200: function (req) {
                    resolve(req);
                },
                403: function () {
                    reject('Вы должны авторизоватся');
                }

            };
            newAjaxRequest(data, status);
        })
    }

    function getHomeReportDetailTableData(config = {}) {
        return new Promise(function (resolve, reject) {
            let data = {
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/${REPORTS_ID}/visitors`,
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: config
            };
            let status = {
                200: function (req) {
                    resolve(req);
                },
                403: function () {
                    reject('Вы должны авторизоватся');
                }

            };
            newAjaxRequest(data, status);
        })
    }

    getHomeReportDetailData().then(data => {
        console.log(data);
        if (data.status === 1) {
            getHomeReportDetailTableData().then(data => {
                makeHomeReportDetailTable(data);
            });
        } else {
            $('#save').text('Редактировать').attr('data-click', false);
            let field = {
                results: data.attends,
                table_columns: data.table_columns
            };
            makeHomeReportDetailTable(field);
        }
        let container = document.createElement('div');
        let ownerContainer = document.createElement('p');
        let ownerTitle = document.createElement('label');
        let ownerData = document.createElement('input');
        $(ownerTitle).text('Лидер: ');
        $(ownerData).val(data.owner.fullname).attr({
            'size': data.owner.fullname.length + 3,
            'disabled': true
        });
        $(ownerContainer).append(ownerTitle).append(ownerData);
        $(container).append(ownerContainer);

        let groupContainer = document.createElement('p');
        let groupTitle = document.createElement('label');
        let groupData = document.createElement('input');
        $(groupTitle).text('Домашняя группа: ');
        $(groupData).val(data.home_group.title).attr({
            'size': data.home_group.title.length + 3,
            'data-name': 'false',
            'disabled': true
        });
        $(groupContainer).append(groupTitle).append(groupData);
        $(container).append(groupContainer);

        let dateContainer = document.createElement('p');
        let dateTitle = document.createElement('label');
        let dateData = document.createElement('input');
        $(dateTitle).text('Дата отчёта: ');
        $(dateData).val(data.date).attr({
            'size': data.date.length,
            'data-name': 'date',
        }).datepicker();
        $(dateContainer).append(dateTitle).append(dateData);
        $(container).append(dateContainer);
        if (data.type.code != 'service') {
            let amountContainer = document.createElement('p');
            let amountTitle = document.createElement('label');
            let amountData = document.createElement('input');
            $(amountTitle).text('Сумма пожертвований: ');
            $(amountData).val(data.total_sum).attr({
                'size': 7,
                'data-name': 'total_sum',
            });
            $(amountContainer).append(amountTitle).append(amountData);
            $(container).append(amountContainer);
        }
        $('#additionalInformation').html(container);
    });

    $('#save').on('click', function () {
        let btn = $(this);
        if (btn.attr('data-click') == "false") {
            btn.attr({
                'data-click': true,
                'data-update': true,
            });
            btn.text('Сохранить');
            return false;
        }
        let data = {};

        $('#additionalInformation').find('input').each(function () {
            let field = $(this).data('name');
            if (field) {
                console.log(field);
                if(field == 'date') {
                    data[field] = $(this).val().split('.').reverse().join('-');
                } else {
                    data[field] = $(this).data('value') || $(this).val();
                }
            }
        });

        // $('#databaseHomeReportsForm').on('submit', function (e) {
        //     e.preventDefault();
        //     console.log(e);
        //     let data = $(this).serializeArray();
        //     console.log(data);
        //     return false;
        // });
        //
        // // $('#databaseHomeReportsForm').find('.submitBtn').trigger('click');


        let $items = $('#databaseHomeReportsForm').find('tbody').find('tr');
        let attends = [];
        $items.each(function () {
            let $input = $(this).find('input');
            let data = {};
            $input.each(function () {
                let elem = $(this);
                let name = elem.attr('name');
                if (name == 'attended') {
                    data[elem.attr('name')] = elem.prop("checked")
                } else if (name == 'user') {
                    data[elem.attr('name')] = parseInt(elem.val());
                } else {
                    data[elem.attr('name')] = elem.val();
                }
            });
            attends.push(data);
        });
        data.attends = attends;
        console.log(btn.attr('data-update'));
        if (btn.attr('data-update') == 'true') {
            updateReports(JSON.stringify(data)).then((data) => {
                console.log(data);
                btn.attr({
                    'data-click': false,
                    'data-update': false,
                });
                btn.text('Редактировать');
            });
        } else {
            submitReports(JSON.stringify(data)).then((data) => {
                console.log(data);
                btn.text('Редактировать');
            });
        }


    });
    $('.submitBtn').on('click', function (e) {
        e.preventDefault();
        console.log(e);
    });

    function submitReports(config) {
        return new Promise((resolve, reject) => {
            let data = {
                method: 'POST',
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/${REPORTS_ID}/submit/`,
                data: config,
                contentType: 'application/json',
            };
            let status = {
                200: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }
            };
            newAjaxRequest(data, status, reject)
        })
    }

    function updateReports(config) {
        return new Promise((resolve, reject) => {
            let data = {
                method: 'PUT',
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/${REPORTS_ID}/`,
                data: config,
                contentType: 'application/json',
            };
            let status = {
                200: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }
            };
            newAjaxRequest(data, status, reject)
        })
    }
})(jQuery);