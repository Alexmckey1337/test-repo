(function ($) {
    function makePastorList(id) {
        getResponsible(id, 2).then(function (data) {
            let options = [];
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#pastor_select').html(options).prop('disabled', false);
        });
    }

    createChurchesTable();

    $('#department_select').select2();
    $('#pastor_select').select2();
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
    })
})(jQuery);