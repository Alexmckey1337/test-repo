'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import {CHARTCOLORS, setConfig, setMixedConfig} from "./config";
import beautifyNumber from '../beautifyNumber';

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
        updatePeoplesChart(optionPeoplesChart);
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
        donationsUAH = [],
        donationsRUB = [],
        donationsUSD = [],
        donationsEUR = [],
        titheUAH = [],
        titheRUB = [],
        titheUSD = [],
        titheEUR = [],
        pastorTitheUAH = [],
        pastorTitheRUB = [],
        pastorTitheUSD = [],
        pastorTitheEUR = [];

        (isGroup === '1m') ?
        labels = data.map(item => `${item.date.week} нед. ${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`)
        :
        labels = data.map(item => `${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);


    labels.map((item, index) => {
        let elem = data[index].result;
        allPeoples.push(_.reduce(elem, (sum, val, key) => sum + val.count_people, 0));
        newPeoples.push(_.reduce(elem, (sum, val, key) => sum + val.count_new_people, 0));
        repentances.push(_.reduce(elem, (sum, val, key) => sum + val.count_repentance, 0));
        donationsUAH.push(elem.uah.donations);
        donationsRUB.push(elem.rur.donations);
        donationsUSD.push(elem.usd.donations);
        donationsEUR.push(elem.eur.donations);
        titheUAH.push(elem.uah.tithe);
        titheRUB.push(elem.rur.tithe);
        titheUSD.push(elem.usd.tithe);
        titheEUR.push(elem.eur.tithe);
        pastorTitheUAH.push(elem.uah.pastor_tithe);
        pastorTitheRUB.push(elem.rur.pastor_tithe);
        pastorTitheUSD.push(elem.usd.pastor_tithe);
        pastorTitheEUR.push(elem.eur.pastor_tithe);
    });
    let datasetsFinChart = {
            labels: labels,
            datasets: [
                {
                    label: 'Пожертвования (грн)',
                    backgroundColor: CHARTCOLORS.yellow,
                    stack: 'Stack 0',
                    data: donationsUAH
                }, {
                    label: 'Десятины (грн)',
                    backgroundColor: CHARTCOLORS.blue,
                    stack: 'Stack 0',
                    data: titheUAH
                },
                                {
                    label: 'Пожертвования (руб)',
                    backgroundColor: CHARTCOLORS.red,
                    stack: 'Stack 1',
                    data: donationsRUB
                }, {
                    label: 'Десятины (руб)',
                    backgroundColor: CHARTCOLORS.green,
                    stack: 'Stack 1',
                    data: titheRUB
                },
                                {
                    label: 'Пожертвования (дол)',
                    backgroundColor: CHARTCOLORS.grey,
                    stack: 'Stack 2',
                    data: donationsUSD
                }, {
                    label: 'Десятины (дол)',
                    backgroundColor: CHARTCOLORS.orange,
                    stack: 'Stack 2',
                    data: titheUSD
                },
                                {
                    label: 'Пожертвования (евро)',
                    backgroundColor: CHARTCOLORS.purple,
                    stack: 'Stack 3',
                    data: donationsEUR
                }, {
                    label: 'Десятины (евро)',
                    backgroundColor: CHARTCOLORS.salmon,
                    stack: 'Stack 3',
                    data: titheEUR
                }
                ]
        },
        datasetsFinPastorTitheChart = [{
            label: "грн",
            borderColor: CHARTCOLORS.green,
            backgroundColor: CHARTCOLORS.green,
            data: pastorTitheUAH,
        },
        {
            label: "руб",
            borderColor: CHARTCOLORS.purple,
            backgroundColor: CHARTCOLORS.purple,
            data: pastorTitheRUB,
        },
        {
            label: "дол",
            borderColor: CHARTCOLORS.yellow,
            backgroundColor: CHARTCOLORS.yellow,
            data: pastorTitheUSD,
        },
        {
            label: "евро",
            borderColor: CHARTCOLORS.red,
            backgroundColor: CHARTCOLORS.red,
            data: pastorTitheEUR,
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
                let sumDonUAH = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
                    sumTitheUAH = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                    sumDonRUB = data.datasets[tooltipItems[2].datasetIndex].data[tooltipItems[2].index],
                    sumTitheRUB = data.datasets[tooltipItems[3].datasetIndex].data[tooltipItems[3].index],
                    sumDonUSD = data.datasets[tooltipItems[4].datasetIndex].data[tooltipItems[4].index],
                    sumTitheUSD = data.datasets[tooltipItems[5].datasetIndex].data[tooltipItems[5].index],
                    sumDonEUR = data.datasets[tooltipItems[6].datasetIndex].data[tooltipItems[6].index],
                    sumTitheEUR = data.datasets[tooltipItems[7].datasetIndex].data[tooltipItems[7].index],
                    totalSumUAH = sumDonUAH + sumTitheUAH,
                    totalSumRUB = sumDonRUB + sumTitheRUB,
                    totalSumUSD = sumDonUSD + sumTitheUSD,
                    totalSumEUR = sumDonEUR + sumTitheEUR;
                return `Общая сумма: грн-> ${beautifyNumber(totalSumUAH)}, руб-> ${beautifyNumber(totalSumRUB)}, дол-> ${beautifyNumber(totalSumUSD)}, евро-> ${beautifyNumber(totalSumEUR)}`;
            },
        },
        configFinChart = setMixedConfig(datasetsFinChart, titleFinChart, callbackFinChart),
        configFinPastorTithe = setConfig('bar', labels, datasetsFinPastorTitheChart, titleFinPastorTitheChart),
        configPeoplesChart = setConfig('line', labels, datasetsPeoplesChart, titlePeoplesChart, xAxes, yAxes),
        optionFinChart = {
            chart: window.ChartFin,
            labels: labels,
            l1: donationsUAH,
            l2: titheUAH,
            l3: donationsRUB,
            l4: titheRUB,
            l5: donationsUSD,
            l6: titheUSD,
            l7: donationsEUR,
            l8: titheEUR,
        },
        optionFinPastorTithe = {
            chart: window.ChartFinPastor,
            labels: labels,
            line1: pastorTitheUAH,
            line2: pastorTitheRUB,
            line3: pastorTitheUSD,
            line4: pastorTitheEUR,
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

function updateFinChart({chart, labels, l1, l2, l3, l4, l5, l6, l7, l8 }) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = l1;
    chart.data.datasets[1].data = l2;
    chart.data.datasets[2].data = l3;
    chart.data.datasets[3].data = l4;
    chart.data.datasets[4].data = l5;
    chart.data.datasets[5].data = l6;
    chart.data.datasets[6].data = l7;
    chart.data.datasets[7].data = l8;
    chart.update();
}

function updateFinPastorTithe({chart, labels, line1, line2, line3, line4}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.data.datasets[2].data = line3;
    chart.data.datasets[3].data = line4;
    chart.update();
}

function updatePeoplesChart({chart, labels, line1, line2, line3}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.data.datasets[2].data = line3;
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