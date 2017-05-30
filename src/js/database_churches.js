(function ($) {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#tree_filter'),
        $pastorFilter = $('#pastor_filter');
    let filterInit = (function () {
        let init = false;
        const USER_ID = $('body').data('id');
        return function () {
            if (!init) {
                getPastorsByDepartment({
                    master_tree: USER_ID
                }).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                    $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                init = true;
            }
        }
    })();

    createChurchesTable();
    $departmentsFilter.select2();
    $('#department_select').select2();
    $('#pastor_select').select2();
    $('#tree_filter').select2();
    $('#hierarchies_filter').select2();
    $('#pastor_filter').select2();
    $('#search_is_open').select2();
    $('#added_churches_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#search_date_open').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
//    Events
    $('#add').on('click', function () {
        let department_id = parseInt($('#department_select').val());
        clearAddChurchData();
        makePastorList(department_id, '#pastor_select');
        setTimeout(function () {
            $('#addChurch').css('display', 'block');
        }, 100);
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id, '#pastor_select');
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesTable);
    });
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
    });
    $('input[name="fullsearch"]').on('keyup', function () {
        createChurchesTable();
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

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {
            level_gte: 2
        };
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
        }
        getPastorsByDepartment({
            department_id: departamentID
        })
            .then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $('#pastor_filter').html('<option>ВСЕ</option>').append(pastors);
                $('#tree_filter').html('<option>ВСЕ</option>').append(pastors);
            });
    });

    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config = {
                master_tree: $(this).val()
            };
        }
        getPastorsByDepartment(config).then(function (data) {
             const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $('#pastor_filter').html('<option>ВСЕ</option>').append(pastors);
        });
    });
})(jQuery);