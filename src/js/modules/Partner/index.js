'use strict';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import ajaxRequest from '../Ajax/ajaxRequest';
import getSearch from '../Search/index';
import {getFilterParam} from "../Filter/index";
import {getOrderingData} from "../Ordering/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import OrderTable from '../Ordering/index';
import {makeDataTable} from "../Table/index";
import getData from "../Ajax/index";

export function getPartners(config) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getPartnersList(config).then(function (response) {
        let page = config['page'] || 1;
        let count = response.count;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let data = {};
        let id = "partnersList";
        let showCount = (count < CONFIG.pagination_count) ? count : response.results.length;
        let text = `Показано ${showCount} из ${count}`;
        let common_table = Object.keys(response.common_table);
        data.user_table = response.user_table;
        common_table.forEach(function (item) {
            data.user_table[item] = response.common_table[item];
        });
        let keys = [];
        for (let k in data.user_table) {
            if (!data.user_table.hasOwnProperty(k)) continue;
            keys.push([k, data.user_table[k].number])
        }
        keys.sort((a, b) => a[1] - b[1]);
        let user_table = {};
        keys.forEach((item) => {
            user_table[item[0]] = data.user_table[item[0]]
        });
        data.user_table = user_table;
        data.results = response.results.map(function (item) {
            let result = item.user;
            common_table.forEach(function (key) {
                result[key] = item[key];
            });
            return result;
        });
        data.count = response.count;
        makeDataTable(data, id);

        $('.preloader').css('display', 'none');

        let paginationConfig = {
            container: ".partners__pagination",
            currentPage: page,
            pages: pages,
            callback: getPartners
        };
        makePagination(paginationConfig);
        $('.table__count').text(text);
        makeSortForm(data.user_table);
        new OrderTable().sort(getPartners, ".table-wrap th");
    });
}

function getPartnersList(data) {
    let config = {
        search: "",
        page: 1
    };
    Object.assign(config, data);
    return new Promise(function (resolve, reject) {

        getData(URLS.partner.list(), config).then(function (data) {
            console.log(config)
            if (data) {
                resolve(data);
            } else {
                reject("Ошибка");
            }
        });
    });
}
