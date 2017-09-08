(function () {
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
    },
        init = false,
        path = window.location.href.split('?')[1];

    function filterInit(liderID=null) {
        if (!init) {
            getPastorsByDepartment({
                master_tree: USER_ID
            }).then(res => {
                let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(leaders);
            });
            getChurches().then(res => {
                let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
            getHomeGroups().then(res => {
                let groups = res.results.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
            });
            getHGLeaders().then(res => {
                let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                $liderFilter.html('<option>ВСЕ</option>').append(liders);
                if (liderID != null) {
                    $liderFilter.find(`option[value='${liderID}']`).prop('selected', true).trigger('change');
                    $('.apply-filter').trigger('click');
                }
            });
            init = true;
        }
    }
    // let filterInit = (function () {
    //     let init = false;
    //     return function () {
    //         if (!init) {
    //             getPastorsByDepartment({
    //                 master_tree: USER_ID
    //             }).then(res => {
    //                 let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
    //                 $treeFilter.html('<option>ВСЕ</option>').append(leaders);
    //             });
    //             getChurches().then(res => {
    //                 let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
    //                 $churchFilter.html('<option>ВСЕ</option>').append(churches);
    //             });
    //             getHomeGroups().then(res => {
    //                let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
    //                 $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
    //             });
    //             getHGLeaders().then(res => {
    //                let liders = res.map(lider=> `<option value="${lider.id}">${lider.fullname}</option>`);
    //                 $liderFilter.html('<option>ВСЕ</option>').append(liders);
    //             });
    //             init = true;
    //         }
    //     }
    // })();
    (path == undefined) && HomeReportsTable(configData);
    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').show();
        let status = $(this).data('status');
        let config = {
            status: status
        };
        Object.assign(config, getFilterParam());
        Object.assign(config, getTabsFilterParam());
        HomeReportsTable(config);
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
    });
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });
    $('#date_range').datepicker({
        dateFormat: 'dd.mm.yyyy',
        range: true,
        autoClose: true,
        multipleDatesSeparator: '-',
        onSelect: function (date) {
            if (date.length > 10) {
                homeReportsTable();
                $('.tab-home-stats').find('.week').removeClass('active');
            }
        }
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

    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        homeReportsTable();
    }, 500));

    $('.tab-home-stats').find('.type').on('click', function () {
        $(this).closest('#tabs').find('li').removeClass('active');
        $(this).parent().addClass('active');
        homeReportsTable();
    });

     $('.tab-home-stats').find('.week').on('click', function () {
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('week_now')) {
            $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
        } else if ($(this).hasClass('week_prev')) {
            $('.set-date').find('input').val(`${lastMonday}-${lastSunday}`);
        } else {
            $('.set-date').find('input').val('');
        }
        homeReportsTable();
    });

    //Filter
    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {},
            config2 = {};
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
            config2.department_id = departamentID;
        }
        getPastorsByDepartment(config2).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(pastors);
            });
        getChurches(config).then(res => {
                    let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
        getHomeGroups(config).then(res => {
            console.log('sadasdas');
                   let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                });
        getHGLeaders(config).then(res => {
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
        getHGLeaders(config).then(res => {
                   let liders = res.map(lider=> `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                });
    });

    $churchFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config.church = $(this).val();
        }
        getHomeGroups(config).then(res => {
            let groups = res.results.map(group=> `<option value="${group.id}">${group.get_title}</option>`);
            $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
        });
        getHGLeaders(config).then(res => {
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

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        $('.week').removeClass('active');
        $('.week_all').addClass('active');
        $('#date_range').val('');
        $('#statusTabs').find('li').removeClass('current');
        $('#statusTabs').find(`button[data-status='${filterParam.type}']`).parent().addClass('current');
        filterInit(filterParam.owner);
    }
})();
