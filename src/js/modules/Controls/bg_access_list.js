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
import makePagination from '../Pagination/index';
import updateHistoryUrl from '../History/index';

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

export function BdAccessTable(config) {
    getData(URLS.controls.bd_access(), config).then(data => {
        makeBdAccessTable(data);
    }).catch(err => {console.log(err)});

}

function makeBdAccessTable(data, config = {}) {
    let count = data.count,
        page = config['page'] || 1,
        pages = Math.ceil(count / CONFIG.pagination_count),
        showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
        text = `Показано ${showCount} из ${count}`,
        paginationConfig = {
            container: ".bd_access__pagination",
            currentPage: page,
            pages: pages,
            callback: bdAccessTable
        };
    makePagination(paginationConfig);
    $('.table__count').text(text);
    $('#tableBdAccessWrap').html('');
    createBdAccessTable(data, '#tableBdAccessWrap');
    new OrderTable().sort(bdAccessTable, ".table-wrap th");
    $('.preloader').hide();
}
export function bdAccessTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getData(URLS.controls.bd_access(), config).then(data => {
        makeBdAccessTable(data, config);
    }).catch(err => {console.log(err)});;
}

function createBdAccessTable(data,block) {
    let table = `<table class="tableBdAccess">
                        <thead>
                            <tr>
                                <th data-order="last_name">ФИО</th>
                                <th data-order="hierarchy__level">Иерархия</th>
                                <th data-order="is_staff">Персонал</th>
                                <th data-order="is_active">Активный</th>
                                <th data-order="is_active">Доступ к заявкам</th>
                                <th data-order="can_login">Имеет право входа</th>
                                <th data-order="no_ordering">Id и пароль</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
        return `<tr data-id="${item.id}">
                            <td>
                                <a href="${item.link}">${item.fullname}
                            </td>
                            <td data-level="${item.hierarchy.level}" data-id="${item.hierarchy.id}">
                                ${item.hierarchy.title}
                            </td>
                            <td>
                                <label>
                                    ${item.is_staff === true ? `<input type="checkbox" name="is_staff" checked>` : `<input type="checkbox" name="is_staff" data-filter="person">`}
                                    <div></div>
                                </label> 
                            </td>
                            <td>
                                <label>
                                    ${item.is_active === true ? `<input type="checkbox" name="is_active" checked>` : `<input type="checkbox" name="is_active" data-filter="person">`}
                                    <div></div>
                                </label>
                            </td>
                            <td>
                                <label>
                                    ${item.can_login === true ? `<input type="checkbox" name="can_login" checked>` : `<input type="checkbox" name="can_login" data-filter="person">`}
                                    <div></div>
                                </label>
                            </td>
                            <td>
                                <label>
                                    ${item.can_login === true ? `<input type="checkbox" name="can_login" checked>` : `<input type="checkbox" name="can_login" data-filter="person">`}
                                    <div></div>
                                </label>
                            </td>
                            <td>
                                <span class="user-id">${item.id}</span><span class="editPassword">${item.has_usable_password ? 'Изменить пароль' : 'Создать пароль'}</span>
                            </td>
                        </tr>
                            `;
    }).join('')}</tbody>
                        </table>`;
    $(block).append(table);
    btnControll();
}
function btnControll() {
    let obj = {
        data: []
    };
    $('.tableBdAccess').on('change', 'input[type = "checkbox"]', function () {
        obj.data.length = 0;
        let prop = $(this).attr('name'),
            data = {
                user_id: $(this).closest('tr').data('id'),
            };
        if ($(this).is(':checked')) {
            data[prop] = 'True';
        } else {
            data[prop] = 'False';
        }
        obj.data.push(data);
        postData(URLS.controls.bd_access_submit(), obj).catch(err => {console.log(err)});;

    });

    $('.editPassword').on('click',function () {
        let userId = Number($(this).closest('td').find('.user-id').text());
        $('.passwordPopup').css({
            'display': 'block'
        });
        $('#passwordForm').data('id', userId).find('input').each(function (i,el) {
            $(el).val('');
        });
        $('.errorTxt').removeClass('error').removeClass('green').removeClass('novalid').find('span').text('');
    });
}
