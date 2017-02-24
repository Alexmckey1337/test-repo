(function ($) {
    const ID = $('#church').data('id');
    const D_ID = $('#added_home_group_church').data('department');
    let responsibleList = false;
    let link = $('.get_info .active').data('link');

    function makeResponsibleList(id, level) {
        getResponsible(id, level).then(function (data) {
            let options = [];
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#added_home_group_pastor').html(options).prop('disabled', false);
        })
    }

    function addUserToChurch(id, el) {
        let config = {};
        config.user_id = id;
        ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/churches/${ID}/add_user/`, config, function () {
            $(el).attr('disabled', true).text('Добавлен');
            createChurchesUsersTable(ID);
        }, 'POST', 'application/json');
    }

    function makeUsersFromDatabaseList(config = {}) {
        getUsersTOChurch(config).then(function (data) {
            let users = data;
            let html = [];
            users.forEach(function (item) {
                let rows_wrap = document.createElement('div');
                let rows = document.createElement('div');
                let col_1 = document.createElement('div');
                let col_2 = document.createElement('div');
                let place = document.createElement('p');
                let link = document.createElement('a');
                let button = document.createElement('button');
                $(link).attr('href', '/account/' + item.id).text(item.full_name);
                $(place).text();
                $(col_1).addClass('col').append(link);
                $(col_2).addClass('col').append(item.country + ', ' + item.city);
                $(rows).addClass('rows').append(col_1).append(col_2);
                $(button).attr('data-id', item.id).text('Выбрать').on('click', function () {
                    let id = $(this).data('id');
                    let _self = this;
                    addUserToChurch(id, _self);
                });
                $(rows_wrap).addClass('rows-wrap').append(button).append(rows);
                html.push(rows_wrap);
            });
            $('#searchedUsers').html(html);
            $('.choose-user-wrap .splash-screen').addClass('active');
        })
    }

    createChurchesDetailsTable({}, ID, link);

    $('#added_home_group_pastor').select2();
    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd'
    });
//    Events
    $('#add_homeGroupToChurch').on('click', function () {
        clearAddHomeGroupData();
        if (!responsibleList) {
            responsibleList = true;
            makeResponsibleList(D_ID, 1);
        }
        setTimeout(function () {
            $('#addHomeGroup').css('display', 'block');
        }, 100)
    });
    $('#add_userToChurch').on('click', function () {
        $('#addUser').css('display', 'block');
        initAddNewUser({
            getDepartments: false,
        });
    });
    $('#choose').on('click', function () {
        $(this).closest('.popup').css('display', 'none');
        $('#searchedUsers').html('');
        $('#searchUserFromDatabase').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        $('#chooseUserINBases').css('display', 'block');
    });
    $('#add_new').on('click', function () {
        let department_id = $('#church').data('department_id');
        let department_title = $('#church').data('department_title');
        let option = document.createElement('option');
        $(option).val(department_id).text(department_title).attr('selected', true).attr('required', false);
        $(this).closest('.popup').css('display', 'none');
        $('#addNewUserPopup').css('display', 'block');
        $('#chooseDepartment').html(option);
    });
    $('#searchUserFromDatabase').on('keyup', function () {
        let search = $(this).val();
        if (search.length < 3) return;
        let config = {};
        config.search = search;
        config.department = D_ID;
        makeUsersFromDatabaseList(config);
    });

    $('.get_info button').on('click', function () {
        let link = $(this).data('link');
        let exportUrl = $(this).data('export-url');
        let canEdit = $(this).data('editable');
        $('#church').removeClass('can_edit');
        if (canEdit) {
            $('#church').addClass('can_edit');
        }
        createChurchesDetailsTable({}, ID, link);
        $('.get_info button').removeClass('active');
        $(this).addClass('active');
        $('#export_table').attr('data-export-url', exportUrl);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesDetailsTable);
    });

    function createNewUser(id) {
        let oldForm = document.forms.createUser;
        let formData = new FormData(oldForm);
        if ($('#division_drop').val()) {
            formData.append('divisions', JSON.stringify($('#chooseDivision').val()));
        } else {
            formData.append('divisions', JSON.stringify([]));
        }
        if($('#phoneNumberCode').val() && $('#phoneNumber').val()) {
            let phoneNumber = $('#phoneNumberCode').val() + $('#phoneNumber').val();
            formData.append('phone_number', phoneNumber)
        }
        if ($('#extra_phone_numbers').val()) {
            formData.append('extra_phone_numbers', JSON.stringify($('#extra_phone_numbers').val().split(',').map((item) => item.trim())));
        } else {
            formData.append('extra_phone_numbers', JSON.stringify([]));
        }
        formData.append('department', $('#chooseDepartment').val());
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
            addUserToChurch(data.id);
            showPopup(`${data.fullname} добален(а) в базу данных`);
            $('#createUser').find('input').each(function () {
                $(this).val('')
            });
            $('#createUser').find('.cleared').each(function () {
                $(this).find('option').eq(0).prop('selected', true).select2()
            });
            $('#addNewUserPopup').css('display', 'none');
        }).catch(function (data) {
            $('.preloader').css('display', 'none');
            showPopup(data);
        });
    }

    $('#createUser').on('submit', function (e) {
        e.preventDefault();
        createNewUser();
    });
    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        exportTableData(this)
            .then(function () {
                $('.preloader').css('display', 'none');
            })
            .catch(function () {
                showPopup('Ошибка при загрузке файла');
                $('.preloader').css('display', 'none');
        });
    });
    $.validate({
        lang: 'ru',
        onSuccess: function () {
            createNewUser();
            return false; // Will stop the submission of the form
        },
    });
})(jQuery);
