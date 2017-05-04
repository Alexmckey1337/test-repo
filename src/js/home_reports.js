(function () {
    function makeHomeReportsTable(data) {
        let tmpl = $('#databaseHomeReports').html();
        let rendered = _.template(tmpl)(data);
        $('#homeReports').html(rendered);
        makeSortForm(data.table_columns);
        $('.preloader').hide();
    }

    function getHomeReports(config = {}) {
        return new Promise(function (resolve, reject) {
            let data = {
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/`,
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                    status: config.status || 2
                }
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

    getHomeReports().then(data => {
        makeHomeReportsTable(data);
    });
    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').show();
        let status = $(this).data('status');
        getHomeReports({
            status: status
        }).then(data => {
            makeHomeReportsTable(data);
        });
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
    })
})();
