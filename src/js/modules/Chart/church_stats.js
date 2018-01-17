'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import {CHARTCOLORS, setConfig, setMixedConfig} from "./config";

export function initCharts(data, update, isGroup) {
    let {
        configPeoplesChart,
        configFinChart,
        configFinPastorTithe,
        optionPeoplesChart,
        optionFinChart,
        optionFinPastorTithe,
        selectPeoplesChart,
        selectFinChart,
        selectFinPastorTithe,
    } = makeChartConfig(data, isGroup);
    if (update) {
        updateFinChart(optionPeoplesChart);
        updateFinChart(optionFinChart);
        updateFinPastorTithe(optionFinPastorTithe);
    } else {
        renderChart(selectPeoplesChart, configPeoplesChart);
        renderChart(selectFinChart, configFinChart);
        renderChart(selectFinPastorTithe, configFinPastorTithe);
    }
}

function makeChartConfig(data, isGroup) {
    let labels,
        allPeoples = [],
        newPeoples = [],
        repentances = [],
        donations = [],
        tithe = [],
        pastorTithe = [],
        percent = [];

    (isGroup === '1m') ?
        labels = data.map(item => `${item.week} нед. ${item.year}-${(item.month < 10) ? '0' + item.month : item.month}`)
        :
        labels = data.map(item => `${item.year}-${(item.month < 10) ? '0' + item.month : item.month}`);

    labels.map((item, index) => {
        let elem = data[index];
        allPeoples.push(elem.count_people);
        newPeoples.push(elem.count_new_people);
        repentances.push(elem.count_repentance);
        donations.push(elem.donations);
        tithe.push(elem.tithe);
        pastorTithe.push(elem.pastor_tithe);
        percent.push(elem.transfer_payments);
    });
    let datasetsFinChart = {
            labels: labels,
            datasets: [{
                type: 'line',
                label: '15% к перечислению',
                borderColor: CHARTCOLORS.red,
                backgroundColor: CHARTCOLORS.red,
                borderWidth: 2,
                yAxisID: "y-axis-0",
                lineTension: 0,
                data: percent,
                fill: false,
            },
                {
                    label: 'Пожертвования',
                    backgroundColor: CHARTCOLORS.yellow,
                    yAxisID: "y-axis-0",
                    data: donations
                }, {
                    label: 'Десятины',
                    backgroundColor: CHARTCOLORS.blue,
                    yAxisID: "y-axis-0",
                    data: tithe
                }]
        },
        datasetsFinPastorTitheChart = [{
            label: "Десятина пастора",
            borderColor: CHARTCOLORS.green,
            backgroundColor: CHARTCOLORS.green,
            data: pastorTithe,
            lineTension: 0,
            fill: false,
        }],
        datasetsPeoplesChart = [{
            label: "Всего людей",
            borderColor: CHARTCOLORS.yellow,
            backgroundColor: CHARTCOLORS.yellow,
            data: allPeoples,
            lineTension: 0,
            fill: false,
        },
            {
                label: "Новые люди",
                borderColor: CHARTCOLORS.green,
                backgroundColor: CHARTCOLORS.green,
                data: newPeoples,
                lineTension: 0,
                fill: false,
            },
            {
                label: "Покаяния",
                borderColor: CHARTCOLORS.red,
                backgroundColor: CHARTCOLORS.red,
                data: repentances,
                lineTension: 0,
                fill: false,
            },
        ],
        titleFinChart = "Статистика по финансам",
        titleFinPastorTitheChart = "Статистика по десятинам пастора",
        titlePeoplesChart = "Статистика по людям",
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
            }
        }],
        callbackFinChart = {
            footer: (tooltipItems, data) => {
                let sumDonations = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                    sumTithe = data.datasets[tooltipItems[2].datasetIndex].data[tooltipItems[2].index],
                    totalSum = sumDonations + sumTithe;
                return `Общая сумма: ${totalSum}`;
            },
        },
        configFinChart = setMixedConfig(datasetsFinChart, titleFinChart, callbackFinChart),
        configFinPastorTithe = setConfig('line', labels, datasetsFinPastorTitheChart, titleFinPastorTitheChart, xAxes, yAxes),
        configPeoplesChart = setConfig('line', labels, datasetsPeoplesChart, titlePeoplesChart, xAxes, yAxes),
        optionFinChart = {
            chart: window.ChartFin,
            labels: labels,
            line1: percent,
            line2: donations,
            line3: tithe,
        },
        optionFinPastorTithe = {
            chart: window.ChartFinPastor,
            labels: labels,
            line1: pastorTithe,
        },
        optionPeoplesChart = {
            chart: window.ChartPeoples,
            labels: labels,
            line1: allPeoples,
            line2: newPeoples,
            line3: repentances,
        },
        selectPeoplesChart = 'chart_peoples',
        selectFinChart = 'chart_finances',
        selectFinPastorTithe = 'chart_finances_pastor';

    return {
        configPeoplesChart,
        configFinChart,
        configFinPastorTithe,
        optionPeoplesChart,
        optionFinChart,
        optionFinPastorTithe,
        selectPeoplesChart,
        selectFinChart,
        selectFinPastorTithe,
    }
}

function updateFinChart({chart, labels, line1, line2, line3}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.data.datasets[2].data = line3;
    chart.update();
}

function updateFinPastorTithe({chart, labels, line1}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.update();
}

function renderChart(select, config) {
    let ctx = document.getElementById(select).getContext("2d");
    if (select == 'chart_finances') {
        window.ChartFin = new Chart(ctx, config);
    } else if (select == 'chart_finances_pastor') {
        window.ChartFinPastor = new Chart(ctx, config);
    } else {
        window.ChartPeoples = new Chart(ctx, config);
    }
}