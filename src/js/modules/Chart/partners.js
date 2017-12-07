'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import URLS from '../Urls/index';
import getData from '../Ajax';
import {CHARTCOLORS, setConfig} from "./config";

export function initCharts(ID, config = {}, update = false) {
    let url = URLS.partner.manager_summary(ID);
    getData(url, config).then(data => {
        let {
            optionFinancesChart,
            optionPartnersChart,
            selectFinancesChart,
            selectPartnersChart,
            configFinancesChart,
            configPartnersChart
        } = makeChartConfig(data);
        (update) ?
            updateFinancesChart(optionFinancesChart)
            :
            renderChart(selectFinancesChart, configFinancesChart);
        (update) ?
            updatePartnersChart(optionPartnersChart)
            :
            renderChart(selectPartnersChart, configPartnersChart);
        $('.preloader').css('display', 'none');
    });
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
        activePartner = [];
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
    });
    let datasetsFinancesChart = [{
            label: "План",
            borderColor: CHARTCOLORS.blue,
            backgroundColor: CHARTCOLORS.blue,
            data: plan,
            fill: false,
        }, {
            label: "Общая сумма платежей",
            borderColor: CHARTCOLORS.green,
            backgroundColor: CHARTCOLORS.green,
            data: sum,
            fill: false,
        }, {
            label: "Сумма сделок",
            borderColor: CHARTCOLORS.yellow,
            backgroundColor: CHARTCOLORS.yellow,
            data: sumDeals,
            fill: false,
        }],
        datasetsPartnersChart = [{
            label: "Всего",
            borderColor: CHARTCOLORS.blue,
            backgroundColor: CHARTCOLORS.blue,
            data: allPartner,
            fill: false,
        }, {
            label: "Активных",
            borderColor: CHARTCOLORS.green,
            backgroundColor: CHARTCOLORS.green,
            data: activePartner,
            fill: false,
        }],
        titleFinancesChart = "Статистика по финансам",
        titlePartnersChart = "Статистика по партнёрам",
        xAxes = [{
            display: true,
            scaleLabel: {
                show: true,
                labelString: 'Month'
            }
        }],
        yAxes = [{
            display: true,
            scaleLabel: {
                show: true,
                labelString: 'Value'
            },
        }],
        callbackPartnersChart = {
            footer: (tooltipItems, data) => {
                let all = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
                    active = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                    diff = all - active;
                return `Неактивных: ${diff}`;
            },
        },
        configFinancesChart = setConfig('line', labels, datasetsFinancesChart, titleFinancesChart, xAxes, yAxes),
        configPartnersChart = setConfig('line', labels, datasetsPartnersChart, titlePartnersChart, xAxes, yAxes, callbackPartnersChart),
        optionFinancesChart = {
            chart: window.ChartFinances,
            labels: labels,
            line1: plan,
            line2: sum,
            line3: sumDeals,
        },
        optionPartnersChart = {
            chart: window.ChartPartners,
            labels: labels,
            line1: allPartner,
            line2: activePartner,
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
    } else {
        window.ChartPartners = new Chart(ctx, config);
    }
}