function initChart(summitId, update = false) {
    getSummitAttends(summitId).then(res => {
        let labels = _.map(res, (el) => moment(el[0] * 1000).format('DD.MM')),
            peopleVisit = _.map(res, (el) => el[1][0]),
            peopleAll = _.map(res, (el) => el[1][1]),
            config = setConfig(labels, peopleVisit, peopleAll),
            option = {
                chart: window.ChartAttends,
                labels: labels,
                peopleVisit: peopleVisit,
                peopleAll: peopleAll,
            };
        (update) ? updateChart(option) : renderChart(config);
    });
}

function initPieChart() {
    let config = setPieConfig();
    renderPieChart(config);
}

function updatePieChart(summitId, masterId) {
    getSummitStatsForMaster(summitId, masterId).then(res => {
        let labels = _.map(res, (el) => el[0] ),
            peoples = _.map(res, (el) => el[1][0]),
            colors = [];
        for (let i = 0; i < labels.length; i++) {
            colors.push(getRandomColor());
        }
        let option = {
                chart: window.PieStats,
                labels: labels,
                peoples: peoples,
                colors: colors,
            };
        $('#pie_stats').show();
        renderUpdatePieChart(option);
    })
}

function updateChart({chart, labels, peopleVisit, peopleAll}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = peopleAll;
    chart.data.datasets[1].data = peopleVisit;
    chart.update();
}

function renderUpdatePieChart({chart, labels, peoples, colors}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = peoples;
    chart.data.datasets[0].backgroundColor = colors;
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

const PLUGINS = [{
    afterDatasetsDraw: function (chart, easing) {
        let ctx = chart.ctx;
        chart.data.datasets.forEach(function (dataset, i) {
            let meta = chart.getDatasetMeta(i);
            if (!meta.hidden) {
                meta.data.forEach(function (element, index) {
                    ctx.fillStyle = 'rgb(0, 0, 0)';
                    let fontSize = 12,
                        fontStyle = 'normal',
                        fontFamily = 'Helvetica Neue';
                    ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);
                    let dataString = dataset.data[index].toString();
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    let padding = 8,
                        position = element.tooltipPosition();
                    ctx.fillText(dataString, position.x, position.y - (fontSize / 2) - padding);
                });
            }
        });
    }
}];

function getRandomColor() {
    let letters = '0123456789ABCDEF',
        color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function setConfig(labels = [], peopleVisit = [], peopleAll = []) {
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
                    ticks: {
                        min: 0,
                        callback: function (value) {
                            if (Math.floor(value) === value) {
                                return value;
                            }
                        }
                    }
                }]
            },
            elements: {
                point: {
                    radius: 5,
                    hoverRadius: 7
                }
            }
        },
        plugins: PLUGINS
    };

    return config;
}

function setPieConfig(labels = [], peoples = [], colors = []) {
    let config = {
        type: 'doughnut',
        data: {
            datasets: [{
                data: peoples,
                backgroundColor: colors,
                label: 'Dataset 1'
            }],
            labels: labels
        },
        options: {
            responsive: true,
            legend: {
                position: 'top',
                labels: {
                    fontSize: 14,
                }
            },
            title: {
                display: true,
                text: 'Разбивка по ответственному',
                fontSize: 18,
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        },
        plugins: PLUGINS
    };

    return config;
}

function renderChart(config) {
    let ctx = document.getElementById("chart_attends").getContext("2d");
    window.ChartAttends = new Chart(ctx, config);
}

function renderPieChart(config) {
    let ctx = document.getElementById("pie_stats").getContext("2d");
    window.PieStats = new Chart(ctx, config);
    $('#pie_stats').hide();
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
    let data = {
        without_pagination: '',
        level_gte: 4,
        summit: summitId
    };
    makeResponsibleSummitStats(data, ['#master']);

    initPieChart();

    $('#departments_filter').on('change', function () {
        $('#master_tree').prop('disabled', true);
        let department_id = parseInt($(this).val()) || null;
        let data = {
            without_pagination: '',
            level_gte: 4,
            department: department_id,
            summit: summitId,
        };
        makeResponsibleSummitStats(data, ['#master']);
    });

    $('#applyFilter').on('click', function (e) {
        e.preventDefault();
        let update = true,
            depart = $('#departments_filter option:selected').text(),
            master = $('#master option:selected').text();
        initChart(summitId, update);
        let filter = $('#master').val();
        (filter !== 'ВСЕ') ? updatePieChart(summitId, filter) : $('#pie_stats').hide();
        $('.department_title').find('span').text(depart);
        $('.master_title').find('span').text(master);
        $(this).closest('#filterPopup').hide();
        let count = getCountFilter();
        $('#filter_button').attr('data-count', count);
    });

    $('#print').on('click', function () {
        $('body').addClass('is-print');
        setTimeout(window.print, 300);
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