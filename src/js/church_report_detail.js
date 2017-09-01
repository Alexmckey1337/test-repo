(function ($) {
    let $additionalInformation = $('#additionalInformation');
    let $reportBlock = $('#report_block');
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    function getChurchReportDetailData(config = {}) {
        return new Promise(function (resolve, reject) {
            let data = {
                url: URLS.event.church_report.detail(REPORTS_ID),
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

    function makeCaption(data) {
        let container = document.createElement('div');

        let pastorContainer = document.createElement('p');
        let pastorTitle = document.createElement('span');
        let pastorData = document.createElement('a');
        $(pastorTitle).text('Пастор: ');
        $(pastorData).text(data.pastor.fullname).attr('href', `/account/${data.pastor.id}`);
        $(pastorContainer).append(pastorTitle).append(pastorData);
        $(container).append(pastorContainer);

        let churchContainer = document.createElement('p');
        let churchTitle = document.createElement('span');
        let churchData = document.createElement('a');
        $(churchTitle).text('Церковь: ');
        $(churchData).text(data.church.title).attr('href', `/churches/${data.church.id}`);
        $(churchContainer).append(churchTitle).append(churchData);
        $(container).append(churchContainer);

        let dateContainer = document.createElement('p');
        let dateTitle = document.createElement('label');
        let dateData = document.createElement('input');
        $(dateTitle).text('Дата отчёта: ');
        let dateReportsFormatted = new Date(data.date.split('.').reverse().join(','));
        let thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(1).format();
        let nextSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
        $(dateData).val(data.date).attr({
            'size': data.date.length,
            'name': 'date',
            'data-validation': 'required'
        }).datepicker({
            autoClose: true,
            minDate: new Date(thisMonday),
            maxDate: new Date(nextSunday),
        });
        $(dateContainer).append(dateTitle).append(dateData);
        $(container).append(dateContainer);

        return container;
    }

    function makeReportData(data) {
        let container = document.createElement('div');
        $(container).attr({
            'class': 'report-block'
        });
        console.log(data.comment);
        let txt = `
             <div class="column col-6">
                    <h3>Отчет по людям</h3>
                    <ul class="info">
                        <li>
                            <div class="label-wrapp">
                                <label for="total_peoples">Количество людей на собрании</label>
                            </div>
                            <div class="input">
                                <input id="total_peoples" type="text" name="total_peoples" 
                                data-validation="number required"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_peoples}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_new_peoples">Количество новых людей</label>
                            </div>
                            <div class="input">
                                <input id="total_new_peoples" type="text" name="total_new_peoples"
                                data-validation="number required"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_new_peoples}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_repentance">Количество покаяний</label>
                            </div>
                            <div class="input">
                                <input id="total_repentance" type="text" name="total_repentance"
                                data-validation="number required"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_repentance}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="comment">Комментарий</label>
                            </div>
                            <div class="input">
                                <textarea name="comment" id="comment">${data.comment}</textarea>
                            </div>
                        </li>
                    </ul>
                </div>
                <div class="column col-6">
                    <h3>Отчет по финансам</h3>
                    <ul class="info">
                        <li>
                            <div class="label-wrapp">
                                <label for="total_tithe">Десятины</label>
                            </div>
                            <div class="input">
                                <input id="total_tithe" type="text" name="total_tithe"
                                 data-validation="number required" data-validation-allowing="float"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_tithe}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_donations">Пожертвования</label>
                            </div>
                            <div class="input">
                                <input id="total_donations" type="text" name="total_donations"
                                data-validation="number required" data-validation-allowing="float"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_donations}">
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="currency_donations">Пожертвования в другой валюте</label>
                            </div>
                            <div class="input">
                                <textarea name="currency_donations" id="currency_donations">${data.currency_donations}</textarea>
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="transfer_payments">15% к перечислению</label>
                            </div>
                            <div class="input">
                                <input name="transfer_payments" id="transfer_payments"
                                 value="${(data.status == 1 || data.status == 3) ? '' : data.transfer_payments}" readonly>
                            </div>
                        </li>
                        <li>
                            <div class="label-wrapp">
                                <label for="total_pastor_tithe">Десятина пастора</label>
                            </div>
                            <div class="input">
                                <input name="total_pastor_tithe" id="total_pastor_tithe"
                                data-validation="number required" data-validation-allowing="float"
                                value="${(data.status == 1 || data.status == 3) ? '' : data.total_pastor_tithe}">
                            </div>
                        </li>
                    </ul>
                </div>`;
        $(container).append(txt);
        return container;
    }

    function submitReports(config) {
        return new Promise((resolve, reject) => {
            let data = {
                method: 'POST',
                url: URLS.event.church_report.submit(REPORTS_ID),
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

    getChurchReportDetailData().then(data => {
        $additionalInformation.append(makeCaption(data));
        $reportBlock.append(makeReportData(data));
        return data;
    }).then(data => {
        if (data.status === 2) {
            $('#save').text('Редактировать').attr('data-click', false);
            $('#databaseChurchReportsForm').find('input:not(:hidden), textarea').each(function () {
                $(this).attr('disabled', true);
            })
        }
        $('#total_tithe, #total_donations').on('input', function () {
            let tithe = $('#total_tithe').val(),
                donat = $('#total_donations').val(),
                calc = (+tithe + +donat)*0.15;
            $('#transfer_payments').val(calc.toFixed(1));
        });
        if(!data.can_submit) {
            showPopup(data.cant_submit_cause);
            $('#save').attr({
                disabled: true
            });
            $('#databaseChurchReportsForm').on('click', 'input', function () {
                showPopup(data.cant_submit_cause);
            });
        }
        $.validate({
            lang: 'ru',
            form: '#databaseChurchReportsForm'
        });
    });

    $('#save').on('click', function () {
        let btn = $(this),
            data = {},
            $input = $('#databaseChurchReportsForm').find('input:not(:hidden), textarea');
        if (btn.attr('data-click') == "false") {
            btn.attr({
                'data-click': true,
                'data-update': true,
            });
            $input.each(function () {
                $(this).attr('disabled', false);
            });

            btn.text('Сохранить');
            return false;
        }
        $input.each(function () {
            let field = $(this).attr('name');
            if (field) {
                if (field == 'date') {
                    data[field] = $(this).val().split('.').reverse().join('-');
                } else {
                    data[field] = $(this).val();
                }
            }
        });
        sendForms(btn, data);
    });

    $('.submitBtn').on('click', function (e) {
        e.preventDefault();
    });

    function sendForms(btn, data) {
        let $input = $('#databaseChurchReportsForm').find('input:not(:hidden), textarea');
        if (btn.attr('data-update') == 'true') {
            updateReports(JSON.stringify(data)).then((res) => {
                btn.attr({
                    'data-click': false,
                    'data-update': false,
                });
                btn.text('Редактировать');
                $input.each(function () {
                    $(this).attr('disabled', true);
                });
                showPopup('Изменения в отчете поданы');
            }).catch( (res) => {
                let error = JSON.parse(res.responseText);
                let errKey = Object.keys(error);
                let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
                showPopup(html);
            });
        } else {
            submitReports(JSON.stringify(data)).then((data) => {
                btn.text('Редактировать').attr({
                    'data-click': false,
                    'data-update': false,
                });
                $input.each(function () {
                    $(this).attr('disabled', true);
                });
                showPopup('Отчет успешно подан');
            }).catch( (res) => {
                let error = JSON.parse(res.responseText);
                let errKey = Object.keys(error);
                let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
                showPopup(html);
            });
        }
    }

    function updateReports(config) {
        return new Promise((resolve, reject) => {
            let data = {
                method: 'PUT',
                url: URLS.event.church_report.detail(REPORTS_ID),
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

})(jQuery);