(function ($) {
    createHomeGroupsTable();

    $('#department_select').select2();
    $('#pastor_select').select2();
    $('.selectdb').select2();
    $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
//    Events
    $('#add').on('click', function () {
        var department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
        $('#addChurch').css('display', 'block');
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        var department_id = parseInt($('#department_select').val());
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
        showPopup('Запрос на создание файла отправлен, через несколько секунд файл появится в списке загрузок');
        exportTableData(this);
    });
})(jQuery);