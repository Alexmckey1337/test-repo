'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import URLS from '../Urls/index';
import getData from '../Ajax';
import {CHARTCOLORS, setConfig} from "./config";

export function initCharts(ID, config = {}, update = false) {
    let url = URLS.partner.manager_summary(ID);
    getData(url, config).then(data => {
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
        let datasets = [{
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
            datasets2 = [{
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
            title = "Статистика по финансам",
            title2 = "Статистика по партнёрам",
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
            callback2 = {
                footer: (tooltipItems, data) => {
                    let all = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
                        active = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
                        diff = all - active;
                    return `Неактивных: ${diff}`;
                },
            },
            config = setConfig('line', labels, datasets, title, xAxes, yAxes),
            config2 = setConfig('line', labels, datasets2, title2, xAxes, yAxes, callback2),
            option = {
                chart: window.ChartFinances,
                labels: labels,
                line1: plan,
                line2: sum,
                line3: sumDeals,
            },
            option2 = {
                chart: window.ChartPartners,
                labels: labels,
                line1: allPartner,
                line2: activePartner,
            },
            select = 'chart_finances',
            select2 = 'chart_partners';
        (update) ? updateChart(option) : renderChart(select, config);
        (update) ? updateChart2(option2) : renderChart(select2, config2);
        $('.preloader').css('display', 'none');
    });
}

function updateChart({chart, labels, line1, line2, line3}) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = line1;
    chart.data.datasets[1].data = line2;
    chart.data.datasets[2].data = line3;
    chart.update();
}

function updateChart2({chart, labels, line1, line2}) {
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