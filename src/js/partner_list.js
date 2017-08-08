(function () {
    "use strict";
    let $departmentsFilter = $('#departments_filter');
    let $treeFilter = $("#tree_filter");
    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        exportTableData(this).then(function () {
            $('.preloader').css('display', 'none');
        });
    });
    $('#accountable').select2();
    $('input[name=fullsearch]').on('keyup', function () {
        getPartners({
            page: 1
        });
    });

    getPartners({});

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(getPartners);
    });
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {
            level_gte: 2
        };
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
        }
        getShortUsers(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ');
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#tree_filter').html(options);
        }).then(function () {
            if ($('#tree_filter').val() == "ВСЕ") {
                getResponsible(departamentID, 2).then(function (data) {
                    let options = [];
                    let option = document.createElement('option');
                    $(option).text('ВСЕ');
                    options.push(option);
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        options.push(option);
                    });
                    $('#masters_filter').html(options);
                });
            } else {
                getPastorsByDepartment(departamentID).then(function (data) {
                    let options = [];
                    let option = document.createElement('option');
                    $(option).text('ВСЕ');
                    options.push(option);
                    data.forEach(function (item) {
                        let option = document.createElement('option');
                        $(option).val(item.id).text(item.fullname);
                        options.push(option);
                    });
                    $('#masters_filter').html(options);
                });
            }
        });
    });
    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config = {
                master_tree: $(this).val()
            };
        }
        getShortUsers(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ');
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#masters_filter').html(options);
        });
    });
    $('.selectdb').select2();
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        selectOtherYears: false,
        showOtherYears: false,
        moveToOtherYearsOnSelect: false,
        minDate: new Date((new Date().getFullYear()), 0, 1),
        maxDate: new Date((new Date().getFullYear()), 11, 31),
        autoClose: true,
        position: "left top",
    });
    $('.select_rep_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
}());
