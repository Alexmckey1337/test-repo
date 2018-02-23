'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import getData, {deleteData, postData, postFormData} from "../Ajax/index";
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
import dataHandling from '../Error';
import {convertNum} from "../ConvertNum/index";
import {getOrderingData} from "../Ordering/index";

export function HomeReportsTable(config = {}, pagination = true) {
    Object.assign(config, getTypeTabsFilterParam(), getOrderingData());
    getData(URLS.event.home_meeting.list(), config).then(data => {
        makeHomeReportsTable(data, config, pagination);
    }).catch(err => dataHandling(err));
}

export function homeReportsTable(config = {}, pagination = true) {
    Object.assign(config, getSearch('search_title'), getFilterParam(), getTabsFilterParam(), getTypeTabsFilterParam(), getOrderingData());
    (pagination) && updateHistoryUrl(config);
    getData(URLS.event.home_meeting.list(), config).then(data => {
        makeHomeReportsTable(data, config, pagination);
    }).catch(err => dataHandling(err));
}

function getTypeTabsFilterParam() {
    let is_submitted = $('#statusTabs').find('.current').find('button').attr('data-is_submitted');

    return {is_submitted};
}

function makeHomeReportsTable(data, config = {}, pagination = true) {
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
    if (pagination) {
        makePagination(paginationConfig);
        makeSortForm(data.table_columns);
        fixedTableHead();
        $('.table__count').text(text);
        new OrderTable().sort(homeReportsTable, ".table-wrap th");
    }
    $('.preloader').css('display', 'none');
    btnControls();
    btnEditReport();
}

function btnControls() {
    $('button.view_img').on('click', function (e) {
        e.stopPropagation();
        let url = $(this).attr('data-img'),
            photo = document.createElement('img');
        $(photo).attr('src', url);
        showAlert(photo, 'Фото присутствующих');
    });
}

export function btnControlsImg() {
    $('#reportImage').on('change', handleImgFileSelect);

    $('#clear_img').on('click', function (e) {
        e.preventDefault();
        const ID = $('#send_report').attr('data-id');
        ($(this).attr('data-clean') === 'yes') && postData(URLS.event.home_meeting.cleanImg(ID));
        $(this).attr('data-clean', 'no');
        $('#reportImage').val('');
        $('#hg_attds').attr('src', '');
        if (!/safari/i.test(navigator.userAgent)) {
            $('#reportImage').attr('type', '');
            $('#reportImage').attr('type', 'file');
        }
        $(this).closest('.input')
                .find('span')
                .text('Выберите файл');
    });
}

function btnEditReport() {
    $("#homeReports").find('.edit').on('click', function () {
        const ID = $(this).attr('data-id');
        getData(URLS.event.home_meeting.detail(ID)).then(function (data) {
            let dateReportsFormatted = new Date(reverseDate(data.date, ',')),
                thisMonday = (moment(dateReportsFormatted).day() === 1) ?
                    moment(dateReportsFormatted).format()
                    :
                    (moment(dateReportsFormatted).day() === 0) ?
                        moment(dateReportsFormatted).subtract(6, 'days').format()
                        :
                        moment(dateReportsFormatted).day(1).format(),
                thisSunday = (moment(dateReportsFormatted).day() === 0) ?
                    moment(dateReportsFormatted).format()
                    :
                    moment(dateReportsFormatted).day(7).format();
            $('#reportDate').datepicker({
                autoClose: true,
                minDate: new Date(thisMonday),
                maxDate: new Date(thisSunday),
            });
            $('#homeReportForm').get(0).reset();
            completeFields(data);
            $('#tableUsers').html('');
            (data.status === 2) ?
                makeReportUserTable(data.attends)
                :
                getReportUserTable(data.id);
            $('#editReport,.bg').addClass('active');
        });
    });
}

export function sendReport(pagination = true, option = {}) {
    const ID = $('#send_report').attr('data-id'),
        status = $('#send_report').attr('data-status'),
        URL = (status === '2') ?
            URLS.event.home_meeting.detail(ID)
            :
            URLS.event.home_meeting.submit(ID),
        MSG = (status === '2') ?
            'Изменения в отчете поданы'
            :
            'Отчет успешно подан';
    let data = reportData(),
        config = {},
        page = $('.pagination__input').val();
    (status === '2') && (config.method = 'PUT');
    postFormData(URL, data, config).then(_ => {
        let conf = {page};
        (!pagination) && (Object.assign(conf, option));
        homeReportsTable(conf, pagination);
        $('#editReport,.bg').removeClass('active');
        showAlert(MSG);
    }).catch(err => dataHandling(err));
}

function reportData() {
    let data = new FormData(),
        $items = $('#tableUsers').find('input'),
        attends = [];
    data.append('date', reverseDate($('#reportDate').val(), '-'));
    if ($('#reportDonations').attr('type') != 'hidden') {
        data.append('total_sum', convertNum($('#reportDonations').val(), '.'));
    }
    if ($('#reportImage').closest('label').is(":visible") && ($('#reportImage')[0].files.length > 0)) {
        data.append('image', $('#reportImage')[0].files[0]);
    }
    $items.each(function () {
        let elem = $(this),
            user_id = parseInt(elem.attr('data-user_id')),
            id = parseInt(elem.attr('data-id')),
            attended = elem.prop("checked"),
            data = {user_id, attended};
        (id) && (data.id = id);
        attends.push(data);
    });
    data.append('attends', JSON.stringify(attends));

    return data;
}

