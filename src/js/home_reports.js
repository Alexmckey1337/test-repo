(function () {
    getHomeReports().then(data => {
        makeHomeReportsTable(data);
    });
    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').show();
        let status = $(this).data('status');
        let config = {
             status: status
        };
        Object.assign(config, getFilterParam());
        getHomeReports(config).then(data => {
            makeHomeReportsTable(data);
        });
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
    });
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('.selectdb').select2();
})();
