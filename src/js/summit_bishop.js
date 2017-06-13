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
                phone_number: {
                    ordering_title: 'phone_number',
                    title: 'Номер телефона',
                    active: true
                },
                absent: {
                    ordering_title: 'absent',
                    title: 'Присутсвие',
                    active: true
                },
                total: {
                    ordering_title: 'total',
                    title: 'Всего',
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
        const filter = getFilterParam();
        Object.keys(filter).forEach(key => {
            url += `${key}=${filter[key]}`
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
    })
})(jQuery);