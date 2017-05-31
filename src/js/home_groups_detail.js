(function ($) {
    let $createUserForm = $('#createUser');
    const ID = $('#home_group').data('id');
    const HG_ID = $('#home_group').data('departament_id');
    const HG_TITLE = $('#home_group').data('departament_title');
    const CH_ID = $('#home_group').data('church-id');

    function addUserToHomeGroup(data) {
        let id = data.id;
        let config = {};
        config.user_id = id;
        return new Promise(function (resolve, reject) {
            let data = {
                method: 'POST',
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${ID}/add_user/`,
                data: config
            };
            let status = {
                200: function (req) {
                    resolve(req)
                },
                403: function () {
                    reject('Вы должны авторизоватся')
                }
            };
            newAjaxRequest(data, status, reject);
        });
    }

    function makeUsersFromDatabaseList(config = {}, id) {
        getUsersTOHomeGroup(config, CH_ID).then(function (data) {
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
                    $(button).attr({
                        'data-id': item.id,
                        'disabled': item.can_add
                    }).text('Выбрать').on('click', function () {
                        let id = $(this).data('id');
                        let config = {};
                        config.id = id;
                        let _self = this;
                        addUserToHomeGroup(config).then(function (data) {
                            $(_self).text('Добавлен').attr('disabled', true);
                            getHomeGroupStats(ID).then(function (data) {
                                let keys = Object.keys(data);
                                keys.forEach(function (item) {
                                    $('#' + item).text(data[item]);
                                })
                            });
                            createHomeGroupUsersTable();
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

    createHomeGroupUsersTable({}, ID);

// Events
    $('#add_userToHomeGroup').on('click', function () {
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
        let departament_id = $('#home_group').data('departament_id');
        let departament_title = $('#home_group').data('departament_title');
        let option = document.createElement('option');
        $(option).val(departament_id).text(departament_title).attr('selected', true);
        $(this).closest('.popup').css('display', 'none');
        $('#addNewUserPopup').css('display', 'block');
        $('#chooseDepartment').html(option).attr('required', false).attr('disabled', false);
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
    });
    $('#searchUserFromDatabase').on('keyup', function () {
        let search = $(this).val();
        if (search.length < 3) return;
        let config = {};
        config.search = search;
        config.department = HG_ID;
        makeUsersFromDatabaseList(config, ID);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupUsersTable);
    });
    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'none');
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
        form: '#createUser',
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(addUserToHomeGroup).then(function() {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        }
    });

    accordionInfo();

})(jQuery);
