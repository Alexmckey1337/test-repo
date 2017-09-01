(function () {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#master_tree_filter'),
        $churchFilter = $('#church_filter'),
        $responsibleFilter = $('#responsible_filter'),
        initResponsible = false,
        init = false;
    const USER_ID = $('body').data('user'),
        PATH = window.location.href.split('?')[1];

    function filterInit(set = null) {
        if (!init) {
            console.log(set);
            if (set != null) {
                $('#departments_filter').find(`option[value='${set.department_id}']`).prop('selected', true).trigger('change');
                let departamentID = $('#departments_filter').val(),
                    config = {},
                    config2 = {};
                if (departamentID) {
                    config.department = departamentID;
                    config2.department_id = departamentID;
                }
                getPastorsByDepartment(config2).then(data => {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(pastors);
                }).then(() => {
                    getChurches(config).then(res => {
                        let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                        $churchFilter.html('<option>ВСЕ</option>').append(churches);
                    });
                }).then(() => {
                    if (set.master_id) {
                        getChurches({master_tree: set.master_id}).then(res => {
                            let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                            $churchFilter.html('<option>ВСЕ</option>').append(churches);
                        });
                    }
                }).then(() => {
                    getHomeLiderReports().then(data => {
                        let responsibles = data.results.map(res => res.master),
                            uniqResponsibles = _.uniqWith(responsibles, _.isEqual);
                        const options = uniqResponsibles.map(option =>
                            `<option value="${option.id}" ${(set.responsible_id == option.id) ? 'selected' : ''}>${option.fullname}</option>`);
                        $responsibleFilter.append(options);
                        $('.apply-filter').trigger('click');
                    });
                });
            } else {
                getPastorsByDepartment({master_tree: USER_ID}).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                getChurches().then(res => {
                    let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
            }
            // getPastorsByDepartment({
            //     master_tree: USER_ID
            // }).then(res => {
            //     let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
            //     $treeFilter.html('<option>ВСЕ</option>').append(leaders);
            // }).then(() => {
            //     getChurches().then(res => {
            //         let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
            //         $churchFilter.html('<option>ВСЕ</option>').append(churches);
            //     });
            // }).then(() => {
            //     console.log(config);
            //     if (config != null) {
            //         let filterKeys = Object.keys(config);
            //         if (filterKeys && filterKeys.length) {
            //             filterKeys.forEach(function (key) {
            //                 $('#filterPopup').find(`select[data-filter='${key}']`)
            //                                  .find(`option[value='${config[key]}']`)
            //                                  .prop('selected', true)
            //                                  .trigger('change');
            //             });
            //         }
            //         $('.apply-filter').trigger('click');
            //     }
            // });
            init = true;
        }
    }

    (PATH == undefined) && HomeLiderReportsTable();

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
            if (!initResponsible) {
                let responsibles = data.results.map(res => res.master),
                    uniqResponsibles = _.uniqWith(responsibles, _.isEqual);
                const options = uniqResponsibles.map(option => `<option value="${option.id}">${option.fullname}</option>`);
                $responsibleFilter.append(options);
                initResponsible = true;
            }
        });
    }

    $('input[name="fullsearch"]').on('keyup', _.debounce(function () {
        $('.preloader').css('display', 'block');
        homeLiderReportsTable();
    }, 500));

    //Filter
    if (init) {
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
                let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
        });

        $treeFilter.on('change', function () {
            let config = {};
            if ($(this).val() != "ВСЕ") {
                config.master_tree = $(this).val();
            }
            getChurches(config).then(res => {
                let churches = res.results.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
        });

        // $churchFilter.on('change', function () {
        //     let config = {};
        //     if ($(this).val() != "ВСЕ") {
        //         config.church = $(this).val();
        //     }
        // });
    }

    //Parsing URL
    if (PATH != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

})();
