(function ($) {
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    homeStatistics();
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('.selectdb').select2();
})(jQuery);
