(function ($) {
    createHomeGroupsTable();
    let $churchFilter = $('#church_filter');
    let $treeFilter = $('#tree_filter');
    $('#department_select').select2();
    $('#pastor_select').select2();
    $('.selectdb').select2();
    $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
//    Events
    $('#add').on('click', function () {
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
        $('#addChurch').css('display', 'block');
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupsTable);
    });
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $('input[name="fullsearch"]').on('keyup', function () {
        createHomeGroupsTable();
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
    $churchFilter.on('change', function () {
        let churchesID = $(this).val();
        let config = {};
        if (churchesID) {
            config = {
                church_id: churchesID
            }
        }
        getLeadersByChurch(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ').attr('selected', true);
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#tree_filter').html(options);
            // $('#leader_filter').html(options);
        })
    });
    $treeFilter.on('change', function () {
        let masterTreeID = $(this).val();
        let config = {};
        if (masterTreeID) {
            config = {
                master_tree: masterTreeID
            }
        }
        getLeadersByChurch(config).then(function (data) {
            let options = [];
            let option = document.createElement('option');
            $(option).text('ВСЕ').attr('selected', true);
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#leader_filter').html(options);
        });
    })
})(jQuery);