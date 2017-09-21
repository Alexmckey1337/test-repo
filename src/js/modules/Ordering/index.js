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