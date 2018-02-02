'use strict';
import URLS from '../Urls/index';
import getData from "../Ajax/index";
import beautifyNumber from '../beautifyNumber';
import updateHistoryUrl from '../History/index';
import {initCharts} from '../Chart/church_stats';

export function churchStatistics(update = false) {
    let config = Object.assign({}, getPreFilterParam()),
        curType = $('#tab_currency').find('button.active').attr('data-curr');
    updateHistoryUrl(config);
    (config.last) && (config.group_by = 'month');
    getData(URLS.event.church_report.statistics(), config).then(data => {
        $('.preloader').css('display', 'none');
        makeStatsTable(data, config.last, curType);
        initCharts(data, update, config.last, curType);
    })
}

export function makeStatsTable(data, isGroup, curType) {
    let formatedData = getTransformData(data, isGroup, curType),
        tableFinances = createFinanceTable(formatedData.headers, formatedData.dataFinances),
        tablePeoples = createPeoplesTable(formatedData.headers, formatedData.dataPeoples);
    $('#tableChRepUserStats').html('').append(tableFinances);
    $('#tableChRepFinStats').html('').append(tablePeoples);
}

function getTransformData(data, isGroup, curType = 'all') {
    let dataFinances = [
            {
                title: 'Пожертвования',
            },
            {
                title: 'Десятины',
            },
            {
                title: 'Десятина пастора',
            },
            {
                title: '15% к перечислению',
            },
        ],
        dataPeoples = [
            {
                title: 'Всего людей',
            },
            {
                title: 'Количество новых людей',
            },
            {
                title: 'Количество покаяний',
            },
        ],
        headers;

    if (isGroup === '1m') {
        headers = data.map(item => `${item.date.week} нед. ${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);
    } else {
        headers = data.map(item => `${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);
    }

    headers.map((item, index) => {
        let elem = data[index].result;
        dataFinances[0][item] = _.reduce(elem, (sum, val, key) => {
            if (curType === 'uah' && key === 'uah') {
                return sum + val.donations;
            } else if (curType === 'rur' && key === 'rur') {
                return sum + val.donations;
            } else if (curType === 'usd' && key === 'usd') {
                return sum + val.donations;
            } else if (curType === 'eur' && key == 'eur') {
                return sum + val.donations;
            } else if (curType === 'all') {
                return sum + val.donations;
            } else {
                return sum;
            }
        }, 0);
        dataFinances[1][item] = _.reduce(elem, (sum, val, key) => {
            if (curType === 'uah' && key === 'uah') {
                return sum + val.tithe;
            } else if (curType === 'rur' && key === 'rur') {
                return sum + val.tithe;
            } else if (curType === 'usd' && key === 'usd') {
                return sum + val.tithe;
            } else if (curType === 'eur' && key === 'eur') {
                return sum + val.tithe;
            } else if (curType === 'all') {
                return sum + val.tithe;
            } else {
                return sum;
            }
        }, 0);
        dataFinances[2][item] = _.reduce(elem, (sum, val, key) => {
            if (curType === 'uah' && key === 'uah') {
                return sum + val.pastor_tithe;
            } else if (curType === 'rur' && key === 'rur') {
                return sum + val.pastor_tithe;
            } else if (curType === 'usd' && key === 'usd') {
                return sum + val.pastor_tithe;
            } else if (curType === 'eur' && key === 'eur') {
                return sum + val.pastor_tithe;
            } else if (curType === 'all') {
                return sum + val.pastor_tithe;
            } else {
                return sum;
            }
        }, 0);
        dataFinances[3][item] = _.reduce(elem, (sum, val, key) => {
            if (curType === 'uah' && key === 'uah') {
                return sum + val.transfer_payments;
            } else if (curType === 'rur' && key === 'rur') {
                return sum + val.transfer_payments;
            } else if (curType === 'usd' && key === 'usd') {
                return sum + val.transfer_payments;
            } else if (curType === 'eur' && key === 'eur') {
                return sum + val.transfer_payments;
            } else if (curType === 'all') {
                return +sum.toFixed(1) + +val.transfer_payments;
            } else {
                return +sum.toFixed(1);
            }
        }, 0);
        dataPeoples[0][item] = _.reduce(elem, (sum, val, key) => sum + val.count_people, 0);
        dataPeoples[1][item] = _.reduce(elem, (sum, val, key) => sum + val.count_new_people, 0);
        dataPeoples[2][item] = _.reduce(elem, (sum, val, key) => sum + val.count_repentance, 0);
    });
    return {
        headers,
        dataFinances,
        dataPeoples
    }
}

function createFinanceTable(headers, body) {
            let table = `
                <table>
                    <thead>
                    <tr>
                        <th>Финансы</th>
                        ${headers.map(item => {
                            return `
                                <th>${item}</th>
                            `    
                        }).join('')}
                    </tr>
                    </thead>
                    <tbody>
                        ${body.map(item => {
                            return `<tr>
                                    <td>${item.title}</td>
                                    ${headers.map(el => {
                                        return `
                                            <td>${beautifyNumber(item[el])}</td>
                                        `
                                    }).join('')}
                                </tr>`;
                        }).join('')}
                    </tbody>
                </table>`;

    return table;
}

function createPeoplesTable(headers, body) {
    let table = `
                <table>
                    <thead>
                    <tr>
                        <th>Люди</th>
                        ${headers.map(item => {
                            return `
                                <th>${item}</th>
                            `    
                        }).join('')}
                    </tr>
                    </thead>
                    <tbody>
                        ${body.map(item => {
                            return `<tr>
                                    <td>${item.title}</td>
                                    ${headers.map(el => {
                                        return `
                                            <td>${beautifyNumber(item[el])}</td>
                                        `
                            }).join('')}
                                </tr>`;
                        }).join('')}
                    </tbody>
                </table>`;

    return table;
}

function getPreFilterParam() {
    let $filterFields = $('.prefilter_select').find('select'),
        rangeActive = $('.tab-home-stats').find('.range.active'),
        data = {};
    $filterFields.each(function () {
        if ($(this).val() === "ВСЕ") return;
        let prop = $(this).attr('data-filter');
        $(this).val() && (data[prop] = $(this).val());
    });

    rangeActive.length ?
        (data.last = rangeActive.attr('data-range'))
        :
        (data.interval = $('#calendar_range').attr('data-interval'));

    return data;
}