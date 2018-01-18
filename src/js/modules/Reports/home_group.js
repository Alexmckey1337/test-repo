'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import getData, {deleteData} from "../Ajax/index";
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
import reverseDate from '../Date';

export function HomeReportsTable(config = {}) {
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
        let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');
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
    _.map(data.results, item => {
        let date = new Date(reverseDate(item.date, '-')),
            weekNumber = moment(date).isoWeek(),
            startDate = moment(date).startOf('isoWeek').format('DD.MM.YY'),
            endDate = moment(date).endOf('isoWeek').format('DD.MM.YY');
        item.date = `${weekNumber} нед. (${startDate} - ${endDate})`;
    });
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
    $("#homeReports").find('tr').on('click',function (event) {
        let target = event.target,
            $input = $('#updateReport').find('input,textarea'),
            reportId = $(this).find('#reportId').data('id'),
            msg = 'Вы действительно хотите удалить данный отчет',
            $homeReports = $('#updateReport'),
            $items = $('#tableUsers'),
            url = URLS.event.home_meeting.detail(reportId);
            // urlUsers = URLS.event.home_meeting.visitors(reportId);
        $('.save-update').attr('disabled',true);
        if(!$(target).is('a') && !$(target).is('button')){
            getData(url).then(function (data) {
                let dateReportsFormatted = new Date(data.date.split('.').reverse().join(',')),
                    eventDay = [dateReportsFormatted.getDate()],
                    eventMonth = [dateReportsFormatted.getMonth()],
                    thisMonday = (moment(dateReportsFormatted).day() === 1) ? moment(dateReportsFormatted).format() : (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).subtract(6, 'days').format() : moment(dateReportsFormatted).day(1).format(),
                    thisSunday = (moment(dateReportsFormatted).day() === 0) ? moment(dateReportsFormatted).format() : moment(dateReportsFormatted).day(7).format();
                $('#reportDate').datepicker({
                    autoClose: true,
                    minDate: new Date(thisMonday),
                    maxDate: new Date(thisSunday),
                    onRenderCell: function (date, cellType) {
                        var currentDay = date.getDate(),
                            currentMonth = date.getMonth();
                        if (cellType == 'day' && eventDay.indexOf(currentDay) != -1 && eventMonth.indexOf(currentMonth) != -1) {
                            return {
                                html: '<span class="selectedDate">' + currentDay + '</span>'
                            }
                        }
                    },
                    onSelect: function () {
                        $('.save-update').attr('disabled', false);
                    }
                });
                $('#updateReport').attr('data-status',data.status);
                completeFields(data);
                reportUserTable(data,$('#tableUsers'));
                $('#updateReport,.bg').addClass('active');
                $('.save-update').on('click', function () {
                    let data = new FormData(), attends = [];
                    $homeReports.find('input').each(function () {
                        let field = $(this).data('name');
                        if (field) {
                            if (field == 'date') {
                                data.append(field, reverseDate($(this).val(), '-'));
                            } else if (field == 'image') {
                                ($(this)[0].files.length > 0) && data.append(field, $(this)[0].files[0]);
                            } else {
                                data.append(field, $(this).data('value') || $(this).val());
                            }
                        }
                    });
                    $items.find('input').each(function () {
                        let data = {},
                            elem = $(this),
                            name = elem.attr('name');
                        if (name == 'attended') {
                            console.log(elem);
                            data[elem.attr('name')] = elem.prop("checked")
                        } else if (name == 'user_id') {
                            data[elem.attr('name')] = parseInt(elem.val());
                        } else {
                            data[elem.attr('name')] = elem.val();
                        }

                        attends.push(data);
                    });
                    data.append('attends', JSON.stringify(attends));
                    sendForms(data);
                });
            })
            $input.each(function (i, elem) {
                $(elem).on('input', function () {
                    $('.save-update').attr('disabled',false);
                })
                $(elem).on('change', function () {
                    $('.save-update').attr('disabled',false);
                })
            });
            $.validate({
                lang: 'ru',
                form: '#updateReport'
            });
        }
    });
}

function completeFields(data) {
    $('#id_report').text(data.id);
    $('#reportHomeGroup').text(data.home_group.title);
    $("#reportLeader").text(data.owner.fullname);
    $('#reportDonations').val(data.total_sum);
    $('#reportDate').val(data.date);
    $('#reportImage').attr('src',data.image);
}

function reportUserTable(data, block) {
    let table = `${data.attends.map(item => {

        return `<label>
                        <span class="label_block">${item.fullname}</span>
                        <div style="display: none"><input type="text" name="user_id" value="${item.user_id}"></div>
                        ${item.attended ? `<input type="checkbox" name="attended" checked>` : `<input type="checkbox" name="attended">`}
                        <div></div>
                    </label>`;
    }).join('')}`;
    $(block).append(table);
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
        dateTitle,
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

    if (data.type.id === 1) {
        dateTitle = 'служения';
    } else if (data.type.id === 2) {
        dateTitle = 'домашки';
    } else if (data.type.id === 3) {
        dateTitle = 'марафона';
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
                    <label>Дата ${dateTitle}: </label>
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

export function sendForms(data) {
    const idReport = parseInt($('#id_report').text());
    let config = {
            data: data,
            method: 'POST',
            contentType: 'multipart/form-data',
        },
        status = parseInt($('#updateReport').attr('data-status'));
    console.log(status);

    if (status === 2) {
        Object.assign(config, {method: 'PUT'});
        config.url = URLS.event.home_meeting.detail(idReport);
        console.log(config.url);
        ajaxSendFormData(config).then(() => {
            $('#updateReport,.bg').removeClass('active');
            showAlert("Отчет сохранен");
        });
    } else if(status === 1) {
        config.url = URLS.event.home_meeting.submit(idReport);
        console.log(config.url);
        ajaxSendFormData(config).then(() => {
            $('#updateReport,.bg').removeClass('active');
            showAlert("Отчет создан");
        }).catch((err) => {
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