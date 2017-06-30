(function () {
    $('.preloader').hide();
    function makeChurchReportsTable(data) {
        let tmpl = $('#databaseHomeReports').html();
        let rendered = _.template(tmpl)(data);
        $('#homeReports').html(rendered);
        makeSortForm(data.table_columns);
    }

    function getChurchReports(config = {}) {
        return new Promise(function (resolve, reject) {
            let data = {
                url: URLS.home_meeting.church_report(),
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                    status: config.status || 1
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

    getChurchReports().then(data => {
        makeChurchReportsTable(data);
    });
    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        let status = $(this).data('status');
        getChurchReports({
            status: status
        }).then(data => {
            makeChurchReportsTable(data);
        });
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
    })
})();
