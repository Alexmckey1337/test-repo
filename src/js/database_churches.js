(function ($) {
    function makePastorList(id, selector) {
        getResponsible(id, 2).then(function (data) {
            let options = [];
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $(selector).html(options).prop('disabled', false);
        });
    }

    createChurchesTable();

    $('#department_select').select2();
    $('#pastor_select').select2();
    $('#added_churches_date').datepicker({
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
        makePastorList(department_id);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesTable);
    });
    $('input[name="fullsearch"]').on('keyup', function () {
        createChurchesTable();
    })
})(jQuery);