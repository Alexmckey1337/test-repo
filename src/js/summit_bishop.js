class BishopReport {
    constructor(id){
        this.summitId = id;
        this.data = {
            results: [],
            user_table: {
                user_name: {
                    ordering_title: 'user_name',
                    title: 'ФИО',
                    active: true
                },
                total: {
                    ordering_title: 'total',
                    title: 'Всего',
                    active: true
                },
                attend: {
                    ordering_title: 'attend',
                    title: 'Присутствует',
                    active: true
                },
                absent: {
                    ordering_title: 'absent',
                    title: 'Отсутствует',
                    active: true
                },
                phone_number: {
                    ordering_title: 'phone_number',
                    title: 'Номер телефона',
                    active: true
                }
            }
        };
    }
    renderTable(){
        let tmpl = $('#databaseUsers').html();
        return _.template(tmpl)(this.data);
    }
    makeTable() {
        this.getReport().then(data => {
            this.data.results = data;
            $('#bishopsReports').html(this.renderTable());
            $('.table__count').html(`Показано ${this.data.results.length}`)
        });
    }
    getReport() {
        let url = `/api/v1.0/summit/${this.summitId}/report_by_bishops/?`;
        const filter = Object.assign(getFilterParam(), getSearch('search_fio'));
        Object.keys(filter).forEach((key, i, arr) => {
            url += `${key}=${filter[key]}`;
            if (i + 1 < arr.length) {
                url += '&'
            }
        });
        let options = {
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
        };
       return fetch(url, options)
           .then(res => res.json());
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
                    <div class="block">
                        <ul class="info">
                            <li>
                                <div class="label-wrapp">
                                    <label>Выберите ответсвенного</label>
                                </div>
                                <div class="input">
                                    <select class="master">`; content += options.join(','); content += `</select>
                                </div>
                            </li>
                            <li>
                                <div class="label-wrapp">
                                    <label>Пристутствие</label>
                                </div>
                                <div class="input">
                                    <select class="attended">
                                        <option value="">ВСЕ</option>
                                        <option value="true">ДА</option>
                                        <option value="false">НЕТ</option>
                                    </select>
                                </div>
                            </li>
                            <li>
                                <div class="label-wrapp">
                                    <label>Дата</label>
                                </div>
                                <div class="input">
                                    <input class="date" type="text">
                                </div>
                            </li>
                        </ul>
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
    const report = new BishopReport(summitId);
    report.makeTable();

    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block').find('.pop_cont').on('click', function (e) {
            e.preventDefault();
            return false
        });
    });
    $('#applyFilter').on('click', function () {
         report.makeTable();
         $(this).closest('#filterPopup').hide();
         let count = getCountFilter();
        $('#filter_button').attr('data-count', count);
    });
     $('#download').on('click', function () {
        let stat = new PrintMasterStat(summitId);
        stat.show();
    });
     $('input[name="fullsearch"]').on('keyup', function () {
         report.makeTable();
     });
})(jQuery);