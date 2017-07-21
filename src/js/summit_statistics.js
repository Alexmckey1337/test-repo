function initChart(id, update = false) {
    let url = URLS.summit.attends(id);
    getSummitStats(url).then(res => {
        let labels = _.map(res, (el) => moment(el[0] * 1000).format('DD.MM')),
            peopleVisit = _.map(res, (el) => el[1][0]),
            peopleAll = _.map(res, (el) => el[1][1]),
            datasets = [{
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
            }],
            title = "Статистика посещаемости саммита",
            callback = {
                    footer: (tooltipItems, data) => {
                        let all = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
                            visit = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                            diff = all - visit;
                        return `Отсутствовало: ${diff}`;
                    },
                },
            xAxes = [{
                    display: true,
                    scaleLabel: {
                        show: true,
                        labelString: 'Day'
                    }
                }],
            yAxes = [{
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
                }],
            config = setConfig('line', labels, datasets, title, xAxes, yAxes, callback),
            option = {
                chart: window.ChartAttends,
                labels: labels,
                line1: peopleAll,
                line2: peopleVisit,
            },
            select = 'chart_attends';
        (update) ? updateChart(option) : renderChart(select, config);
    });
}

function initBarChart(id, update = false) {
    let url = URLS.summit.stats_latecomer(id);
    getSummitStats(url).then(res => {
        let labels = _.map(res, (el) => moment(el[0] * 1000).format('DD.MM')),
            peopleLate = _.map(res, (el) => el[1][0]),
            peopleInTime = _.map(res, (el) => el[1][1]),
            datasets = [{
                label: "Опоздавшие",
                borderColor: CHARTCOLORS.red,
                backgroundColor: CHARTCOLORS.red,
                data: peopleLate,
            }, {
                label: "Вовремя",
                borderColor: CHARTCOLORS.green,
                backgroundColor: CHARTCOLORS.green,
                data: peopleInTime,
            }],
            title = "Статистика опоздавших",
            xAxes = [{
                stacked: true,
            }],
            yAxes = [{
                stacked: true,
            }],
            config = setConfig('bar', labels, datasets, title, xAxes, yAxes),
            option = {
                chart: window.ChartLatecomers,
                labels: labels,
                line1: peopleInTime,
                line2: peopleLate,
            },
            select = 'chart_latecomer';
        (update) ? updateChart(option) : renderBarChart(select, config);
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

function updateChart({chart, labels, line1, line2}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
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
                        fontFamily = 'Open Sans, sans-serif';
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

function setConfig(type = 'line', labels = [], datasets = [], title = '', xAxes = [], yAxes = [], callback = {} ) {
    let config = {
        type: type,
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: title,
                fontSize: 18,
                fontFamily: 'Open Sans, sans-serif'
            },
            legend: {
                display: true,
                labels: {
                    fontSize: 14,
                },
                fontFamily: 'Open Sans, sans-serif'
            },
            tooltips: {
                mode: 'index',
                callbacks: callback,
                footerFontStyle: 'normal',
                titleFontSize: 15,
                bodyFontSize: 13,
                footerFontSize: 13,
                titleMarginBottom: 12,
                bodySpacing: 6,
                titleFontFamily: 'Open Sans, sans-serif',
                bodyFontFamily: 'Open Sans, sans-serif',
                footerFontFamily: 'Open Sans, sans-serif'
            },
            hover: {
                mode: 'index',
                intersect: true
            },
            scales: {
                xAxes: xAxes,
                yAxes: yAxes,
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
                position: 'left',
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

function renderChart(select, config) {
    let ctx = document.getElementById(select).getContext("2d");
    window.ChartAttends = new Chart(ctx, config);
}

function renderBarChart(select, config) {
    let ctx = document.getElementById(select).getContext("2d");
    window.ChartLatecomers = new Chart(ctx, config);
}

function renderPieChart(config) {
    let ctx = document.getElementById("pie_stats").getContext("2d");
    window.PieStats = new Chart(ctx, config);
    $('#pie_stats').hide();
}

$('document').ready(function () {
    let summitId = $('#summit-title').data('summit-id');
    initChart(summitId);
    initBarChart(summitId);

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
        initBarChart(summitId, update);
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