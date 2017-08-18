(function ($) {
    let $createUserForm = $('#createUser'),
        $homeGroup = $('#home_group');

    const ID = $homeGroup.data('id');
    const HG_ID = $homeGroup.data('departament_id');
    const CH_ID = $homeGroup.data('church-id');
    const HG_TITLE = $homeGroup.data('departament_title');

    function reRenderTable(config) {
        addUserToHomeGroup(config).then(() => createHomeGroupUsersTable());
    }

    function addUserToHomeGroup(data) {
        let id = data.id;
        let config = {};
        config.user_id = id;
        return new Promise(function (resolve, reject) {
            let data = {
                method: 'POST',
                url: URLS.home_group.add_user(ID),
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
                        'disabled': !item.can_add
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
        // $('#addUser').css('display', 'block');
        initAddNewUser({getDepartments: false});
        $('#searchedUsers').html('');
        $('#searchUserFromDatabase').val('');
        $('.choose-user-wrap .splash-screen').removeClass('active');
        document.querySelector('#searchUserFromDatabase').focus();
        $('#chooseUserINBases').css('display', 'block');
    });

    // $('#choose').on('click', function () {
    //     $(this).closest('.popup').css('display', 'none');
    //     $('#searchedUsers').html('');
    //     $('#searchUserFromDatabase').val('');
    //     $('.choose-user-wrap .splash-screen').removeClass('active');
    //     $('#chooseUserINBases').css('display', 'block');
    // });

    $('#addNewUser').on('click', function () {
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
        onError: function (form) {
          showPopup(`Введены некорректные данные`);
          let top = $(form).find('div.has-error').first().offset().top;
          $(form).find('.body').animate({scrollTop: top}, 500);
        },
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(reRenderTable).then(function() {
                    $(form).find('#saveNew').attr('disabled', false);
                });
            }
            return false; // Will stop the submission of the form
        }
    });

    accordionInfo();

    $('#opening_date').datepicker({
        dateFormat: 'dd.mm.yyyy',
        autoClose: true
    });

    $('.accordion').find('.edit').on('click', function (e) {
        e.preventDefault();
        let $input = $(this).closest('form').find('input:not(.select2-search__field), select');

        if ($(this).hasClass('active')) {
            $input.each(function (i, el) {
                if (!$(this).attr('disabled')) {
                    $(this).attr('disabled', true);
                }
                $(this).attr('readonly', true);
                if ($(el).is('select')) {
                    if (!$(this).is('.no_select')) {
                        $(this).select2('destroy');
                    }
                }
            });
            $(this).removeClass('active');
        } else {
            let leaderId = $('#homeGroupLeader').val(),
                churchId = $('#editHomeGroupForm').attr('data-departament_id');

             getPotentialLeadersForHG({church: churchId}).then(function (res) {
                    return res.map(function (leader) {
                        return `<option value="${leader.id}" ${(leaderId == leader.id) ? 'selected' : ''}>${leader.fullname}</option>`;
                    });
                }).then(function (data) {
                    $('#homeGroupLeader').html(data).prop('disabled', false).select2();
                });
            $input.each(function (i, el) {
                if (!$(this).hasClass('no__edit')) {
                    if ($(this).attr('disabled')) {
                        $(this).attr('disabled', false);
                    }
                    if (!$(el).is('#church')) {
                        $(this).attr('readonly', false);
                    }
                }
            });
            $(this).addClass('active');
        }
    });

    $('.accordion').find('.save__info').on('click', function (e) {
        e.preventDefault();
        let idHomeGroup = $(this).closest('form').attr('data-id');
        editHomeGroups($(this), idHomeGroup);
        let liderLink = '/account/' + $('#homeGroupLeader').val();
        pasteLink($('#homeGroupLeader'), liderLink);
        let webLink = $(this).closest('form').find('#web_site').val();
        let linkIcon = $('#site-link');
        if (webLink == '' ) {
            !linkIcon.hasClass('link-hide') && linkIcon.addClass('link-hide');
        } else {
            pasteLink($('#web_site'), webLink);
            linkIcon.hasClass('link-hide') && linkIcon.removeClass('link-hide');
        }
    });

})(jQuery);
