(function ($) {

    function createChurchesTable(config = {}) {
        getChurches().then(function (data) {
            console.log(data);
            let count = data.count;
            let filterData = {};
            filterData.results = data.results;
            filterData.user_table = data.table_columns;
            let page = config['page'] || 1;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
            let text = `Показано ${showCount} из ${count}`;
            let tmpl = $('#databaseUsers').html();
            let rendered = _.template(tmpl)(filterData);
            $('#tableChurches').html(rendered);
            makeSortForm(filterData.user_table);
            let paginationConfig = {
                container: ".users__pagination",
                currentPage: page,
                pages: pages,
                callback: createUsersTable
            };
            makePagination(paginationConfig);
            $('.table__count').text(text);
            $('.preloader').css('display', 'none');
        });
    }

    createChurchesTable();
//    Events
    $('#add').on('click', function () {
        $('#addChurch').css('display', 'block');
    })
})(jQuery);