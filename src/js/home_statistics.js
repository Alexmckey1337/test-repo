(function ($) {
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    homeStatistics();
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
    $('.selectdb').select2();
    $('.tab-home-stats').find('.type').on('click', function () {
        $(this).closest('#tabs').find('li').removeClass('active');
        $(this).parent().addClass('active');
        homeStatistics();
    })
})(jQuery);
