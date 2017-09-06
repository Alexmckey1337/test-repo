(function () {
    const USER_ID = $('body').data('user');
    let dateReports = new Date(),
        thisPeriod = moment(dateReports).format('MM/YYYY'),
        lastPeriod = moment(dateReports).subtract(1, 'month').format('MM/YYYY'),
        configData = {
            year: moment(dateReports).format('YYYY'),
            month: moment(dateReports).format('MM')
        };

    $('.set-date').find('input').val(thisPeriod);

    $('#date_field_stats').datepicker({
        maxDate: new Date(),
        startDate: new Date(),
        view: 'months',
        minView: 'months',
        dateFormat: 'mm/yyyy',
        autoClose: true,
        onSelect: (formattedDate) => {
            if (formattedDate != '') {
                $('.preloader').css('display', 'block');
                partnershipSummaryTable();
            }
        }
    });

    PartnershipSummaryTable(configData);

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(PartnershipSummaryTable);
    });
    function PartnershipSummaryTable(config) {
        $('.preloader').css('display', 'block');
        getPartnershipSummary(config).then(data => {
            let results = data.results.map(elem=> {
                 elem.not_active_partners = elem.total_partners - elem.active_partners;
                 let percent = (100/(elem.plan/elem.sum_pay)).toFixed(1);
                 elem.percent_of_plan = isFinite(percent) ? percent : 0;
                 return elem;
            }),
                newRow = {
                    manager: 'СУММАРНО:',
                    plan: data.results.reduce((sum,current) => sum + current.plan, 0),
                    potential_sum: data.results.reduce((sum,current) => sum + current.potential_sum, 0),
                    sum_deals: data.results.reduce((sum,current) => sum + current.sum_deals, 0),
                    sum_pay: data.results.reduce((sum,current) => sum + current.sum_pay, 0),
                    percent_of_plan: null,
                    total_partners: data.results.reduce((sum,current) => sum + current.total_partners, 0),
                    active_partners: data.results.reduce((sum,current) => sum + current.active_partners, 0),
                    not_active_partners: data.results.reduce((sum,current) => sum + current.not_active_partners, 0),
                };

            results.push(newRow);
            let newData = {
                table_columns: data.table_columns,
                results: results
            };
            makePartnershipSummaryTable(newData);
        });
    }

    $('.prefilter-group').find('.month').on('click', function () {
        $('.preloader').css('display', 'block');
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
