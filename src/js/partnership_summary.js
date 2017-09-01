(function () {
    const USER_ID = $('body').data('user');
    let dateReports = new Date(),
        thisPeriod = moment(dateReports).format('MM/YYYY'),
        lastPeriod = moment(dateReports).subtract(1, 'month').format('MM/YYYY');
    PartnershipSummaryTable();

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(PartnershipSummaryTable);
    });
    function PartnershipSummaryTable(config) {
        getPartnershipSummary(config).then(data => {
            let columns = _.last(data),
                results = _.dropRight(data),
                config = {};
            config.results = results;
            Object.assign(columns,config);
            makePartnershipSummaryTable(columns);
        });
    }

    $('#date_field_stats').datepicker({
            maxDate: new Date(),
            startDate: new Date(),
            autoClose: true,
            onSelect: () => {
                partnershipSummaryTable();
            }
        });

    $('.prefilter-group').find('.month').on('click', function () {
        $(this).closest('.prefilter-group').find('.month').removeClass('active');
        $(this).addClass('active');
        if (!$(this).hasClass('month_prev')) {
            $('#date_field_stats').val(`${thisPeriod}`);
        } else {
            $('#date_field_stats').val(`${lastPeriod}`);
        }
        partnershipSummaryTable();
    });



    // $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
    //     $('.preloader').css('display', 'block');
    //     homeReportsTable();
    // }, 500));

})();
