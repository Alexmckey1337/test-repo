(function () {
    "use strict";
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
    $('.select_db').select2();
}());
