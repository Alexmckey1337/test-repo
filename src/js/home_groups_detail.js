(function ($) {
    let tableUserINHomeGroups;
    const ID = $('#home_group').data('id');
    const HG_ID = $('#home_group').data('departament_id');
    const HG_TITLE = $('#home_group').data('departament_title');

    function createHomeGroupUsersTable(config = {}) {
        getHomeGroupUsers(ID).then(function (data) {
            console.log(data);
            let count = data.count;
            let page = config['page'] || 1;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
            let text = `Показано ${showCount} из ${count}`;
            let tmpl = $('#databaseUsers').html();
            let filterData = {};
            filterData.user_table = data.table_columns;
            filterData.results = data.results;
            let rendered = _.template(tmpl)(filterData);
            $('#tableUserINHomeGroups').html(rendered);
            makeSortForm(filterData.user_table);
            let paginationConfig = {
                container: ".users__pagination",
                currentPage: page,
                pages: pages,
                callback: createHomeGroupUsersTable
            };
            makePagination(paginationConfig);
            $('.table__count').text(text);
            $('.preloader').css('display', 'none');
        })
    }

    function addUserToHomeGroup(id, el) {
        $(el).attr('disabled', true).text('Добавлен');
        console.log(id)
    }

    function makeUsersFromDatabaseList(config = {}) {
        getUsersFromDatabase(config).then(function (data) {
            let users = data.results;
            let html = [];
            users.forEach(function (item) {
                let rows_wrap = document.createElement('div');
                let rows = document.createElement('div');
                let col_1 = document.createElement('div');
                let col_2 = document.createElement('div');
                let place = document.createElement('p');
                let link = document.createElement('a');
                let button = document.createElement('button');
                $(link).attr('href', '/account/' + item.id).text(item.fullname);
                $(place).text();
                $(col_1).addClass('col').append(link);
                $(col_2).addClass('col').append(item.city);
                $(rows).addClass('rows').append(col_1).append(col_2);
                $(button).attr('data-id', item.id).text('Выбрать').on('click', function () {
                    let id = $(this).data('id');
                    let _self = this;
                    addUserToHomeGroup(id, _self);
                });
                $(rows_wrap).addClass('rows-wrap').append(button).append(rows);
                html.push(rows_wrap);
            });
            $('#searchedUsers').html(html);
            $('.choose-user-wrap .splash-screen').addClass('active');
        })
    }

    createHomeGroupUsersTable();

    getStatuses().then(function (data) {
        let statuses = data.results;
        let rendered = [];
        let option = document.createElement('option');
        $(option).text('Выбирите статус').attr('disabled', true).attr('selected', true);
        rendered.push(option);
        statuses.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).attr('data-level', item.level).text(item.title);
            rendered.push(option);
        });
        return rendered;
    }).then(function (rendered) {
        $('#chooseStatus').html(rendered).select2().on('change', function () {
            let status = $(this).val();
            getResponsible(HG_ID, status).then(function (data) {
                let rendered = [];
                data.forEach(function (item) {
                    let option = document.createElement('option');
                    $(option).val(item.id).text(item.fullname);
                    rendered.push(option);
                });
                $('#chooseResponsible').html(rendered).attr('disabled', false).select2();
            })
        });
    });

    getDivisions().then(function (data) {
        let divisions = data.results;
        let rendered = [];
        divisions.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.title);
            rendered.push(option);
        });
        $('#chooseDivision').html(rendered).select2();
    });
    getCountryCodes().then(function (data) {
        let codes = data;
        let rendered = [];
        codes.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.phone_code).text(item.title + ' ' + item.phone_code);
            if (item.phone_code == '+38') {
                $(option).attr('selected', true);
            }
            rendered.push(option);
        });
        $('#chooseCountryCode').html(rendered).on('change', function () {
            let code = $(this).val();
            $('#phoneNumberCode').val(code);
        }).trigger('change');
    });

    getCountries().then(function (data) {
        let rendered = [];
        let option = document.createElement('option');
        $(option).text('Выберите страну').attr('disabled', true).attr('selected', true);
        rendered.push(option);
        data.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.title);
            rendered.push(option);
        });
        $('#chooseCountry').html(rendered).on('change', function () {
            let config = {};
            config.country = $(this).val();
            getRegions(config).then(function (data) {
                let rendered = [];
                let option = document.createElement('option');
                $(option).text('Выберите регион');
                rendered.push(option);
                data.forEach(function (item) {
                    let option = document.createElement('option');
                    $(option).val(item.id).text(item.title);
                    rendered.push(option);
                });
                $('#chooseRegion').html(rendered).attr('disabled', false).on('change', function () {
                    let config = {};
                    config.country = $(this).val();
                    getCities(config).then(function (data) {
                        let rendered = [];
                        let option = document.createElement('option');
                        $(option).text('Выберите регион');
                        rendered.push(option);
                        data.forEach(function (item) {
                            let option = document.createElement('option');
                            $(option).val(item.id).text(item.title);
                            rendered.push(option);
                        });
                        $('#chooseCity').html(rendered).attr('disabled', false).select2();
                    })
                }).select2();
            })
        }).select2();
    });
// Events
    $('#add_userToHomeGroup').on('click', function () {
        $('#addUser').css('display', 'block');
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
        $('#chooseDepartment').append(option);
    });
    $('#searchUserFromDatabase').on('keyup', function () {
        let search = $(this).val();
        if (search.length < 3) return;
        let config = {};
        config.search_fio = search;
        makeUsersFromDatabaseList(config);
    });
    $('#partner').on('change', function () {
        let partner = $(this).is(':checked');
        if (partner) {
            $('.hidden-partner').css('display', 'block');
        } else {
            $('.hidden-partner').css('display', 'none');
        }
    });
    $('#repentanceDate').datepicker();
    $('#search_name').datepicker();
    $('#chooseCountryCode').select2();
})(jQuery);
