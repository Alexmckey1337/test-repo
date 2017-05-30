(function ($) {
    let $departmentsFilter = $('#departments_filter');
    let $treeFilter = $('#tree_filter');

    createChurchesTable();

    $('#department_select').select2();
    $('#pastor_select').select2();
    $('#tree_filter').select2();
    $departmentsFilter.select2();
    $('#hierarchies_filter').select2();
    $('#pastor_filter').select2();
    $('#search_is_open').select2();
    $('#added_churches_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
//    Events
    $('#add').on('click', function () {
        let department_id = parseInt($('#department_select').val());
        clearAddChurchData();
        makePastorList(department_id, '#pastor_select');
        setTimeout(function () {
            $('#addChurch').css('display', 'block');
        }, 100);
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id, '#pastor_select');
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesTable);
    });
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $('input[name="fullsearch"]').on('keyup', function () {
        createChurchesTable();
    });
    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        exportTableData(this)
            .then(function () {
                $('.preloader').css('display', 'none');
            })
            .catch(function () {
                showPopup('Ошибка при загрузке файла');
                $('.preloader').css('display', 'none');
            });
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
        getPastorsByDepartment({department_id: departamentID}).then(function (data) {
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
        });
        getPastorsByDepartment({department_id: departamentID}).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ');
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#pastor_filter').html(options);
        });
    });
    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config = {
                master_tree: $(this).val()
            };
        }
        getPastorsByDepartment(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ');
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#pastor_filter').html(options);
        });
    });
})(jQuery);