'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import {deleteData} from "../Ajax/index";
import newAjaxRequest from  '../Ajax/newAjaxRequest';
import ajaxSendFormData from '../Ajax/ajaxSendFormData';
import getSearch from '../Search/index';
import {getFilterParam, getTabsFilterParam} from "../Filter/index";
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import OrderTable from '../Ordering/index';
import {showAlert, showConfirm} from "../ShowNotifications/index";
import updateHistoryUrl from '../History/index';

export function HomeReportsTable(config) {
    getHomeReports(config).then(data => {
        makeHomeReportsTable(data);
    });
}

export function homeReportsTable(config = {}) {
    let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');
    config.is_submitted = is_submitted;
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getTabsFilterParam());
    updateHistoryUrl(config);
    getHomeReports(config).then(data => {
        makeHomeReportsTable(data, config);
    })
}

function getHomeReports(config = {}) {
    if (!config.is_submitted) {
        let is_submitted = parseInt($('#statusTabs').find('.current').find('button').attr('data-is_submitted'));
        config.is_submitted = is_submitted || 'false';
    }
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.list(),
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            data: config
        };
        let status = {
            200: function (req) {
                resolve(req);
            },
            403: function () {
                reject('Вы должны авторизоватся');
            }

        };
        newAjaxRequest(data, status);
    })
}

function makeHomeReportsTable(data, config = {}) {
    let tmpl = $('#databaseHomeReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeReports').html(rendered);
    let count = data.count;
    let pages = Math.ceil(count / CONFIG.pagination_count);
    let page = config.page || 1;
    let showCount = (count < CONFIG.pagination_count) ? count : data.results.length;
    let text = `Показано ${showCount} из ${count}`;
    let paginationConfig = {
        container: ".reports__pagination",
        currentPage: page,
        pages: pages,
        callback: homeReportsTable
    };
    // $('.table__count').text(data.count);
    makePagination(paginationConfig);
    makeSortForm(data.table_columns);
    fixedTableHead();
    $('.table__count').text(text);
    new OrderTable().sort(homeReportsTable, ".table-wrap th");
    $('.preloader').css('display', 'none');
    btnControls();
}

function btnControls() {
    $("button.delete_btn").on('click', function () {
        let id = $(this).attr('data-id');
        showConfirm('Удаление', 'Вы действительно хотите удалить данный отчет?', function () {
            deleteData(URLS.event.home_meeting.detail(id)).then(() => {
                showAlert('Отчет успешно удален!');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                homeReportsTable({page: page});
            }).catch((error) => {
                let errKey = Object.keys(error),
                    html = errKey.map(errkey => `${error[errkey]}`);
                showAlert(html[0], 'Ошибка');
            });
        }, () => {
        });
    });
    $('button.view_img').on('click', function () {
        let url = $(this).attr('data-img'),
            photo = document.createElement('img');
        $(photo).attr('src', url);
        showAlert(photo, 'Фото присутствующих');
    })
}

export function makeHomeReportDetailTable(data) {
    let tmpl = $('#databaseHomeReports').html();
    let rendered = _.template(tmpl)(data);
    $('#homeReports').html(rendered);
    fixedTableHead();
}

export function getHomeReportDetailData(config = {}) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.detail(REPORTS_ID),
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            data: config
        };
        let status = {
            200: function (req) {
                resolve(req);
            },
            403: function () {
                reject('Вы должны авторизоватся');
            }
        };
        newAjaxRequest(data, status);
    })
}

export function getHomeReportDetailTableData(config = {}) {
    let pathnameArr = window.location.pathname.split('/');
    const REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];

    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.event.home_meeting.visitors(REPORTS_ID),
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            data: config
        };
        let status = {
            200: function (req) {
                resolve(req);
            },
            403: function () {
                reject('Вы должны авторизоватся');
            }

        };
        newAjaxRequest(data, status);
    })
}

export function makeCaption(data) {
    let container = document.createElement('div'),
        title,
        dist = {
            night: "О Марафоне",
            home: "Домашней группы",
            service: "О Воскресном Служении"
        };
    if (data.status === 1) {
        title = `Подача отчета ${dist[data.type.code]}`;
    } else if (data.status === 2) {
        title = `Отчет ${dist[data.type.code]}`;
    } else if (data.status === 3) {
        title = `Отчет ${dist[data.type.code]}<span> (просрочен)</span>`;
    }
    $(container).addClass('hg_caption');
    let txt = `<h2>${title}</h2>
                 <p>
                    <span>Лидер: </span><a href="/account/${data.owner.id}">${data.owner.fullname}</a>
                 </p>
                 <p>
                    <span>Домашняя группа: </span>
                    <a href="/home_groups/${data.home_group.id}">${data.home_group.title}</a>
                 </p>
                 <p>
                    <label>Дата отчёта: </label>
                    <input id="report_date" value="${data.date}" size="${data.date.length}" data-name="date">
                 </p>
                    ${ (data.type.code != 'service') ?
                        `<p>
                            <label>Сумма пожертвований: </label>
                                <input value=${data.total_sum} size="7" data-name="total_sum">
                            </p>` : '' }
                    ${ (data.type.code == 'home') ?
                    `<p>
                        <label>Загрузить фото: </label>
                        <input type="file" data-name="image" id="file">
                        <button id="clear_img">Очистить фото</button>
                        <img id="hg_attds" src="${(data.image) ? data.image : ''}"/>
                    </p>` : ''}`;
    $(container).append(txt);

    return container;
}

export function sendForms(btn, data) {
    const $homeReports = $('#homeReports'),
          pathnameArr = window.location.pathname.split('/'),
          REPORTS_ID = pathnameArr[(pathnameArr.length - 2)];
    let config = {
            data: data,
            method: 'POST',
            contentType: 'multipart/form-data',
        };

    if (btn.attr('data-update') == 'true') {
        Object.assign(config, {method: 'PUT'});
        config.url = URLS.event.home_meeting.detail(REPORTS_ID);
        ajaxSendFormData(config).then(() => {
            btn.attr({
                'data-click': false,
                'data-update': false,
            });
            btn.text('Редактировать');
            $homeReports.find('input').each(function () {
                $(this).attr('disabled', true);
            });
        });
    } else {
        config.url = URLS.event.home_meeting.submit(REPORTS_ID);
        ajaxSendFormData(config).then((data) => {
            console.log(data);
            btn.text('Редактировать').attr({
                'data-click': false,
                'data-update': false,
            });
            $homeReports.find('input').each(function () {
                $(this).attr('disabled', true);
            });
        }).catch((err) => {
            console.log(err);
            let error = JSON.parse(err.responseText),
                errKey = Object.keys(error);
            let html = errKey.map(errkey => `${error[errkey]}`);
            showAlert(html[0]);
        });
    }
}

export function handleImgFileSelect(e) {
    let $img = $('#hg_attds'),
        files = e.target.files;
    for (let i = 0, file; file = files[i]; i++) {
        if (!file.type.match('image.*')) {
            continue;
        }
        let reader = new FileReader();
        reader.onload = (function () {
            return function (e) {
                $img.attr('src', e.target.result);
            };
        })();
        reader.readAsDataURL(file);
    }
}