export function deleteReport(callback, config = {}, pagination = true) {
    let msg = 'Вы действительно хотите удалить данный отчет',
        id = $('#delete_report').attr('data-id');
    showConfirm('Удаление', msg, function () {
        deleteData(URLS.event.home_meeting.detail(id)).then(function () {
            $('.preloader').css('display', 'block');
            callback(config, pagination);
            showAlert('Отчет удален');
            $('#editReport, .bg').removeClass('active');
        }).catch(err => dataHandling(err));
    }, _ => {});
}

function completeFields(data) {
    let title,
        dateTitle,
        dist = {
            night: "Марафон",
            home: "Домашняя",
            service: "Служение"
        };
    $('#delete_report').attr('data-id', data.id);
    $('#send_report').attr({
        'data-id': data.id,
        'data-status': data.status
    });
    $('#reportHomeGroup').text(data.home_group.title);
    $("#reportLeader").text(data.owner.fullname);
    $('#reportDate').val((data.status === 2) ? data.date : '');
    $('#hg_attds').attr('src', data.image ? data.image : '');
    $('#clear_img').attr('data-clean', data.image ? 'yes' : 'no');
    $('#send_report').text((data.status === 2) ? 'Сохранить' : 'Подать');
    (data.status === 2) ?
        title = `Редактирование отчета ${dist[data.type.code]}`
        :
        title = `Подача отчета ${dist[data.type.code]}`;
    $('#report_title').text(title);
    if (data.type.id === 1) {
        dateTitle = 'служения';
    } else if (data.type.id === 2) {
        dateTitle = 'домашки';
    } else if (data.type.id === 3) {
        dateTitle = 'марафона';
    }
    $('#date_title').text(dateTitle);
    if (data.type.id === 2) {
        $('#reportDonations')
            .attr('type', 'text')
            .val((data.status === 2) ? convertNum(data.total_sum, ',') : '')
            .closest('label')
            .css('display', 'block');
        $('#reportImage').closest('label').css('display', 'block');
        $('#hg_attds').closest('label').css('display', 'block');
    } else {
        $('#reportDonations')
            .attr('type', 'hidden')
            .closest('label')
            .css('display', 'none');
        $('#reportImage').closest('label').css('display', 'none');
        $('#hg_attds').closest('label').css('display', 'none');
    }
    if (!data.can_submit) {
        showAlert(data.cant_submit_cause);
        $('#send_report').attr({disabled: true});
    } else {
        $('#send_report').attr({disabled: false});
    }
}

function getReportUserTable (id) {
    getData(URLS.event.home_meeting.visitors(id)).then(data => {
        makeReportUserTable(data.results)
    }).catch(err => dataHandling(err));
}

function makeReportUserTable(data) {
    let nodeElem;
    if (data.length) {
        nodeElem = `<label><p class="update-title">Люди</p></label>
            ${data.map(item => {
                return `<label>
                            <span class="label_block">${item.fullname}</span>
                            ${(item.attended) ?
                                `<input type="checkbox" name="attended"
                                        data-id="${item.id}" 
                                        data-user_id="${item.user_id}" checked/>`
                                :
                                `<input type="checkbox" name="attended" 
                                        data-id="${item.id}"
                                        data-user_id="${item.user_id}"/>`
                            }
                            <span></span>
                        </label>`
            }).join('')}`;
    } else {
        nodeElem = `<label><p class="update-title">Люди</p></label>
                    <label><span>В домашней группе нет людей</span></label>`
    }
    $('#tableUsers').append(nodeElem);
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
        status = parseInt($('#editReport').attr('data-status'));

    if (status === 2) {
        Object.assign(config, {method: 'PUT'});
        config.url = URLS.event.home_meeting.detail(idReport);
        ajaxSendFormData(config).then(() => {
            homeReportsTable();
            $('#editReport,.bg').removeClass('active');
            showAlert("Отчет сохранен");
        });
    } else if(status === 1) {
        config.url = URLS.event.home_meeting.submit(idReport);
        console.log(config.url);
        ajaxSendFormData(config).then(() => {
            // homeReportsTable();
            $('#editReport,.bg').removeClass('active');
            showAlert("Отчет создан");
        }).catch((err) => {
            let error = JSON.parse(err.responseText),
                errKey = Object.keys(error);
            let html = errKey.map(errkey => `${error[errkey]}`);
            showAlert(html[0]);
        });
    }
}

function handleImgFileSelect(e) {
    let files = e.target.files;
    $('#reportImage').closest('.input')
                    .find('span')
                    .text(files['0'].name);
    for (let i = 0, file; file = files[i]; i++) {
        if (!file.type.match('image.*')) {
            continue;
        }
        let reader = new FileReader();
        reader.onload = (function () {
            return function (e) {
                $('#hg_attds').attr('src', e.target.result);
            };
        })();
        reader.readAsDataURL(file);
    }
}