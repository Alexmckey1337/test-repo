function initChart(summitId, update = false) {
    getSummitAttends(summitId).then(res => {
        let labels = _.map(res, (el) => moment(el[0]*1000).format('DD.MM')),
            peopleVisit = _.map(res, (el) => el[1][0]),
            peopleAll = _.map(res, (el) => el[1][1]),
            config = setConfig(labels, peopleVisit, peopleAll);
        (update) ? updateChart(window.ChartAttends, labels, peopleVisit, peopleAll) : renderChart(config);
    });
}

function updateChart(chart, labels, peopleVisit, peopleAll) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = peopleAll;
    chart.data.datasets[1].data = peopleVisit;
    chart.update();
}

const CHARTCOLORS = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(60, 174, 218)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
};

function setConfig(labels=[], peopleVisit=[], peopleAll=[]) {
    let config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: "Всего людей",
                    borderColor: CHARTCOLORS.blue,
                    backgroundColor: CHARTCOLORS.blue,
                    data: peopleAll,
                    fill: false,
                }, {
                    label: "Присутствовало",
                    borderColor: CHARTCOLORS.red,
                    backgroundColor: CHARTCOLORS.red,
                    data: peopleVisit,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: "Статистика посещаемости саммита",
                    fontSize: 18,
                },
                legend: {
                    display: true,
                    labels: {
                        fontSize: 14,
                    }
                },
                tooltips: {
                    mode: 'index',
                    callbacks: {
                        footer: (tooltipItems, data) => {
                            let all = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
                                visit = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                                diff = all - visit;
                            return `Отсутствовало: ${diff}`;
                        },
                    },
                    footerFontStyle: 'normal',
                    titleFontSize: 15,
                    bodyFontSize: 13,
                    footerFontSize: 13,
                    titleMarginBottom: 12,
                    bodySpacing: 6,
                },
                hover: {
                    mode: 'index',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            show: true,
                            labelString: 'Day'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            show: true,
                            labelString: 'Value'
                        },
                    }]
                },
                elements: {
                    point: {
                        radius: 5,
                        hoverRadius: 7
                    }
                }
            }
        };

    return config;
}

function renderChart(config) {
    let ctx = document.getElementById("chart_attends").getContext("2d");
    window.ChartAttends = new Chart(ctx, config);
}

$('document').ready(function () {
    let summitId = $('#summit-title').data('summit-id');
    initChart(summitId);

    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block').find('.pop_cont').on('click', function (e) {
            e.preventDefault();
            return false
        });
    });

    $('.select__db').select2();

    $('#departments_filter').on('change', function () {
        $('#master_tree').prop('disabled', true);
        let department_id = parseInt($(this).val()) || null;
        makePastorListNew(department_id, ['#master']);
    });

    $('#applyFilter').on('click', function (e) {
        e.preventDefault();
        let update = true,
            depart = $('#departments_filter option:selected').text(),
            master = $('#master option:selected').text();
        initChart(summitId, update);
        $('.department_title').find('span').text(depart);
        $('.master_title').find('span').text(master);
        $(this).closest('#filterPopup').hide();
        let count = getCountFilter();
        $('#filter_button').attr('data-count', count);
    });

    $('#print').on('click', function () {
        $('body').addClass('is-print');
        setTimeout(window.print,1000);
    });

    (function () {
        let afterPrint = function () {
            $('body').removeClass('is-print');
        };

        if (window.matchMedia) {
            let mediaQueryList = window.matchMedia('print');
            mediaQueryList.addListener(function (mql) {
                if (!mql.matches) {
                    afterPrint();
                }
            });
        }

        window.onafterprint = afterPrint;
    }());
});