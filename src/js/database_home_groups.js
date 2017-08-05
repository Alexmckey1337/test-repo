(function ($) {
    let filterInit = (function () {
        let init = false;
        return function () {
            if (!init) {
                getHGLeaders().then(res => {
                    const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $('#tree_filter').html('<option value="">ВСЕ</option>').append(leaders);
                    $('#leader_filter').html('<option value="">ВСЕ</option>').append(leaders);
                });
                init = true;
            }
        }
    })();

    function getConfigSuperMega() {
        const churchId = $('#added_home_group_church_select').val() || null;
        const masterId = $('#available_master_tree_id').val() || null;
        let config = {
            church: churchId,
        };
        if (masterId) {
            config.master_tree = masterId;
        }
        return config
    }
    function updateLeaderSelect() {
        const config = getConfigSuperMega();
        getPotentialLeadersForHG(config).then(function (data) {
            const pastors = data.map((pastor) => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#added_home_group_pastor').html(pastors).prop('disabled', false).select2();
        });
    }

    let $departmentSelect = $('#department_select');
    const $churchSelect = $('#added_home_group_church_select');
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
        updateLeaderSelect();
        setTimeout(function () {
            $('#addHomeGroup').css('display', 'block');
        }, 100);
    });

    if ($churchSelect) {
        $churchSelect.on('change', function () {
            updateLeaderSelect();
        });
    }

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
        let churchID = $(this).val();
        let config = {};
        if (churchID) {
            config.church = churchID;
        }
        getHGLeaders(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#tree_filter').html('<option value="">ВСЕ</option>').append(pastors);
            $('#leader_filter').html('<option value="">ВСЕ</option>').append(pastors);
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
        getHGLeaders(config).then(function (data) {
            const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
            $('#leader_filter').html('<option value="">ВСЕ</option>').append(pastors);
        });
    });
})(jQuery);