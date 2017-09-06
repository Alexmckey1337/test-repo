(function ($) {
    const CHURCH_ID = $('#church').data('id');
    const D_ID = $('#added_home_group_church').data('department');
    let responsibleList = false;
    let link = $('.get_info .active').data('link');

    function setOptionsToPotentialLeadersSelect(churchId) {
        let config = {
                church: churchId,
            };
        getPotentialLeadersForHG(config).then(function (data) {
            let options = data.map( (item) => {
                let option = document.createElement('option');
                return $(option).val(item.id).text(item.fullname);
            });
            $('#added_home_group_pastor').html(options).prop('disabled', false).select2();
        });
    }

    function reRenderTable(config) {
        addUserToChurch(config).then(() => createChurchesUsersTable(CHURCH_ID));
    }

    function addUserToChurch(data) {
        let userId = data.id;
        let config = {};
        config.user_id = userId;
        return new Promise(function (resolve, reject) {
            let data = {
                method: 'POST',
                url: URLS.church.add_user(CHURCH_ID),
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
                    $(button).attr({
                        'data-id': item.id,
                        'disabled': !item.can_add
                    }).text('Выбрать').on('click', function () {
                        let id = $(this).data('id');
                        let _self = this;
                        let config = {};
                        config.id = id;
                        addUserToChurch(config).then(function (data) {
                            $(_self).text('Добавлен').attr('disabled', true);
                            getChurchStats(CHURCH_ID).then(function (data) {
                                let keys = Object.keys(data);
                                keys.forEach(function (item) {
                                    $('#' + item).text(data[item]);
                                })
                            });
                            createChurchesUsersTable(CHURCH_ID);
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

    createChurchesDetailsTable({}, CHURCH_ID, link);

    $('#added_home_group_pastor').select2();
    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
//    Events
    $('#addHomeGroupToChurch').on('click', function () {
        clearAddHomeGroupData();
        if (!responsibleList) {
            responsibleList = true;
            setOptionsToPotentialLeadersSelect(CHURCH_ID);
        }
        setTimeout(function () {
            $('#addHomeGroup').css('display', 'block');
        }, 100)
    });
    $('#addUserToChurch').on('click', function () {
        // $('#addUser').css('display', 'block');
        initAddNewUser({
            getDepartments: false,
        });
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
        let department_id = $('#church').data('department_id');
        let department_title = $('#church').data('department_title');
        let option = document.createElement('option');
        $(option).val(department_id).text(department_title).attr('selected', true).attr('required', false);
        $(this).closest('.popup').css('display', 'none');
        $('#addNewUserPopup').css('display', 'block');
        $('#chooseDepartment').html(option).attr('disabled', false);
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
    });
    $('#searchUserFromDatabase').on('keyup', _.debounce(function () {
        let search = $(this).val();
        if (search.length < 3) return;
        let config = {};
        config.search = search;
        config.department = D_ID;
        makeUsersFromDatabaseList(config);
    }, 500));

    $('.get_info button').on('click', function () {
        let link = $(this).data('link');
        let exportUrl = $(this).data('export-url');
        let canEdit = $(this).data('editable');
        $('#church').removeClass('can_edit');
        if (canEdit) {
            $('#church').addClass('can_edit');
        }
        createChurchesDetailsTable({}, CHURCH_ID, link);
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

    // $('#addHomeGroupForm').submit(function (e) {
    //     e.preventDefault();
    //     addHomeGroup(this);
    // });

//     function addHomeGroup(el, callback) {
//     let data = getAddHomeGroupData();
//     let json = JSON.stringify(data);
//     addHomeGroupToDataBase(json).then(function (data) {
//         clearAddHomeGroupData();
//         hidePopup(el);
//         callback();
//         showPopup(`Домашняя группа ${data.get_title} добавлена в базу данных`);
//     }).catch(function (data) {
//         hidePopup(el);
//         showPopup('Ошибка при создании домашней группы');
//     });
// }

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
                createNewUser(reRenderTable).then(function () {
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

    $('#addHomeGroup').find('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });

    let department = $('#editDepartmentSelect').val(),
        pastor = $('#editPastorSelect').val();

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
                    if ($(this).is(':not([multiple])')) {
                        if (!$(this).is('.no_select')) {
                            $(this).select2('destroy');
                        }
                    }
                }
            });
            $(this).removeClass('active');
        } else {
            makePastorList(department, '#editPastorSelect', pastor);
            makeDepartmentList('#editDepartmentSelect', department).then(function () {
                $('#editDepartmentSelect').on('change', function () {
                    let id = parseInt($(this).val());
                    makePastorList(id, '#editPastorSelect');
                })
            });
            $('#report_currency').prop('disabled', false).select2();
            $input.each(function () {
                if (!$(this).hasClass('no__edit')) {
                    if ($(this).attr('disabled')) {
                        $(this).attr('disabled', false);
                    }
                    $(this).attr('readonly', false);
                }
            });
            $(this).addClass('active');
        }
    });

    $('.accordion').find('.save__info').on('click', function (e) {
        e.preventDefault();
        let idChurch = $(this).closest('form').attr('data-id');
        editChurches($(this), idChurch);
        let pastorLink = '/account/' + $(this).closest('form').find('#editPastorSelect').val();
        pasteLink($('#editPastorSelect'), pastorLink);
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
