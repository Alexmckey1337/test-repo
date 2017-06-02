(function () {
    HomeReportsTable();
    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').show();
        let status = $(this).data('status');
        let config = {
            status: status
        };
        Object.assign(config, getFilterParam());
        HomeReportsTable(config);
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

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(HomeReportsTable);
    });
    function HomeReportsTable(config) {
        getHomeReports(config).then(data => {
            makeHomeReportsTable(data);
        });
    }

    $('input[name=fullsearch]').on('keyup', function () {
        $('.preloader').show();
        homeReportsTable();
    });

    $('.tab-home-stats').find('.type').on('click', function () {
        $(this).closest('#tabs').find('li').removeClass('active');
        $(this).parent().addClass('active');
        homeReportsTable();
    })

})();