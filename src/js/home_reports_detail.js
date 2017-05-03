(function ($) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];
     $('.preloader').hide();
    function makeHomeReportDetailTable(data) {
        let tmpl = $('#databaseHomeReports').html();
        let rendered = _.template(tmpl)(data);
        $('#homeReports').html(rendered);
        makeSortForm(data.table_columns);
    }

    function getHomeReportDetail(config = {}) {
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

    getHomeReportDetail().then(data => {
        makeHomeReportDetailTable(data);
    });

})(jQuery);