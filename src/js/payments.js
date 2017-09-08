(function ($) {
    createPaymentsTable({});

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createPaymentsTable({});
    }, 500));

    $('#filter_button').on('click', ()=> {
        $('#filterPopup').show();
    });
    $('#date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#sent_date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#sent_date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });
    $('#purpose_date_from').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        view: 'months',
        minView: 'months',
        position: "left top",
    });
    $('#purpose_date_to').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        view: 'months',
        minView: 'months',
        position: "left top",
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
