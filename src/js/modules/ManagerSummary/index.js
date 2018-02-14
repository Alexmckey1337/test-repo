'use strict';
import URLS from '../Urls';
import getData from '../Ajax';
import beautifyNumber from '../beautifyNumber';
import {convertNum} from "../ConvertNum/index";
import {initCharts} from "../Chart/partners";

export function renderStats(ID, config = {}, update = false) {
    getData(URLS.partner.manager_summary(ID), config).then(data => {
        $('.preloader').css('display', 'none');
        makeManagerTable(data);
        initCharts(data, update);
    });
}

export function makeManagerTable(data) {
    let formatedData = getTransformData(data),
        tableFinances = createFinanceTable(formatedData.headers, formatedData.dataFinances),
        tablePartners = createPartnerTable(formatedData.headers, formatedData.dataPartners);
    $('#managersFinances').html('').append(tableFinances);
    $('#managersPartners').html('').append(tablePartners);
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
                                            <td>${beautifyNumber(convertNum(item[el], ','))}</td>
                                        `
                            }).join('')}
                                </tr>`;
                        }).join('')}
                    </tbody>
                </table>`;

    return table;
}

function createPartnerTable(headers, body) {
    let table = `
                <table>
                    <thead>
                    <tr>
                        <th>Партнеры</th>
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

function getTransformData(data) {
    let dataFinances = [
            {
                title: 'План',
            },
            {
                title: '% выполнения плана',
            },
            {
                title: 'Общая сумма',
            },
            {
                title: 'Сумма партнерских',
            },
            {
                title: 'Сумма десятин',
            },
            {
                title: 'Потенциал',
            },
            {
                title: 'Сумма сделок',
            },
        ],
        dataPartners = [
            {
                title: 'Активных',
            },
            {
                title: 'Неактивных',
            },
            {
                title: 'Всего партнеров',
            },
        ],
        headers = Object.keys(data).sort();
    headers.map(item => {
        let elem = data[item],
            percent = (100 / (elem.plans / elem.payments)).toFixed(1);
        dataFinances[0][item] = elem.plans;
        dataFinances[1][item] = isFinite(percent) ? percent : 0;
        dataFinances[2][item] = elem.payments;
        dataFinances[3][item] = elem.payments_t1;
        dataFinances[4][item] = elem.payments_t2;
        dataFinances[5][item] = elem.potential;
        dataFinances[6][item] = elem.deals;
        dataPartners[0][item] = elem.active_partners_count;
        dataPartners[1][item] = (+elem.partners_count - +elem.active_partners_count);
        dataPartners[2][item] = elem.partners_count;
    });

    return {
        headers,
        dataFinances,
        dataPartners
    }

}
