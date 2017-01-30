$('document').ready(function () {

    createUsersTable({});

    $('.selectdb').select2();

    //Events
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });
    $('#add').on('click', function () {
        $('#addNewUserPopup').css('display', 'block');
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
    $('input[name="searchDep"]').keyup(function () {
        delay(function () {
            createUserDep();
        }, 1500);
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

});