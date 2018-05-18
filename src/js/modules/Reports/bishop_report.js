'use strict';
import URLS from '../Urls/index';
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
import fixedTableHead from '../FixedHeadTable/index';

export default class BishopReport {
    constructor(id) {
        this.summitId = id;
        this.data = {
            results: [],
            table_columns: {
                user_name: {
                    ordering_title: 'user_name',
                    title: 'ФИО',
                    active: true
                },
                total: {
                    ordering_title: 'total',
                    title: 'Всего',
                    active: true
                },
                attend: {
                    ordering_title: 'attend',
                    title: 'Присутствует',
                    active: true
                },
                absent: {
                    ordering_title: 'absent',
                    title: 'Отсутствует',
                    active: true
                },
                phone_number: {
                    ordering_title: 'phone_number',
                    title: 'Номер телефона',
                    active: true
                }
            }
        };
    }

    renderTable() {
        let tmpl = $('#databaseUsers').html();
        return _.template(tmpl)(this.data);
    }

    makeTable() {
        $('.preloader').css('display', 'block');
        this.getReport().then(data => {
            this.data.results = data;
            $('#bishopsReports').html(this.renderTable());
            fixedTableHead();
            $('.table__count').html(`Показано ${this.data.results.length}`);
            $('.preloader').css('display', 'none');
        });
    }

    getReport() {
        let url = `${URLS.summit.report_by_bishop(this.summitId)}?`;
        const filter = Object.assign(getFilterParam(), getSearch('search_fio'));
        Object.keys(filter).forEach((key, i, arr) => {
            url += `${key}=${filter[key]}`;
            if (i + 1 < arr.length) {
                url += '&'
            }
        });
        let options = {
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
        };
        return fetch(url, options)
            .then(res => res.json());
    }
}