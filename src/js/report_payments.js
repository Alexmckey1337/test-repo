(function ($) {
    createChurchPaymentsTable({});

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createChurchPaymentsTable({});
    }, 500));

    //Filter
    $('#filter_button').on('click', ()=> {
        $('#filterPopup').show();
    });

    $('.date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchPaymentsTable);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createChurchPaymentsTable);
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.selectdb').select2();

})(jQuery);
