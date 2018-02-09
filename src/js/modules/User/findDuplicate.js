'use strict';
import numeral from 'numeral/min/numeral.min.js';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import makePagination from '../Pagination/index';

export function makeDuplicateCount(config = {}) {
    let firstName = $('#first_name').val() || null,
        middleName = $('#middle_name').val() || null,
        lastName = $('#last_name').val() || null,
        phoneNumber = numeral($('#phone').inputmask('unmaskedvalue')).value() || null;
    (firstName != null) && (config.first_name = firstName);
    (middleName != null) && (config.middle_name = middleName);
    (lastName != null) && (config.last_name = lastName);
    (phoneNumber != null) && (config.phone_number = phoneNumber);
    config.only_count = true;
    getDuplicates(config).then(data => {
        $('#duplicate_count').html(data.count);
        $('#createUser').find('._preloader').css('opacity', '0');
    });
}

function getDuplicates(options = {}) {
    let keys = Object.keys(options),
        url = URLS.user.find_duplicates();
    if (keys.length) {
        url += '?';
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }
    let defaultOption = {
        method: 'GET',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };
    if (typeof url === "string") {
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}

export function makeDuplicateUsers(config = {}) {
    let firstName = $('#first_name').val() || null,
        middleName = $('#middle_name').val() || null,
        lastName = $('#last_name').val() || null,
        phoneNumber = numeral($('#phone').inputmask('unmaskedvalue')).value() || null,
        popup = $('#create_duplicate_pop');
    (firstName != null) && (config.first_name = firstName);
    (middleName != null) && (config.middle_name = middleName);
    (lastName != null) && (config.last_name = lastName);
    (phoneNumber != null) && (config.phone_number = phoneNumber);
    getDuplicates(config).then(data => {
        let table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Город</th>
                                <th>Ответственный</th>
                                <th>Номер телефонна</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
            let master = item.master;
            if (master == null) {
                master = '';
            } else {
                master = master.fullname;
            }

            return `<tr>
                                       <td><a target="_blank" href="${item.link}">${item.last_name} ${item.first_name} ${item.middle_name}</a></td>
                                       <td>${item.city}</td>
                                       <td>${master}</td>
                                       <td>********${item.phone_number.slice(-4)}</td>
                                     </tr>`;
        }).join('')}</tbody>
                        </table>`;
        let count = data.count,
            page = config.page || 1,
            pages = Math.ceil(count / CONFIG.pagination_duplicates_count),
            showCount = (count < CONFIG.pagination_duplicates_count) ? count : data.results.length,
            text = `Показано ${showCount} из ${count}`,
            paginationConfig = {
                container: ".duplicate_users__pagination",
                currentPage: page,
                pages: pages,
                callback: makeDuplicateUsers
            };
        makePagination(paginationConfig);
        popup.find('.table__count').text(text);
        $('#table_duplicate').html('').append(table);
        $('#createUser').find('._preloader').css('opacity', '0');
        $('.preloader').css('display', 'none');
        popup.css('display', 'block');
    });
}

