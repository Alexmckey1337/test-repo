'use strict';
import {CONFIG} from "../config";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {getHomeLiderReports} from "../GetList/index";
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
import updateHistoryUrl from '../History/index';

export function makeHomeLiderReportsTable(data, config = {}) {
    let tmpl = $('#databaseHomeLiderReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeLiderReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: homeLiderReportsTable
    };
    $('.table__count').text(data.count);
    $('#homeLiderReports').find('table').on('click', (e) => {
        if (e.target.className != 'url') return;
        let url = e.target.getAttribute('data-url'),
            type = e.target.getAttribute('data-type'),
            nameId = e.target.getAttribute('data-id');
        window.location = `${url}?type=${type}&owner=${nameId}`;
    });
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    $('.table__count').text(text);
    fixedTableHead();
    new OrderTable().sort(homeLiderReportsTable, ".table-wrap th");
    $('.preloader').hide();
}

export function homeLiderReportsTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getHomeLiderReports(config).then(data => {
        makeHomeLiderReportsTable(data, config);
    })
}