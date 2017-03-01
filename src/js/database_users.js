$('document').ready(function () {
    createUsersTable({});

    $('.selectdb').select2();
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        selectOtherYears: false,
        showOtherYears: false,
        moveToOtherYearsOnSelect: false,
        minDate: new Date((new Date().getFullYear()), 0, 1),
        maxDate: new Date((new Date().getFullYear()), 11, 31),
        autoClose: true
    });
    //Events
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });
    $('.editprofile').on('click', function (e) {
        e.stopPropagation();
    });
    $('.popap').on('click', function () {
        $(this).css('display', 'none');
    });
    $('input[name="fullsearch"]').keyup(function () {
        let search = $(this).val();
        $('.preloader').css('display', 'block');
        delay(function () {
            createUsersTable({})
        }, 1000);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createUsersTable);
    });
    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        exportTableData(this).then(function () {
            $('.preloader').css('display', 'none');
        });
    });

    $('#quickEditCartPopup').find('.close').on('click', function () {
        let $input = $(this).closest('.pop_cont').find('input');
        let $select = $(this).closest('.pop_cont').find('select');
        let $button = $(this).closest('.pop_cont').find('.save-user');
        let $info = $(this).closest('.pop_cont').find('.info');
        $button.css('display', 'inline-block');
        $button.removeAttr('disabled');
        $button.text('Сохранить');
        $info.each(function () {
            $(this).css('display', 'none');
        });
        $input.each(function () {
            $(this).removeAttr('readonly');
        });
        $select.each(function () {
            $(this).removeAttr('disabled');
        });
    });

    $('#add').on('click', function () {
        $('body').addClass('no_scroll');
        $('#addNewUserPopup').css('display', 'block');
        initAddNewUser();
    });

    $.validate({
        lang: 'ru',
        form: '#createUser',
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(null).then(function() {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        },
    });
});