'use strict';

export default class OrderTable {
    constructor() {
        this.savePath = sessionStorage.getItem('path');
        this.path = window.location.pathname;
        if (this.savePath != this.path) {
            sessionStorage.setItem('path', this.path);
            sessionStorage.setItem('revers', '');
            sessionStorage.setItem('order', '');
        }
    }

    get sort() {
        return this._addListener;
    }

    _addListener(callback, selector) {
        $(selector).on('click', function () {
            let dataOrder = void 0;
            const data_order = this.getAttribute('data-order');
            if (data_order == "no_ordering") {
                return;
            }
            let page = $('.pagination__input').val();
            let revers = sessionStorage.getItem('revers') ? sessionStorage.getItem('revers') : "+";
            let order = sessionStorage.getItem('order') ? sessionStorage.getItem('order') : '';
            if (order != '') {
                dataOrder = order == data_order && revers == "+" ? '-' + data_order : data_order;
            } else {
                dataOrder = '-' + data_order;
            }
            const data = {
                'ordering': dataOrder,
                'page': page
            };
            if (order == data_order) {
                revers = revers == '+' ? '-' : '+';
            } else {
                revers = "+";
            }
            sessionStorage.setItem('revers', revers);
            sessionStorage.setItem('order', data_order);
            $('.preloader').css('display', 'block');
            callback(data);
        });
    }
}

export function getOrderingData() {
    let revers, order, savePath;
    let path = window.location.pathname;
    revers = window.sessionStorage.getItem('revers');
    order = window.sessionStorage.getItem('order');
    savePath = window.sessionStorage.getItem('path');
    if (savePath != path) {
        return
    }
    if (revers && order) {
        revers = (revers == "+") ? "" : revers;
        return {
            ordering: revers + order
        }
    }
}

export class OrderTableByClient extends OrderTable {
    constructor() {
        super();
    }

    get sortByClient() {
        return this._addListenerByClient;
    }

    get searchByClient() {
        return this._addSearchListenerByClient;
    }

    get searchCompareByClient() {
        return this._addSearchCompareListenerByClient;
    }

    _addListenerByClient(callback, selector, data) {
        $(selector).on('click', function () {
            let dataOrder = this.getAttribute('data-order'),
                type = this.getAttribute('data-order_type') || null,
                revers = sessionStorage.getItem('revers') ? sessionStorage.getItem('revers') : "+",
                order = sessionStorage.getItem('order') ? sessionStorage.getItem('order') : '',
                newArr;
            if (dataOrder != null) {
                revers = (revers == '+') ? '-' : '+';
                sessionStorage.setItem('revers', revers);
                sessionStorage.setItem('order', dataOrder);
                let pureArr = _.slice(data.results, 0, data.results.length - 1);
                let summary = _.last(data.results);
                if (type == 'letter') {
                    newArr = _.sortBy(pureArr, (e) => e[`${dataOrder}`]);
                } else {
                    newArr = _.sortBy(pureArr, (e) => parseFloat(e[`${dataOrder}`]));
                }
                (revers == "+") && newArr.reverse();
                newArr.push(summary);
                $('.preloader').css('display', 'block');
                let sortedData = {
                    table_columns: data.table_columns,
                    results: newArr,
                };
                (data.flag) ? sortedData.flag = true : sortedData.flag = false;
                callback(sortedData);
            }
        });
    }

