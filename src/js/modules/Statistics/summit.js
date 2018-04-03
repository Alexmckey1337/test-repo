'use strict';
import moment from 'moment';
import 'moment/locale/ru';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import makePagination from '../Pagination/index';
import getSearch from '../Search/index';
import {getFilterParam, getTabsFilter, getPreSummitFilterParam} from "../Filter/index";
import makeSortForm from '../Sort/index';
import OrderTable from '../Ordering/index';
import fixedTableHead from '../FixedHeadTable/index';
import {getResponsibleForSelect} from "../GetList/index";

export default class SummitStat {
    constructor(id) {
        this.summitID = id;
        this.sortTable = new OrderTable();
    }

    getStatsData(config = {}) {
        let options = {
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            }),
        };
        let url = `${URLS.summit.stats(this.summitID)}?`;
        Object.keys(config).forEach((param, i, arr) => {
            url += `${param}=${config[param]}`;
            if (i + 1 < arr.length) {
                url += '&'
            }
        });
        return fetch(url, options)
            .then(res => res.json())
    }

    makePage(count, length, page = 1) {
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : length;
        let text = `Показано ${showCount} из ${count}`;
        $('.table__count').html(text);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: this.makeDataTable.bind(this)
        };
        makePagination(paginationConfig);
    }

    makeDataTable(config = {}) {
        $('.preloader').css('display', 'block');
        Object.assign(config, getFilterParam(), getTabsFilter(), getSearch('search_fio'));
        this.getStatsData(config)
            .then(data => {
                this.makePage(data.count, data.results.length, config.page);
                makeSammitsDataTable(data, 'summitUsersList');
                makeSortForm(data.user_table);
                this.sortTable.sort(this.makeDataTable.bind(this), ".table-wrap th");
                $('.preloader').css('display', 'none');
                changeSummitStatusCode();
            });
    }
}

function makeSammitsDataTable(data, id) {
    data.results.map(item => {
        (item.attended != null) && (item.attended = moment(item.attended).locale('ru').format('LTS'))
    });
    let tmpl = document.getElementById('databaseUsers').innerHTML,
        rendered = _.template(tmpl)(data);
    document.getElementById(id).innerHTML = rendered;
    $('.quick-edit').on('click', function () {
        makeQuickEditSammitCart(this);
    });
    fixedTableHead();
}

function makeQuickEditSammitCart(el) {
    let anketID, id, link, url;
    anketID = $(el).closest('td').find('a').data('ankets');
    id = $(el).closest('td').find('a').data('id');
    link = $(el).closest('td').find('a').data('link');
    url = URLS.summit_profile.detail(anketID);
    ajaxRequest(url, null, function (data) {
        $('#fullNameCard').text(data.full_name);
        $('#userDescription').val(data.description);
        $('#summit-valueDelete').val(data.total_sum);
        $('#member').prop("checked", data.is_member);
        $('#userID').val(data.user_id);
        $('#applyChanges').data('id', data.id);
        $('#preDeleteAnket').attr('data-id', data.user_id).attr('data-anket', data.id);
        $('#popupParticipantInfo').css('display', 'block');
    }, 'GET', true, {
        'Content-Type': 'application/json'
    });
}

function changeSummitStatusCode() {
    $('#summitUsersList').find('.ticket_code').find('input').on('change', function () {
        let id = $(this).closest('.ticket_code').attr('data-id'),
            ban = $(this).prop("checked") ? 0 : 1,
            option = {
                method: 'POST',
                credentials: 'same-origin',
                headers: new Headers({
                    'Content-Type': 'application/json',
                }),
                body: JSON.stringify({
                    anket_id: id,
                    active: ban
                })
            };
        fetch(URLS.profile_status(), option)
            .then(
                $(this).closest('.ticket_code').find('a').toggleClass('is-ban')
            )

    });
}

export function getSummitStats(url, config = {}) {
    // Object.assign(config, getFilterParam());
    Object.assign(config, getPreSummitFilterParam());
    return new Promise(function (resolve, reject) {
        let data = {
            url: url,
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }

        };
        newAjaxRequest(data, status, reject)
    });
}

export function makeResponsibleSummitStats(config, selector = [], active = null) {
    getResponsibleForSelect(config).then(function (data) {
        let options = '<option selected>ВСЕ</option>';
        data.forEach(function (item) {
            options += `<option value="${item.id}"`;
            if (active == item.id) {
                options += 'selected';
            }
            options += `>${item.title}</option>`;
        });
        selector.forEach(item => {
            $(item).html(options).prop('disabled', false).select2();
        })
    });
}

export function getSummitStatsForMaster(summitId, masterId, config = {}) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.summit.stats_by_master(summitId, masterId),
            data: config,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        };
        let status = {
            200: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }

        };
        newAjaxRequest(data, status, reject)
    });
}