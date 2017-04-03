(function ($) {
    makePayments().then((data) => {

    });
    $('input[name="fullsearch"]').keyup(function () {
        let search = $(this).val();
        $('.preloader').css('display', 'block');
        delay(function () {
            makePayments({
                search_purpose_fio: search
            }).then(() => {

            })
        }, 1000);
    });
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
})(jQuery);
