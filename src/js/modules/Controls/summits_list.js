'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'whatwg-fetch';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import {getFilterParam} from "../Filter/index";
import getData, {postData} from '../Ajax/index';
import getSearch from '../Search/index';
import OrderTable from '../Ordering/index';
import {showAlert} from "../ShowNotifications/index";
import makePagination from '../Pagination/index';
import updateHistoryUrl from '../History/index';
import makeSelect from '../MakeAjaxSelect/index';

function parseFunc(data, params) {
    params.page = params.page || 1;
    const results = [];
    data.results.forEach(function makeResults(element) {
        results.push({
            id: element.id,
            name: element.title,
        });
    });
    return {
        results: results,
        pagination: {
            more: (params.page * 100) < data.count
        }
    };
}
function formatRepo(data) {
    if (data.id === '') {
        return 'ВСЕ';
    } else {
        return `<option value="${data.id}">${data.name}</option>`;
    }
}

export function SummitListTable(config) {
    getData(URLS.controls.summit_access(), config).then(data => {
        makeSummitListTable(data);
    });

}

function makeSummitListTable(data, config = {}) {
    let count = data.count,
        page = config['page'] || 1,
        pages = Math.ceil(count / CONFIG.pagination_count),
        showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
        text = `Показано ${showCount} из ${count}`,
        paginationConfig = {
            container: ".summit__pagination",
            currentPage: page,
            pages: pages,
            callback: summitListTable
        };
    makePagination(paginationConfig);
    $('.table__count').text(text);
    $('#tableSummitListWrap').html('');
    createSummitListTable(data, '#tableSummitListWrap');
    new OrderTable().sort(summitListTable, ".table-wrap th");
    $('.preloader').hide();
}
export function summitListTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getData(URLS.controls.summit_access(), config).then(data => {
        makeSummitListTable(data, config);
    });
}

function createSummitListTable(data,block) {
    let table = `<table class="tableSummitList">
                        <thead>
                            <tr>
                                <th data-order="">Название саммита</th>
                                <th data-order="">Тип саммита</th>
                                <th data-order="">Дата начала</th>
                                <th data-order="">Дата окончания</th>                                        
                                <th data-order="">Статус</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
        return `<tr data-id="${item.id}">
                            <td>
                                ${item.description}
                                <button class="view_img" data-img="${item.type.image}"></button>
                            </td>
                            <td>
                                ${item.type.title}
                            </td>
                            <td>
                                ${item.start_date}
                            </td>
                            <td>
                                ${item.end_date}
                            </td>
                            <td>
                                ${item.status}
                            </td>
                        </tr>
                            `;
    }).join('')}</tbody>
                        </table>`;
    $(block).append(table);
    btnControll();
}
function btnControll() {

}
