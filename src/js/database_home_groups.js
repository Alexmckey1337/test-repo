(function ($) {
    function makePastorList(id) {
        getResponsible(id, 2).then(function (data) {
            let options = [];
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.fullname);
                options.push(option);
            });
            $('#pastor_select').html(options).prop('disabled', false);
        });
    }

    function createHomeGroupsTable(config = {}) {
        config.search_title = $('input[name="fullsearch"]').val();
        getHomeGroups(config).then(function (data) {
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
            $('#tableHomeGroup').html(rendered);
            $('.quick-edit').on('click', function () {
                let id = $(this).closest('.edit').find('a').attr('data-id');
                ajaxRequest(`${CONFIG.DOCUMENT_ROOT}api/v1.0/home_groups/${id}/`, null, function (data) {
                    let quickEditCartTmpl, rendered;
                    quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                    rendered = _.template(quickEditCartTmpl)(data);
                    $('#quickEditCartPopup .popup_body').html(rendered);
                    $('#opening_date').datepicker({
                        dateFormat: 'yyyy-mm-dd'
                    });
                    // makePastorList(id, '#pastorSelect', data.department);
                    // makeDepartmentList('#departmentSelect', data.department);
                    setTimeout(function () {
                        $('#quickEditCartPopup').css('display', 'block');
                    }, 100)
                })
            });
            makeSortForm(filterData.user_table);
            let paginationConfig = {
                container: ".users__pagination",
                currentPage: page,
                pages: pages,
                callback: createHomeGroupsTable
            };
            makePagination(paginationConfig);
            $('.table__count').text(text);
            $('.preloader').css('display', 'none');
        });
    }

    createHomeGroupsTable();

    $('#department_select').select2();
    $('#pastor_select').select2();
//    Events
    $('#add').on('click', function () {
        var department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
        $('#addChurch').css('display', 'block');
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        var department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
    });
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupsTable);
    });
    $('input[name="fullsearch"]').on('keyup', function () {
        createHomeGroupsTable();
    })
})(jQuery);