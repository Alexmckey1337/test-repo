(function () {
    "use strict";
    function getPartners(config) {
        config.search = $('input[name=fullsearch]').val();
        getPartnersList(config).then(function (response) {
            let page = config['page'] || 1;
            let count = response.count;
            let pages = Math.ceil(count / CONFIG.pagination_count);
            let data = {};
            let id = "partnersList";
            let text = `Показано ${CONFIG.pagination_count} из ${count}`;
            let common_table = Object.keys(response.common_table);
            data.user_table = response.user_table;
            common_table.forEach(function (item) {
                data.user_table[item] = response.common_table[item];
            });
            data.results = response.results.map(function (item) {
                let result = item.user;
                common_table.forEach(function (key) {
                    result[key] = item[key];
                });
                return result;
            });
            data.count = response.count;
            makeDataTable(data, id);

            $('.preloader').css('display', 'none');
            let paginationConfig = {
                container: ".partners__pagination",
                currentPage: page,
                pages: pages,
                callback: getPartners
            };
            makePagination(paginationConfig);
            $('#table__count').text(text);
            makeSortForm(response.user_table);
            orderTable.sort(getPartners);
        });
    }

    $('#accountable').select2();
    $('input[name=fullsearch]').on('keyup', function () {
        getPartners({
            page: 1
        });
    });
    getPartners({});

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(getPartners);
    });
}());
