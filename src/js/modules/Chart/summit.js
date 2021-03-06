'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {getSummitStats, getSummitStatsForMaster} from "../Statistics/summit";
import {CHARTCOLORS, PLUGINS, setConfig, getRandomColor} from "./config";

export function initChart(id, update = false) {
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
        $('.preloader_chart').hide();
    });
}

function updateChart({chart, labels, line1, line2}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.update();
}

function renderChart(select, config) {
    let ctx = document.getElementById(select).getContext("2d");
    window.ChartAttends = new Chart(ctx, config);
}

export function initBarChart(id, update = false) {
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
                line1: peopleLate,
                line2: peopleInTime,
            },
            select = 'chart_latecomer';
        (update) ? updateChart(option) : renderBarChart(select, config);
    });
}

export function initPieChart() {
    let config = setPieConfig();
    renderPieChart(config);
}

export function updatePieChart(summitId, masterId) {
    getSummitStatsForMaster(summitId, masterId).then(res => {
        let labels = _.map(res, (el) => el[0]),
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

function renderUpdatePieChart({chart, labels, peoples, colors}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = peoples;
    chart.data.datasets[0].backgroundColor = colors;
    chart.update();
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
            labels: labels,
            borderWidth: 100
        },
        options: {
            responsive: false,
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
            },
        },
        plugins: PLUGINS
    };

    return config;
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