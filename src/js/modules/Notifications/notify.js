'use strict';
import URLS from '../Urls/index';
import {CONFIG} from '../config'
import makePagination from '../Pagination/index';
import moment from 'moment/min/moment.min.js';

export function counterNotifications() {
    let url = URLS.notification_tickets();
    let defaultOption = {
        method: 'GET',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };

    return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
}

export function birhtdayNotifications(options = {}, count = false) {
    let keys = Object.keys(options),
        today = moment().format('YYYY-MM-DD'),
        url = (count) ? `${URLS.users_birthdays(today)}&only_count=true&` : `${URLS.users_birthdays(today)}&`,
        defaultOption = {
            method: 'GET',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
    if (keys.length) {
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }

    return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
}

export function repentanceNotifications(options = {}, count = false) {
    let keys = Object.keys(options),
        today = moment().format('YYYY-MM-DD'),
        url = (count) ? `${URLS.users_repentance_days(today)}&only_count=true&` : `${URLS.users_repentance_days(today)}`,
        defaultOption = {
            method: 'GET',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
    if (keys.length) {
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }

    return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
}

export function makeBirthdayUsers(config = {}) {
    $('.preloader').css('display', 'block');
    birhtdayNotifications(config).then(data => {
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
        $('.pop-up_special__table').css('display', 'block');
    });
}

export function makeRepentanceUsers(config = {}) {
    $('.preloader').css('display', 'block');
    repentanceNotifications(config).then(data => {
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
        $('.pop-up_special__table').css('display', 'block');
    });
}