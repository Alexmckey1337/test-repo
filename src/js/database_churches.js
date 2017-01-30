(function ($) {

    function createChurchesTable(config = {}) {
        getChurches().then(function (data) {
            console.log(data);
            let count = data.count;
            let page = config['page'] || 1;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
            let text = `Показано ${showCount} из ${count}`;
            let tmpl = $('#databaseUsers').html();
            let rendered = _.template(tmpl)(data);
            $('#tableChurches').html(rendered);
            makeSortForm(data.user_table);
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