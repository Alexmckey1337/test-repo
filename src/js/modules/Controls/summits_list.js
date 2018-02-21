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
import dataHandling from '../Error';
import reverseDate from '../Date';

export function SummitListTable(config) {
    getData(URLS.controls.summit_access(), config).then(data => makeSummitListTable(data));
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
    createSummitListTable(data);
    new OrderTable().sort(summitListTable, ".table-wrap th");
    $('.preloader').hide();
}

export function summitListTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getData(URLS.controls.summit_access(), config).then(data => makeSummitListTable(data, config));
}

function createSummitListTable(data) {
    let table = `<table class="tableSummitList">
                        <thead>
                            <tr>
                                <th data-order="no_ordering">Название саммита</th>
                                <th data-order="type">Тип саммита</th>
                                <th data-order="start_date">Дата начала</th>
                                <th data-order="end_date">Дата окончания</th>                                        
                                <th data-order="status">Статус</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
        return `<tr>
                            <td class="edit" data-id="${item.id}">
                                ${item.type.title} ${reverseDate(item.start_date, '-')}
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
                                ${item.status === 'open' ? 'Открытый' : 'Закрытый'}
                            </td>
                        </tr>`;}).join('')}</tbody>
                        </table>`;
    $('#tableSummitListWrap').append(table);
}

export function btnSummitControlls() {
    $("#tableSummitListWrap").on('click', '.edit', function () {
        let form = $('#addSammit'),
            id = $(this).data('id');
        form.attr('data-id', id).addClass('active').addClass('change').removeClass('add');
        $('.bg').addClass('active');
        refreshAddSummitFields();
        form.find('.popup_text').find('h2').text('Изменить саммит');
        removeValidText(form);
        getData(URLS.controls.summit_detail(id)).then(data => completeForm(data));
    });
}

export function refreshAddSummitFields() {
    let form = $('#addSammitForm'),
        $input = form.find('input'),
        $select = form.find('select');
    $input.each(function () {
        $(this).val('')
    });
    $select.each(function () {
        $(this).val(null).trigger("change");
    });
}

export function submitSummit() {
    let form = $('#addSammitForm'),
        $input = form.find('label').find('input, select'),
        type = $('#addSammit').hasClass('add') ? 'add' : 'save',
        data = {},
        config = {},
        id = $('#addSammit').data('id'),
        url = (type === 'add') ? URLS.controls.summit_access() : URLS.controls.summit_detail(id),
        message = (type === 'add') ? 'Саммит успешно создан' : 'Саммит успешно сохранен';
    $input.each(function () {
        let name = $(this).attr('name');
        if ($(this).hasClass('summit-date')) {
            data[name] = reverseDate($(this).val(), '-');
        } else {
            data[name] = $(this).val();
        }
    });
    (type === 'save') && Object.assign(config, {method: 'PUT'});
    postData(url, data, config).then(_ => {
        showAlert(message);
        $('#addSammit').removeClass('active');
        $('.bg').removeClass('active');
        summitListTable();
    }).catch(err => dataHandling(err));
}

function completeForm(data) {
    let form = $('#addSammit');
    for (let key in data) {
        if (key != 'id') {
            let input = form.find('[name = ' + key + ']');
            if (input.is('select') && data[key] != null) {
                (typeof data[key] === 'object') ?
                    input.val(data[key].id).trigger('change')
                    :
                    input.val(data[key]).trigger('change');
            } else {
                input.val(data[key]);
            }
        }
    }
}

export function removeValidText(form) {
    let errInput = form.find('.has-error');
    errInput.each(function (i, el) {
       $(el).removeClass('has-error').find('.help-block').remove();
       let inp = $(el).removeClass('has-error').find('input, select, textarea');
       $(inp).css('border-color', '#cdd0d4');
    });
}