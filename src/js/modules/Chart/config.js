'use strict';
import 'chart.js/dist/Chart.bundle.min.js';

export function regLegendPlagin() {
    // Register the legend plugin
    Chart.plugins.register({
        beforeInit: function (chartInstance) {
            let legendOpts = chartInstance.options.legend;

            if (legendOpts) {
                createNewLegendAndAttach(chartInstance, legendOpts);
            }
        },
        beforeUpdate: function (chartInstance) {
            let legendOpts = chartInstance.options.legend;

            if (legendOpts) {
                legendOpts = Chart.helpers.configMerge(Chart.defaults.global.legend, legendOpts);

                if (chartInstance.newLegend) {
                    chartInstance.newLegend.options = legendOpts;
                } else {
                    createNewLegendAndAttach(chartInstance, legendOpts);
                }
            } else {
                Chart.layoutService.removeBox(chartInstance, chartInstance.newLegend);
                delete chartInstance.newLegend;
            }
        },
        afterEvent: function (chartInstance, e) {
            let legend = chartInstance.newLegend;
            if (legend) {
                legend.handleEvent(e);
            }
        }
    });

    Chart.NewLegend = Chart.Legend.extend({
        afterFit: function () {
            this.height = this.height + 30;
        },
    });
}

function createNewLegendAndAttach(chartInstance, legendOpts) {
    let legend = new Chart.NewLegend({
        ctx: chartInstance.chart.ctx,
        options: legendOpts,
        chart: chartInstance
    });

    if (chartInstance.legend) {
        Chart.layoutService.removeBox(chartInstance, chartInstance.legend);
        delete chartInstance.newLegend;
    }

    chartInstance.newLegend = legend;
    Chart.layoutService.addBox(chartInstance, legend);
}

export const CHARTCOLORS = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(60, 174, 218)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};

export function getRandomColor() {
    let letters = '0123456789ABCDEF',
        color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

export function setConfig(type = 'line', labels = [], datasets = [], title = '', xAxes = [], yAxes = [], callback = {}) {
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
                },
                rectangle: {
                    borderWidth: 1000
                }

            }
        },
        plugins: PLUGINS
    };

    return config;
}

export const PLUGINS = [{
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