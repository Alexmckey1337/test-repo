(function ($) {
    createPaymentsTable({});

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createPaymentsTable({});
    }, 500));
    // $('input[name="fullsearch"]').keyup(function () {
    //     $('.preloader').css('display', 'block');
    //     delay(function () {
    //         createPaymentsTable({});
    //     }, 1000);
    // });
    $('#filter_button').on('click', ()=> {
        $('#filterPopup').show();
    });
    $('#date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#sent_date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#sent_date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#purpose_date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        view: 'months',
        minView: 'months'
    });
    $('#purpose_date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        view: 'months',
        minView: 'months'
    });
    $('.custom_select').select2();

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createPaymentsTable);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createPaymentsTable);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.selectdb').select2();

})(jQuery);
