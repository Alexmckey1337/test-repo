(function ($) {
    createChurchesTable();

    $('#department_select').select2();
    $('#pastor_select').select2();
    $('#departments_filter').select2();
    $('#hierarchies_filter').select2();
    $('#pastor_filter').select2();
    $('#added_churches_date').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
     $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
//    Events
    $('#add').on('click', function () {
        var department_id = parseInt($('#department_select').val());
        clearAddChurchData();
        makePastorList(department_id, '#pastor_select');
        setTimeout(function () {
            $('#addChurch').css('display', 'block');
        }, 100);
    });
    $('#department_select').on('change', function () {
         $('#pastor_select').prop('disabled', true);
        var department_id = parseInt($('#department_select').val());
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
        showPopup('Запрос на создание файла отправлен, через несколько секунд файл появится в списке загрузок');
        exportTableData(this);
    });
})(jQuery);