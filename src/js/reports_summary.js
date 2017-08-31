(function () {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#tree_filter'),
        $churchFilter = $('#church_filter'),
        $responsibleFilter = $('#responsible_filter'),
        initResponsible = false;
    const USER_ID = $('body').data('user');
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
                init = true;
            }
        }
    })();
    function ChurchPastorReportsTable(config={}) {
        Object.assign(config, getTabsFilterParam());
        getChurchPastorReports(config).then(data => {
            makeChurchPastorReportsTable(data);
            if (!initResponsible) {
                let responsibles = data.results.map(res => res.master),
                    uniqResponsibles = _.uniqWith(responsibles, _.isEqual);
                const options = uniqResponsibles.map(option => `<option value="${option.id}">${option.fullname}</option>`);
                $responsibleFilter.append(options);
                initResponsible = true;
            }
        });
    }
    ChurchPastorReportsTable();
    // Events
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });

     $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        churchPastorReportsTable();
    }, 500));

    $('.selectdb').select2();

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(ChurchPastorReportsTable);
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
    });

})();
