class SummitStat {
    constructor(id) {
        this.summitID = id;
        this.sortTable = new OrderTable();
    }

    getStatsData(config = {}) {
        let options = {
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
        };
        let url = `${URLS.summit.stats(this.summitID)}?`;
        Object.keys(config).forEach((param, i, arr) => {
            url += `${param}=${config[param]}`;
            if (i + 1 < arr.length) {
                url += '&'
            }
        });
        return fetch(url, options)
            .then(res => res.json())
    }

    makePage(count, length, page = 1) {
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : length;
        let text = `Показано ${showCount} из ${count}`;
        $('.table__count').html(text);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: this.makeDataTable.bind(this)
        };
        makePagination(paginationConfig);
    }

    makeDataTable(config = {}) {
        Object.assign(config, getFilterParam(), getTabsFilter(), getSearch('search_fio'));
        this.getStatsData(config)
            .then(data => {
                this.makePage(data.count, data.results.length, config.page);
                makeSammitsDataTable(data, 'summitUsersList');
                makeSortForm(data.user_table);
                this.sortTable.sort(this.makeDataTable.bind(this), ".table-wrap th");
                $('.preloader').css('display', 'none');
                changeSummitStatusCode();
            });
    }
}

function changeSummitStatusCode() {
    $('#summitUsersList').find('.ticket_code').find('input').on('change', function () {
        let id = $(this).closest('.ticket_code').attr('data-id'),
            ban = $(this).prop("checked") ? 0 : 1,
            option = {
                method: 'POST',
                credentials: 'same-origin',
                headers: new Headers({
                    'Content-Type': 'application/json',
                }),
                body: JSON.stringify({
                    anket_id: id,
                    active: ban
                })
            };
        fetch(URLS.profile_status(), option)
            .then(
                $(this).closest('.ticket_code').find('a').toggleClass('is-ban')
            )

    });
}

(function ($) {
    const summitId = $('#summit-title').data('summit-id');
    const summit = new SummitStat(summitId);
    $('#tabsFilterData')
        .val(moment().format('YYYY-MM-DD'))
        .datepicker({
            dateFormat: 'yyyy-mm-dd',
            autoClose: true,
            maxDate: new Date(),
            onSelect: function () {
                summit.makeDataTable();
            }
        });
    $('.week').on('click', function () {
        $('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('day_prev')) {
            $('#tabsFilterData').val(moment().subtract(1, 'days').format('YYYY-MM-DD'))
        } else {
            $('#tabsFilterData').val(moment().format('YYYY-MM-DD'))
        }
        summit.makeDataTable();
    });
    $('#tabs').find('li').on('click', function () {
        $('#tabs').find('li').removeClass('active');
        $(this).addClass('active');
        summit.makeDataTable();
    });
    getTabsFilter();
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block').find('.pop_cont').on('click', function (e) {
            e.preventDefault();
            return false
        });
    });

    $('#applyFilter').on('click', function (e) {
        e.preventDefault();
        summit.makeDataTable();
        $(this).closest('#filterPopup').hide();
        let count = getCountFilter();
        $('#filter_button').attr('data-count', count);
    });
    $('input[name="fullsearch"]').keyup(function () {
        delay(function () {
            summit.makeDataTable();
        }, 100);
    });

    $('.select__db').select2();

    $('#departments_filter').on('change', function () {
        $('#master_tree').prop('disabled', true);
        let department_id = parseInt($(this).val()) || null;
        makePastorListNew(department_id, ['#master_tree', '#master']);
    });
    $('#master_tree').on('change', function () {
        $('#master').prop('disabled', true);
        let config = {};
        let master_tree = parseInt($(this).val());
        if (!isNaN(master_tree)) {
            config = {master_tree: master_tree}
        }
        makePastorListWithMasterTree(config, ['#master'], null);
    });
    $('#export_table').on('click', function () {
        $('.preloader').css('display', 'block');
        exportTableData(this, getTabsFilter()).then(function () {
            $('.preloader').css('display', 'none');
        });
    });
    // $('.select_time_filter').datepicker({
    //     dateFormat: ' ',
    //     timepicker: true,
    //     onlyTimepicker: true,
    //     classes: 'only-timepicker'
    // });
    $('#time_from').timepicker({
        timeFormat: 'H:mm',
        interval: 30,
        minTime: '0',
        maxTime: '23:30',
        dynamic: true,
        dropdown: true,
        scrollbar: true,
        change: function () {
            summit.makeDataTable();
        }
    });

    $('#time_to').timepicker({
        timeFormat: 'H:mm',
        interval: 30,
        minTime: '0',
        maxTime: '23:30',
        dynamic: true,
        dropdown: true,
        scrollbar: true,
        change: function () {
            summit.makeDataTable();
        }
    });

    summit.makeDataTable();
})(jQuery);