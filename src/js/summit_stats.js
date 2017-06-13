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
        let url = `/api/v1.0/summits/${this.summitID }/stats/?`;
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
            })
    }
}

class PrintMasterStat {
    constructor(summitId) {
        this.summit = summitId;
        this.masterId = null;
        this.filter = [];
        this.url = `/api/v1.0/summit/${summitId}/master/`
    }

    setMaster(id) {
        this.masterId = id;
    }

    setFilterData(data) {
        this.setMaster(data.id);
        if (data.attended) {
            this.filter.push({
                attended: data.attended,
            });
        }
        if (data.date) {
            this.filter.push({
                date: data.date
            });
        }
        this.makeLink();
    }

    getMasters() {
        let defaultOption = {
            method: 'GET',
            credentials: "same-origin",
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
        return fetch(`/api/v1.0/summits/${this.summit}/bishop_high_masters/`, defaultOption)
            .then(res => res.json());
    }

    show() {
        this.getMasters()
            .then(data => data.map(item => `<option value="${item.id}">${item.full_name}</option>`))
            .then(options => {
                let content = `
                    <div>
                    <label>Выберите ответсвенного</label>
                        <select class="master">`;
                content += options.join(',');
                content += `</select>
                                    </div>
                                        <div>
                                        <label>Пристутствие</label>
                                        <select class="attended">
                                            <option value="">ВСЕ</option>
                                            <option value="true">ДА</option>
                                            <option value="false">НЕТ</option>
                                        </select>
                                    </div>
                                    <div>
                                    <label>Дата</label>
                                    <input class="date" type="text">
                                    </div>`;
                showStatPopup(content, 'Сформировать файл статистики', this.setFilterData.bind(this));
            });

    }

    print() {
        if (!this.masterId) {
            showPopup('Выберите мастера для печати');
            return
        }
        let defaultOption = {
            method: 'GET',
            credentials: "same-origin",
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
        return fetch(`${this.url}${this.masterId}.pdf`, defaultOption).then(data => data.json()).catch(err => err);
    }

    makeLink() {
        console.log(this.filter);
        if (!this.masterId) {
            showPopup('Выберите мастера для печати');
            return
        }
        let link = `${this.url}${this.masterId}.pdf?`;
        this.filter.forEach(item => {
            let key = Object.keys(item);
            link += `${key[0]}=${item[key[0]]}&`
        });
        link += 'short';
        showPopup(`<a class="btn" href="${link}">Скачать</a>`, 'Скачать статистику');
    }
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
    });
    $('input[name="fullsearch"]').keyup(function () {
        delay(function () {
            summit.makeDataTable();
        }, 100);
    });

    $('.select__db').select2();

    $('#departments_filter').on('change', function () {
        $('#master_tree').prop('disabled', true);
        let department_id = parseInt($(this).val());
        makePastorListNew(department_id, ['#master_tree', '#master']);
    });
    $('#master_tree').on('change', function () {
        $('#master').prop('disabled', true);
        let master_tree = parseInt($(this).val());
        makePastorListWithMasterTree({
            master_tree: master_tree
        }, ['#master'], null);
    });
    $('#download').on('click', function () {
        let stat = new PrintMasterStat(summitId);
        stat.show();
    });
    summit.makeDataTable();
})(jQuery);