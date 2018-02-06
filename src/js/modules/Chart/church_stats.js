'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import {CHARTCOLORS, setConfig, setMixedConfig} from "./config";
import beautifyNumber from '../beautifyNumber';

export function initCharts(data, update, isGroup, curType) {
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
    } = makeChartConfig(data, isGroup, curType);
    if (update) {
        updateChart(optionPeoplesChart);
        updateChart(optionFinChart);
        updateFinPastorTithe(optionFinPastorTithe);
    } else {
        renderChart(selectPeoplesChart, configPeoplesChart);
        renderChart(selectFinChart, configFinChart);
        renderChart(selectFinPastorTithe, configFinPastorTithe);
    }
}

function makeChartConfig(data, isGroup = '1m', curType) {
    let labels,
        allPeoples = [],
        newPeoples = [],
        repentances = [],
        donations = [],
        tithe = [],
        pastorTithe = [],
        percent = [];

        (isGroup === '1m') ?
        labels = data.map(item => `${item.date.week} нед. ${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`)
        :
        labels = data.map(item => `${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);

    labels.map((item, index) => {
        let elem = data[index].result;
        allPeoples.push(_.reduce(elem, (sum, val, key) => sum + val.count_people, 0));
        newPeoples.push(_.reduce(elem, (sum, val, key) => sum + val.count_new_people, 0));
        repentances.push(_.reduce(elem, (sum, val, key) => sum + val.count_repentance, 0));
        donations.push(_.reduce(elem, (sum, val, key) => {
                if (curType === key) {
                    return (+sum + +val.donations).toFixed(2);
                } else if (curType === 'all') {
                    return (+sum + +val.donations).toFixed(2);
                } else {
                    return sum;
                }
            }, 0));
        tithe.push(_.reduce(elem, (sum, val, key) => {
                if (curType === key) {
                    return (+sum + +val.tithe).toFixed(2);
                } else if (curType === 'all') {
                    return (+sum + +val.tithe).toFixed(2);
                } else {
                    return sum;
                }
            }, 0));
        pastorTithe.push(_.reduce(elem, (sum, val, key) => {
                if (curType === key) {
                    return (+sum + +val.pastor_tithe).toFixed(2);
                } else if (curType === 'all') {
                    return (+sum + +val.pastor_tithe).toFixed(2);
                } else {
                    return sum;
                }
            }, 0));
        percent.push(_.reduce(elem, (sum, val, key) => {
                if (curType === key) {
                    return (+sum + +val.transfer_payments).toFixed(2);
                } else if (curType === 'all') {
                    return (+sum + +val.transfer_payments).toFixed(2);
                } else {
                    return sum;
                }
            }, 0));
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
            label: "Десятины пастора",
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
                let sumDon = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                    sumTithe = data.datasets[tooltipItems[2].datasetIndex].data[tooltipItems[2].index],
                    totalSum = (+sumDon + +sumTithe).toFixed(2);
                return `Общая сумма: ${beautifyNumber(totalSum)}`;
            },
        },
        configFinChart = setMixedConfig(datasetsFinChart, titleFinChart, callbackFinChart),
        configFinPastorTithe = setConfig('line', labels, datasetsFinPastorTitheChart, titleFinPastorTitheChart, xAxes, yAxes),
        configPeoplesChart = setConfig('line', labels, datasetsPeoplesChart, titlePeoplesChart, xAxes, yAxes),
        optionFinChart = {
            chart: window.ChartFin,
            labels: labels,
            l1: percent,
            l2: donations,
            l3: tithe,
        },
        optionFinPastorTithe = {
            chart: window.ChartFinPastor,
            labels: labels,
            line1: pastorTithe,
        },
        optionPeoplesChart = {
            chart: window.ChartPeoples,
            labels: labels,
            l1: allPeoples,
            l2: newPeoples,
            l3: repentances,
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

function updateChart({chart, labels, l1, l2, l3 }) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = l1;
    chart.data.datasets[1].data = l2;
    chart.data.datasets[2].data = l3;
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