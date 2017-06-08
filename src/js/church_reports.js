(function () {
    let dateReports = new Date();
    let thisMonday = (moment(dateReports).day() === 1) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(1).format('DD.MM.YYYY');
    let thisSunday = (moment(dateReports).day() === 0) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(7).format('DD.MM.YYYY');
    let lastMonday = (moment(dateReports).day() === 1) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).subtract(7, 'days').format('DD.MM.YYYY');
    let lastSunday = (moment(dateReports).day() === 0) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(7).subtract(7, 'days').format('DD.MM.YYYY');
    $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
    let configData = {
        from_date: thisMonday.split('.').reverse().join('-'),
        to_date: thisSunday.split('.').reverse().join('-')
    };
    function ChurchReportsTable(config) {
        getChurchReports(config).then(data => {
            makeChurchReportsTable(data);
        });
    }
    ChurchReportsTable(configData);
    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').show();
        let status = $(this).data('status');
        let config = {
            status: status
        };
        Object.assign(config, getFilterParam());
        ChurchReportsTable(config);
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
    });
    $('#date_range').datepicker({
        dateFormat: 'dd.mm.yyyy',
        range: true,
        autoClose: true,
        multipleDatesSeparator: '-',
        onSelect: function (date) {
            if (date.length > 10) {
                churchReportsTable();
                $('.tab-home-stats').find('.week').removeClass('active');
            }
        }
    });

     $('.tab-home-stats').find('.week').on('click', function () {
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if (!$(this).hasClass('week_prev')) {
            $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
        } else {
            $('.set-date').find('input').val(`${lastMonday}-${lastSunday}`);
        }
        churchReportsTable();
    });

     $('input[name=fullsearch]').on('keyup', function () {
        $('.preloader').show();
        churchReportsTable();
    });

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(ChurchReportsTable);
    });

})();
