'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'whatwg-fetch';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import {getFilterParam} from "../Filter/index";
import getData, {postData, deleteData} from '../Ajax/index';
import getSearch from '../Search/index';
import OrderTable from '../Ordering/index';
import {showAlert} from "../ShowNotifications/index";
import makePagination from '../Pagination/index';
import {refreshFilter} from "../Filter/index";
import updateHistoryUrl from '../History/index';
import {showConfirm} from "../ShowNotifications/index";
import dataHandling from '../Error';

export function SummitListTable(config) {
    getData(URLS.controls.summit_access(), config).then(data => {
        makeSummitListTable(data);
    });
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
    createSummitListTable(data, '#tableSummitListWrap');
    new OrderTable().sort(summitListTable, ".table-wrap th");
    $('.preloader').hide();
}
export function summitListTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getData(URLS.controls.summit_access(), config).then(data => {
        makeSummitListTable(data, config);
    });
}

function createSummitListTable(data,block) {
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
                                ${item.type.title} ${item.start_date.split('.').reverse().join('-')}
                                <!--<button class="delete_btn"></button>-->
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
                                ${item.status === 'open'?'Открытый':'Закрытый'}
                            </td>
                        </tr>
                            `;
    }).join('')}</tbody>
                        </table>`;
    $(block).append(table);

    btnControll();
}
function btnControll() {
    $(".tableSummitList").find('.edit').on('click', function (e) {
        let target = e.target;
        if (!$(target).hasClass('delete_btn')) {
            let clear_btn = $('#addSammit').find('.add-summit'),
                id = $(this).data('id'),
                form = $('#addSammit');
            $('#addSammit').attr('data-id',id).addClass('active').addClass('change').removeClass('add');
            $('.bg').addClass('active');
            refreshFilter($(clear_btn));
            $('#addSammit').find('.popup_text').find('h2').text('Изменить саммит');
            removeValidText($('#addSammit'));
            getData(URLS.controls.summit_detail(id)).then(function (data) {
                completeForm(form, data);
            });
        } else {
            let id = $(this).data('id'),
                message = 'Вы действительно хотите удалить саммит?';
            showConfirm('Удаление', message, function () {
                deleteData(URLS.controls.summit_detail(id)).then(function () {
                    $('.preloader').css('display', 'block');
                    summitListTable();
                    showAlert('Саммит удален');
                }).catch(err => dataHandling(err));
            });
        }
    });
}
export function submitSummit(el,type) {
    let field = $(el).find('input, select, textarea'),
        data = {},
        id = $('#addSammit').data('id'),
        url = type === 'add' ? URLS.controls.summit_access() : URLS.controls.summit_detail(id),
        config = type === 'add' ? {} : {method:'PUT'};
    $(field).each(function (i, el) {
        data[$(el).attr('name')] = $(el).val();
    });
    postData(url, data, config).then(function () {
        console.log(url, config, id);
        showAlert(type === 'add' ? 'Саммит успешно создан' : 'Саммит успешно сохранен');
        $('#addSammit').removeClass('active');
        $('.bg').removeClass('active');
        summitListTable();
    }).catch(function (err) {
        dataHandling(err);
    });
}

function completeForm(form,data) {
    for (let key in data) {
        if (key != 'id') {
            let input = form.find('[name = ' + key + ']');
            if ($(input).is('select') && data[key] != null) {
                if(typeof data[key] === 'object'){
                    $(input).val(data[key].id).trigger('change');
                }else {
                    $(input).val(data[key]).trigger('change');
                }
            } else if (key.search(/date/g) != -1) {
                $(input).val(data[key].split('.').reverse().join('-'));
            } else{
                $(input).val(data[key]);
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
};