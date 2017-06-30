/* globals moment */
(function ($) {
    let $additionalInformation = $('#additionalInformation'),
        $homeReports = $('#homeReports');
    let dist = {
        night: "О Ночной молитве",
        home: "Домашней группы",
        service: "О Воскресном Служении"
    };

    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    function makeHomeReportDetailTable(data) {
        let tmpl = $('#databaseHomeReports').html();
        let rendered = _.template(tmpl)(data);
        $homeReports.html(rendered);
    }

    function getHomeReportDetailData(config = {}) {
        return new Promise(function (resolve, reject) {
            let data = {
                url: URLS.event.home_meeting.detail(REPORTS_ID),
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
                url: URLS.event.home_meeting.visitors(REPORTS_ID),
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
        if (data.status === 1 || data.status === 3) {
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
            let $input = $homeReports.find('input');
            $input.each(function () {
                $(this).attr('disabled', true);
            })
        }
        $additionalInformation.html(makeCaption(data));
        if(!data.can_submit) {
            showPopup(data.cant_submit_cause);
            $('#save').attr({
                disabled: true
            });
            $homeReports.on('click', 'input', function () {
                showPopup(data.cant_submit_cause);
            });
        }
    });

    $('#save').on('click', function () {
        let btn = $(this),
            data = {};
        if (btn.attr('data-click') == "false") {
            btn.attr({
                'data-click': true,
                'data-update': true,
            });
            $homeReports.find('input').each(function () {
                $(this).attr('disabled', false);
            });

            btn.text('Сохранить');
            return false;
        }

        $additionalInformation.find('input').each(function () {
            let field = $(this).data('name');
            if (field) {
                if (field == 'date') {
                    data[field] = $(this).val().split('.').reverse().join('-');
                } else {
                    data[field] = $(this).data('value') || $(this).val();
                }
            }
        });

        let $items = $homeReports.find('tbody').find('tr');
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

        sendForms(btn, data);
    });
    $('.submitBtn').on('click', function (e) {
        e.preventDefault();
    });

    function submitReports(config) {
        return new Promise((resolve, reject) => {
            let data = {
                method: 'POST',
                url: URLS.event.home_meeting.submit(REPORTS_ID),
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
                url: URLS.event.home_meeting.detail(REPORTS_ID),
                data: config,
                contentType: 'application/json',
            };
            let status = {
                200: function (req) {
                    resolve(req)
                },
                403: function (err) {
                    reject(err)
                },
                400: function (err) {
                    reject(err)
                }
            };
            newAjaxRequest(data, status, reject)
        })
    }
    function makeCaption(data) {
        let container = document.createElement('div');
        let title = document.createElement('h2');
        if(data.status === 1 ) {
            $(title).text(`Подача отчета ${dist[data.type.code]}`);
        }
        if (data.status === 2 ) {
            $(title).text(`Отчет ${dist[data.type.code]}`);
        }
        if (data.status === 3 ) {
             $(title).html(`Отчет ${dist[data.type.code]} <span>(просрочен)</span>`);
        }
        $(container).append(title);
        let ownerContainer = document.createElement('p');
        let ownerTitle = document.createElement('span');
        let ownerData = document.createElement('a');
        $(ownerTitle).text('Лидер: ');
        $(ownerData).text(data.owner.fullname).attr('href', `/account/${data.owner.id}`);
        $(ownerContainer).append(ownerTitle).append(ownerData);
        $(container).append(ownerContainer);

        let groupContainer = document.createElement('p');
        let groupTitle = document.createElement('span');
        let groupData = document.createElement('a');
        $(groupTitle).text('Домашняя группа: ');
        $(groupData).text(data.home_group.title).attr('href', `/home_groups/${data.home_group.id}`);
        $(groupContainer).append(groupTitle).append(groupData);
        $(container).append(groupContainer);

        let dateContainer = document.createElement('p');
        let dateTitle = document.createElement('label');
        let dateData = document.createElement('input');
        $(dateTitle).text('Дата отчёта: ');
        let dateReportsFormatted = new Date(data.date.split('.').reverse().join(','));
        let thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(1).format();
        let nextSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
        $(dateData).val(data.date).attr({
            'size': data.date.length,
            'data-name': 'date',
        }).datepicker({
            autoClose: true,
            minDate: new Date(thisMonday),
            maxDate: new Date(nextSunday),
        });
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
        return container;
    }
    function sendForms(btn, data) {
        if (btn.attr('data-update') == 'true') {
            updateReports(JSON.stringify(data)).then((res) => {
                btn.attr({
                    'data-click': false,
                    'data-update': false,
                });
                btn.text('Редактировать');
                $homeReports.find('input').each(function () {
                    $(this).attr('disabled', true);
                });
            });
        } else {
            submitReports(JSON.stringify(data)).then((data) => {
                btn.text('Редактировать').attr({
                    'data-click': false,
                    'data-update': false,
                });
                $homeReports.find('input').each(function () {
                    $(this).attr('disabled', true);
                });
            }).catch( (err) => {
                showPopup(err);
            });
        }
    }
})(jQuery);