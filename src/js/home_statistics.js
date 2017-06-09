(function ($) {
    let dateReports = new Date(),
        thisMonday = (moment(dateReports).day() === 1) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(1).format('DD.MM.YYYY'),
        thisSunday = (moment(dateReports).day() === 0) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(7).format('DD.MM.YYYY'),
        lastMonday = (moment(dateReports).day() === 1) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).subtract(7, 'days').format('DD.MM.YYYY'),
        lastSunday = (moment(dateReports).day() === 0) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(7).subtract(7, 'days').format('DD.MM.YYYY'),
        $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#master_tree_filter'),
        $churchFilter = $('#church_filter'),
        $homeGroupFilter = $('#home_group_filter'),
        $liderFilter = $('#masters_filter');
    const USER_ID = $('body').data('user');
    $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
    let configData = {
        from_date: thisMonday.split('.').reverse().join('-'),
        to_date: thisSunday.split('.').reverse().join('-')
    };
    let filterInit = (function () {
        let init = false;
        return function () {
            if (!init) {
                getPastorsByDepartment({
                    master_tree: USER_ID
                }).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                getChurches().then(res => {
                    let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
                getHomeGroups().then(res => {
                   let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                });
                getLeadersByChurch().then(res => {
                   let liders = res.map(lider=> `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                });
                init = true;
            }
        }
    })();

    homeStatistics(configData);

    $('#date_range').datepicker({
        dateFormat: 'dd.mm.yyyy',
        range: true,
        autoClose: true,
        multipleDatesSeparator: '-',
        onSelect: function (date) {
            if (date.length > 10) {
                homeStatistics();
                $('.tab-home-stats').find('.week').removeClass('active');
            }
        }
    });
    $('.selectdb').select2();
    $('.tab-home-stats').find('.type').on('click', function () {
        $(this).closest('#tabs').find('li').removeClass('active');
        $(this).parent().addClass('active');
        homeStatistics();
    });
    $('.tab-home-stats').find('.week').on('click', function () {
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if (!$(this).hasClass('week_prev')) {
            $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
        } else {
            $('.set-date').find('input').val(`${lastMonday}-${lastSunday}`);
        }
        homeStatistics();
    });

    //Filter
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {};
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
        }
        getPastorsByDepartment({
            department_id: departamentID
        }).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(pastors);
            });
        getChurches(config).then(res => {
                    let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
        getHomeGroups(config).then(res => {
                   let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                });
        getLeadersByChurch(config).then(res => {
                   let liders = res.map(lider=> `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                });
    });

    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config.master_tree = $(this).val();
        }
        getChurches(config).then(res => {
                    let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
        getHomeGroups(config).then(res => {
                   let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                });
        getLeadersByChurch(config).then(res => {
                   let liders = res.map(lider=> `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                });
    });

    $churchFilter.on('change', function () {
        let config = {},
            config2 = {};
        if ($(this).val() != "ВСЕ") {
            config.church = $(this).val();
            config2.church_id = $(this).val();
        }
        getHomeGroups(config).then(res => {
            let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
            $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
        });
        getLeadersByChurch(config2).then(res => {
            let liders = res.map(lider=> `<option value="${lider.id}">${lider.fullname}</option>`);
            $liderFilter.html('<option>ВСЕ</option>').append(liders);
        });
    });

    $liderFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config.leader = $(this).val();
        }
        getHomeGroups(config).then(res => {
            let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
            $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
        });
    });

})(jQuery);
