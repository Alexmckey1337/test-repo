$('document').ready(function () {
    let $createUser = $('#createUser');

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
    function createNewUser() {
        let oldForm = document.forms.createUser;
        let formData = new FormData(oldForm);
        if ($('#division_drop').val()) {
            formData.append('divisions', JSON.stringify($('#chooseDivision').val()));
        } else {
            formData.append('divisions', JSON.stringify([]));
        }
        if ($('#phoneNumber').val()) {
            let phoneNumber = $('#phoneNumberCode').val() + $('#phoneNumber').val();
            formData.append('phone_number', phoneNumber)
        }
        if ($('#extra_phone_numbers').val()) {
            formData.append('extra_phone_numbers', JSON.stringify($('#extra_phone_numbers').val().split(',').map((item) => item.trim())));
        } else {
            formData.append('extra_phone_numbers', JSON.stringify([]));
        }
        if ($('#partner').is(':checked')) {
            let partner = {};
            partner.value = parseInt($('#partnerFrom').val()) || 0;
            partner.currency = parseInt($('#payment_currency').val());
            partner.date = $('#partners_count').val() || null;
            partner.responsible = parseInt($("#chooseManager").val());
            formData.append('partner', JSON.stringify(partner));
        }
        let send_image = $('#file').prop("files").length || false;
        if (send_image) {
            try {
                let blob;
                blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                formData.append('image', blob);
                formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
                formData.append('id', id);
            } catch (err) {
                console.log(err);
            }
        }
        let url = `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/`;
        let config = {
            url: url,
            data: formData,
            method: 'POST'
        };
        $('.preloader').css('display', 'block');
        ajaxSendFormData(config).then(function (data) {
            $('.preloader').css('display', 'none');
            showPopup(`${data.fullname} добален(а) в базу данных`);
            $createUser.find('input').each(function () {
                $(this).val('').attr('disabled', false);
            });
            $createUser.find('.cleared').each(function () {
                $(this).find('option').eq(0).prop('selected', true).select2()
            });
            $('#addNewUserPopup').css('display', 'none');

        }).catch(function (data) {
            $('.preloader').css('display', 'none');
            showPopup(data);
        });
    }

    $('#add').on('click', function () {
        $('#addNewUserPopup').css('display', 'block');
        initAddNewUser();
    });

    $.validate({
        lang: 'ru',
        form: '#createUser',
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                createNewUser();
            }
            return false; // Will stop the submission of the form
        },
    });
});