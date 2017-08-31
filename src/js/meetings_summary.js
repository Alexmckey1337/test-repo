(function () {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#master_tree_filter'),
        $churchFilter = $('#church_filter');
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
    HomeLiderReportsTable();

    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });

    $('.selectdb').select2();

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(HomeLiderReportsTable);
    });
    function HomeLiderReportsTable() {
        getHomeLiderReports().then(data => {
            makeHomeLiderReportsTable(data);
        });
    }

    $('input[name="fullsearch"]').on('keyup', _.debounce(function () {
        $('.preloader').css('display', 'block');
        homeLiderReportsTable();
    }, 500));

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

    $churchFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config.church = $(this).val();
        }
    });

})();
