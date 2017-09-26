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