    _addSearchListenerByClient(callback, data, oldData) {
        $('input[name="fullsearch"]').unbind('keyup');
        let actualData;
        if ($.isEmptyObject(oldData)) {
            actualData = data;
        } else {
            actualData = oldData;
        }
        $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
            $('.preloader').css('display', 'block');
            let search = $(this).val();
            if (search !== '') {
                let pureArr = _.slice(actualData.results, 0, actualData.results.length - 1),
                    newArr = _.filter(pureArr, (e) => {
                        return e.manager.toUpperCase().indexOf(search.toUpperCase()) !== -1;
                    }),
                    allPlans = newArr.reduce((sum, current) => sum + current.plan, 0),
                    allSum = newArr.reduce((sum, current) => sum + current.total_sum, 0),
                    newRow = {
                        manager: 'СУММАРНО:',
                        plan: allPlans,
                        potential_sum: newArr.reduce((sum, current) => sum + current.potential_sum, 0),
                        sum_deals: newArr.reduce((sum, current) => sum + current.sum_deals, 0),
                        sum_pay: newArr.reduce((sum, current) => sum + current.sum_pay, 0),
                        sum_pay_tithe: newArr.reduce((sum, current) => sum + current.sum_pay_tithe, 0),
                        sum_pay_church: newArr.reduce((sum, current) => sum + current.sum_pay_church, 0),
                        total_sum: allSum,
                        percent_of_plan: (100 / (allPlans / allSum)).toFixed(1),
                        total_partners: newArr.reduce((sum, current) => sum + current.total_partners, 0),
                        active_partners: newArr.reduce((sum, current) => sum + current.active_partners, 0),
                        not_active_partners: newArr.reduce((sum, current) => sum + current.not_active_partners, 0),
                    };
                newArr.push(newRow);
                let sortedData = {
                    table_columns: actualData.table_columns,
                    results: newArr,
                };
                (actualData.flag) ? sortedData.flag = true : sortedData.flag = false;
                callback(sortedData, actualData);
            } else {
                callback(actualData, actualData);
            }
        }, 500));
    }

    _addSearchCompareListenerByClient(callback, data, oldData) {
        $('input[name="fullsearch"]').unbind('keyup');
        let actualData;
        if ($.isEmptyObject(oldData)) {
            actualData = data;
        } else {
            actualData = oldData;
        }
        $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
            $('.preloader').css('display', 'block');
                        let search = $(this).val();
            if (search !== '') {
                let pureArr = _.slice(actualData.result, 0, actualData.result.length - 1),
                    pureArrCompare = _.slice(actualData.resultCompare, 0, actualData.resultCompare.length - 1),
                    newArr = _.filter(pureArr, (e) => {
                        return e.manager.toUpperCase().indexOf(search.toUpperCase()) !== -1;
                    }),
                    newArrCompare = _.filter(pureArrCompare, (e) => {
                        return e.manager.toUpperCase().indexOf(search.toUpperCase()) !== -1;
                    }),
                    allPlans = newArr.reduce((sum, current) => sum + current.plan, 0),
                    allSum = newArr.reduce((sum, current) => sum + current.total_sum, 0),
                    newRow = {
                        manager: 'СУММАРНО:',
                        plan: allPlans,
                        potential_sum: newArr.reduce((sum, current) => sum + current.potential_sum, 0),
                        sum_deals: newArr.reduce((sum, current) => sum + current.sum_deals, 0),
                        sum_pay: newArr.reduce((sum, current) => sum + current.sum_pay, 0),
                        sum_pay_tithe: newArr.reduce((sum, current) => sum + current.sum_pay_tithe, 0),
                        sum_pay_church: newArr.reduce((sum, current) => sum + current.sum_pay_church, 0),
                        total_sum: allSum,
                        percent_of_plan: (100 / (allPlans / allSum)).toFixed(1),
                        total_partners: newArr.reduce((sum, current) => sum + current.total_partners, 0),
                        active_partners: newArr.reduce((sum, current) => sum + current.active_partners, 0),
                        not_active_partners: newArr.reduce((sum, current) => sum + current.not_active_partners, 0),
                    },
                    allPlansCompare = newArrCompare.reduce((sum, current) => sum + current.plan, 0),
                    allSumCompare = newArrCompare.reduce((sum, current) => sum + current.total_sum, 0),
                    newRowCompare = {
                        manager: 'СУММАРНО:',
                        plan: allPlansCompare,
                        potential_sum: newArrCompare.reduce((sum, current) => sum + current.potential_sum, 0),
                        sum_deals: newArrCompare.reduce((sum, current) => sum + current.sum_deals, 0),
                        sum_pay: newArrCompare.reduce((sum, current) => sum + current.sum_pay, 0),
                        sum_pay_tithe: newArrCompare.reduce((sum, current) => sum + current.sum_pay_tithe, 0),
                        sum_pay_church: newArrCompare.reduce((sum, current) => sum + current.sum_pay_church, 0),
                        total_sum: allSumCompare,
                        percent_of_plan: (100 / (allPlansCompare / allSumCompare)).toFixed(1),
                        total_partners: newArrCompare.reduce((sum, current) => sum + current.total_partners, 0),
                        active_partners: newArrCompare.reduce((sum, current) => sum + current.active_partners, 0),
                        not_active_partners: newArrCompare.reduce((sum, current) => sum + current.not_active_partners, 0),
                    };
                newArr.push(newRow);
                newArrCompare.push(newRowCompare);
                let sortedData = {
                    table_columns: actualData.table_columns,
                    result: newArr,
                    resultCompare: newArrCompare,
                    firstDate: actualData.firstDate,
                    secondDate: actualData.secondDate,
                    flag: actualData.flag,
                };
                callback(sortedData, actualData);
            } else {
                callback(actualData, actualData);
            }
        }, 500));
    }
}