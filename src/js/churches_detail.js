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

    function addUserToChurch(data) {
        let id = data.id;
        let config = {};
        config.user_id = id;
        return new Promise(function (resolve, reject) {
            let data = {
                method: 'POST',
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/${ID}/add_user/`,
                data: config
            };
            let status = {
                201: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }
            };
            newAjaxRequest(data, status, reject);
        });
    }

    function makeUsersFromDatabaseList(config = {}) {
        getUsersTOChurch(config).then(function (data) {
            let users = data;
            let html = [];
            if (users.length) {
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
                        let config = {};
                        config.id = id;
                        addUserToChurch(config).then(function (data) {
                            $(_self).text('Добавлен').attr('disabled', true);
                            createChurchesUsersTable(ID);
                        });
                    });
                    $(rows_wrap).addClass('rows-wrap').append(button).append(rows);
                    html.push(rows_wrap);
                });
            } else {
                let rows_wrap = document.createElement('div');
                let rows = document.createElement('div');
                let col_1 = document.createElement('div');
                $(col_1).text('Пользователь не найден');
                $(rows).addClass('rows').append(col_1);
                $(rows_wrap).addClass('rows-wrap').append(rows);
                html.push(rows_wrap);
            }
            $('#searchedUsers').html(html);
            $('.choose-user-wrap .splash-screen').addClass('active');
        })
    }

    createChurchesDetailsTable({}, ID, link);

    $('#added_home_group_pastor').select2();
    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
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
        $('#chooseDepartment').html(option).attr('disabled', false);
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
    $('#addHomeGroup').on('submit', function (e) {
        e.preventDefault();
        addHomeGroup(this);
    });
    $.validate({
        lang: 'ru',
        form: '#createUser',
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(addUserToChurch).then(function() {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        }
    });
})(jQuery);
