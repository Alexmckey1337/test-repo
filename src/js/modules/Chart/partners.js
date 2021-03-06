'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import {CHARTCOLORS, setConfig, setMixedConfig} from "./config";

export function initCharts(data, update) {
    let {
        configFinancesChart,
        configPartnersChart,
        optionFinancesChart,
        optionPartnersChart,
        selectFinancesChart,
        selectPartnersChart
    } = makeChartConfig(data);
    if (update) {
        updateFinancesChart(optionFinancesChart);
        updatePartnersChart(optionPartnersChart);
    } else {
        renderChart(selectFinancesChart, configFinancesChart);
        renderChart(selectPartnersChart, configPartnersChart);
    }
}

function makeChartConfig(data) {
    let labels = Object.keys(data).sort(),
        plan = [],
        percent = [],
        sum = [],
        sumPartner = [],
        sumTithe = [],
        sumDeals = [],
        potential = [],
        allPartner = [],
        activePartner = [],
        inertPartner = [];
    labels.map(item => {
        let elem = data[item],
            perc = (100 / (elem.plans / elem.payments)).toFixed(1);
        plan.push(elem.plans);
        percent.push(isFinite(perc) ? perc : 0);
        sum.push(elem.payments);
        sumPartner.push(elem.payments_t1);
        sumTithe.push(elem.payments_t2);
        sumDeals.push(elem.deals);
        potential.push(elem.potential);
        allPartner.push(elem.partners_count);
        activePartner.push(elem.active_partners_count);
        inertPartner.push(elem.partners_count - elem.active_partners_count);
    });
    let dataFinancesChart = {
            labels: labels,
            datasets: [{
                type: 'line',
                label: 'План',
                borderColor: CHARTCOLORS.red,
                backgroundColor: CHARTCOLORS.red,
                borderWidth: 2,
                yAxisID: "y-axis-0",
                lineTension: 0,
                data: plan,
                fill: false,
            },
                {
                    label: 'Сумма партнерских',
                    backgroundColor: CHARTCOLORS.green,
                    yAxisID: "y-axis-0",
                    data: sumPartner
                }, {
                    label: 'Сумма десятин',
                    backgroundColor: CHARTCOLORS.yellow,
                    yAxisID: "y-axis-0",
                    data: sumTithe
                }]
        },
        datasetsPartnersChart = [{
            label: "Активных",
            borderColor: CHARTCOLORS.green,
            backgroundColor: CHARTCOLORS.green,
            data: activePartner,
        }, {
            label: "Неактивных",
            borderColor: CHARTCOLORS.red,
            backgroundColor: CHARTCOLORS.red,
            data: inertPartner,
        }],
        titleFinancesChart = "Статистика по финансам",
        titlePartnersChart = "Статистика по партнёрам",
        xAxesBar = [{
            stacked: true,
        }],
        yAxesBar = [{
            stacked: true,
        }],
        callbackFinancesChart = {
            footer: (tooltipItems, data) => {
                let sumParthner = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                    sumTithe = data.datasets[tooltipItems[2].datasetIndex].data[tooltipItems[2].index],
                    totalSum = sumParthner + sumTithe;
                return `Общая сумма: ${totalSum}`;
            },
        },
        callbackPartnersChart = {
            footer: (tooltipItems, data) => {
                let inert = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
                    active = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                    all = active + inert;
                return `Всего партнёров: ${all}`;
            },
        },
        configFinancesChart = setMixedConfig(dataFinancesChart, titleFinancesChart, callbackFinancesChart),
        configPartnersChart = setConfig('bar', labels, datasetsPartnersChart, titlePartnersChart, xAxesBar, yAxesBar, callbackPartnersChart),
        optionFinancesChart = {
            chart: window.ChartFinances,
            labels: labels,
            line1: plan,
            line2: sumPartner,
            line3: sumTithe,
        },
        optionPartnersChart = {
            chart: window.ChartPartners,
            labels: labels,
            line1: activePartner,
            line2: inertPartner,
        },
        selectFinancesChart = 'chart_finances',
        selectPartnersChart = 'chart_partners';

    return {
        configFinancesChart,
        configPartnersChart,
        optionFinancesChart,
        optionPartnersChart,
        selectFinancesChart,
        selectPartnersChart
    }
}

function updateFinancesChart({chart, labels, line1, line2, line3}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.data.datasets[2].data = line3;
    chart.update();
}

function updatePartnersChart({chart, labels, line1, line2}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.update();
}

function renderChart(select, config) {
    let ctx = document.getElementById(select).getContext("2d");
    if (select == 'chart_finances') {
        window.ChartFinances = new Chart(ctx, config);
    } else if (select == 'chart_percent') {
        window.ChartPercent = new Chart(ctx, config);
    } else {
        window.ChartPartners = new Chart(ctx, config);
    }
}