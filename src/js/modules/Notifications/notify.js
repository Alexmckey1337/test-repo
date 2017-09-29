'use strict';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {CONFIG} from '../config';
import getData from '../Ajax/index';
import makePagination from '../Pagination/index';

let today = moment().format('YYYY-MM-DD');

export function makeBirthdayUsers(config = {}) {
    $('.preloader').css('display', 'block');
    let urlBirth = URLS.users_birthdays(),
        configDefault = {
            from_date: today,
            to_date: today,
        };
    Object.assign(configDefault, config);
    getData(urlBirth, configDefault).then(data => {
        let table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Дата рождения</th>
                                <th>Ответственный</th>
                                <th>Номер телефонна</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
                            let master = item.﻿master;
                            if (master == null) {
                                master = '';
                            } else {
                                master = master.fullname;
                            }

            return `<tr>
                        <td><a target="_blank" href="${item.link}">${item.fullname}</a></td>
                        <td>${item.born_date}</td>
                        <td>${master}</td>
                        <td>${item.phone_number}</td>
                    </tr>`;
            }).join('')}</tbody></table>`;
        let count = data.count,
            page = config.page || 1,
            pages = Math.ceil(count / CONFIG.pagination_duplicates_count),
            showCount = (count < CONFIG.pagination_duplicates_count) ? count : data.results.length,
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
                container: ".special_users__pagination",
                currentPage: page,
                pages: pages,
                callback: makeBirthdayUsers
            };
        makePagination(paginationConfig);
        $('.pop-up_special__table').find('.table__count').text(text);
        $('#table_special-users').html('').append(table);
        $('.pop-up_special__table').find('.top-text h3').text('Дни рождения');
        $('.preloader').css('display', 'none');
        $('.pop-up_special__table').removeClass('table-wrap__export').css('display', 'block');
    });
}

export function makeRepentanceUsers(config = {}) {
    $('.preloader').css('display', 'block');
    let urlRepen = URLS.users_repentance_days(),
        configDefault = {
            from_date: today,
            to_date: today,
        };
    Object.assign(configDefault, config);
    getData(urlRepen, configDefault).then(data => {
        let table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Дата покаяния</th>
                                <th>Ответственный</th>
                                <th>Номер телефонна</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
            let master = item.﻿master;
            if (master == null) {
                master = '';
            } else {
                master = master.fullname;
            }

            return `<tr>
                        <td><a target="_blank" href="${item.link}">${item.fullname}</a></td>
                        <td>${item.repentance_date}</td>
                        <td>${master}</td>
                        <td>${item.phone_number}</td>
                    </tr>`;
            }).join('')}</tbody></table>`;
        let count = data.count,
            page = config.page || 1,
            pages = Math.ceil(count / CONFIG.pagination_duplicates_count),
            showCount = (count < CONFIG.pagination_duplicates_count) ? count : data.results.length,
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
                container: ".special_users__pagination",
                currentPage: page,
                pages: pages,
                callback: makeRepentanceUsers
            };
        makePagination(paginationConfig);
        $('.pop-up_special__table').find('.table__count').text(text);
        $('#table_special-users').html('').append(table);
        $('.pop-up_special__table').find('.top-text h3').text('Дни покаяний');
        $('.preloader').css('display', 'none');
        $('.pop-up_special__table').removeClass('table-wrap__export').css('display', 'block');
    });
}

export function makeExports() {
    $('.preloader').css('display', 'block');
    getData('/api/v1.0/notifications/exports/').then(data => {
        console.log(data);
        let table = `<table>
                        <thead>
                            <tr>
                                <th>Заглавие</th>
                                <th>Вложение</th>
                            </tr>
                        </thead>
                        <tbody>${data.export_urls.map(item => {
            return `<tr>
                        <td>${item}</td>
                        <td><a href="${item}">Скачать</a></td>
                    </tr>`;
        }).join('')}</tbody></table>`;
        $('#table_special-users').html('').append(table);
        $('.pop-up_special__table').find('.top-text h3').text('Доступный экспорт');
        $('.preloader').css('display', 'none');
        $('.pop-up_special__table').addClass('table-wrap__export').css('display', 'block');
    });
}