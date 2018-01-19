'use strict';
import URLS from '../Urls/index';
import getData from "../Ajax/index";
import beautifyNumber from '../beautifyNumber';
import updateHistoryUrl from '../History/index';
import {initCharts} from '../Chart/church_stats';

export function churchStatistics(update = false) {
    let config = Object.assign({}, getPreFilterParam());
    updateHistoryUrl(config);
    (config.last != '1m') && (config.group_by = 'month');
    getData(URLS.event.church_report.statistics(), config).then(data => {
        $('.preloader').css('display', 'none');
        makeStatsTable(data, config.last);
        initCharts(data, update, config.last);
    })
}

export function makeStatsTable(data, isGroup) {
    let formatedData = getTransformData(data, isGroup),
        tableFinances = createFinanceTable(formatedData.headers, formatedData.dataFinances),
        tablePeoples = createPeoplesTable(formatedData.headers, formatedData.dataPeoples);
    $('#tableChRepUserStats').html('').append(tableFinances);
    $('#tableChRepFinStats').html('').append(tablePeoples);
}

function getTransformData(data, isGroup) {
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
        dataFinances[0][item] = _.reduce(elem, (result, value, key) => {
                result[key] = value.donations;
                return result;
            }, {});
        dataFinances[1][item] = _.reduce(elem, (result, value, key) => {
                result[key] = value.tithe;
                return result;
            }, {});
        dataFinances[2][item] = _.reduce(elem, (result, value, key) => {
                result[key] = value.pastor_tithe;
                return result;
            }, {});
        dataFinances[3][item] = _.reduce(elem, (result, value, key) => {
                result[key] = value.transfer_payments;
                return result;
            }, {});
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
                                <th colspan="4">${item}</th>
                            `    
                        }).join('')}
                    </tr>
                    <tr>
                        <th></th>
                        ${headers.map(_ => {
                            return `<th>грн</th>
                                    <th>руб</th>
                                    <th>дол</th>
                                    <th>евро</th>`    
                        }).join('')}
                    </tr>
                    </thead>
                    <tbody>
                        ${body.map(item => {
                            return `<tr>
                                    <td>${item.title}</td>
                                    ${headers.map(el => {
                                        return `
                                            <td>${beautifyNumber(item[el].uah)}</td>
                                            <td>${beautifyNumber(item[el].rur)}</td>
                                            <td>${beautifyNumber(item[el].usd)}</td>
                                            <td>${beautifyNumber(item[el].eur)}</td>
                                          
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
        data = {};
    $filterFields.each(function () {
        if ($(this).val() === "ВСЕ") return;
        let prop = $(this).attr('data-filter');
        $(this).val() && (data[prop] = $(this).val());
    });
    data.last = $('.tab-home-stats').find('.range.active').attr('data-range');

    return data;
}