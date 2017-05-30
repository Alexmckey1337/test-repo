(function ($) {
    let filterInit = (function () {
        let init = false;
        const USER_ID = $('body').data('id');
        return function () {
            if (!init) {
                getLeadersByChurch({
                    master_tree: USER_ID
                }).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $('#tree_filter').html('<option>ВСЕ</option>').append(leaders);
                    $('#leader_filter').html('<option>ВСЕ</option>').append(leaders);
                });
                init = true;
            }
        }
    })();

    let $departmentSelect = $('#department_select');
    createHomeGroupsTable();
    let $churchFilter = $('#church_filter');
    let $treeFilter = $('#tree_filter');
    $departmentSelect.select2();
    $('#pastor_select').select2();
    $('.selectdb').select2();
    $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    // Events
    $('#add').on('click', function () {
        clearAddHomeGroupData();
        let church_id = $('#added_home_group_church').attr('data-id');
        let user_id = $('#added_home_group_church').attr('data-user');
        let config = {
            master_tree: user_id,
            church_id: church_id,
        };
        getResponsibleBYHomeGroupNew(config).then(function (data) {
            let pastors = data.map((pastor) => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#added_home_group_pastor').html(pastors).prop('disabled', false).select2();
        });
        setTimeout(function () {
            $('#addHomeGroup').css('display', 'block');
        }, 100);
    });

    $departmentSelect.on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupsTable);
    });
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });
    $('input[name="fullsearch"]').on('keyup', function () {
        createHomeGroupsTable();
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
    $churchFilter.on('change', function () {
        let churchesID = $(this).val();
        let config = {};
        if (churchesID) {
            config = {
                church_id: churchesID
            }
        }
        getLeadersByChurch(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#tree_filter').html('<option>ВСЕ</option>').append(pastors);
            $('#leader_filter').html('<option>ВСЕ</option>').append(pastors);
            // let options = [];
            // let option = document.createElement('option');
            // $(option).text('ВСЕ').attr('selected', true);
            // options.push(option);
            // data.forEach(function (item) {
            //     let option = document.createElement('option');
            //     $(option).val(item.id).text(item.fullname);
            //     options.push(option);
            // });
            //
            // $('#tree_filter').html(options);
        })
    });
    $treeFilter.on('change', function () {
        let masterTreeID = $(this).val();
        let config = {};
        if (masterTreeID) {
            config = {
                master_tree: masterTreeID
            }
        }
        getLeadersByChurch(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#leader_filter').html('<option>ВСЕ</option>').append(pastors);
            // let options = [];
            // let option = document.createElement('option');
            // $(option).text('ВСЕ').attr('selected', true);
            // options.push(option);
            // data.forEach(function (item) {
            //     let option = document.createElement('option');
            //     $(option).val(item.id).text(item.fullname);
            //     options.push(option);
            // });
            // $('#leader_filter').html(options);
        });
    });
})(jQuery);