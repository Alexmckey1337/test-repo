'use strict';
import getSearch from '../Search/index';
import {postExport} from "../Ajax/index";
import {getFilterParam} from "../Filter/index";
import {showAlert, showPromt} from "../ShowNotifications/index";

export default function exportTableData(el, additionalFilter = {}, search = 'search_fio', urlExp = '') {
    let url, filter, filterKeys, items, count;
    showPromt('Экспорт', 'Введите имя файла', 'File_default', (evt, value) => {
        let perVal = value.replace(/^\s+|\s+$/g, '');
        if (!perVal) {
            showAlert('Имя файла не введено. Повторите попытку');
            return;
        }
        showAlert('Запрос отправлен в обработку. После завершения формирования файла Вы будете оповещены');
        url = ($(el).attr('data-export-url')) ? $(el).attr('data-export-url') : urlExp;
        filter = Object.assign(getFilterParam(), getSearch(search), additionalFilter);
        console.log('Filter -->', filter);
        filterKeys = Object.keys(filter);
        if (filterKeys && filterKeys.length) {
            url += '?';
            items = filterKeys.length;
            count = 0;
            filterKeys.forEach(function (key) {
                count++;
                if (Array.isArray(filter[key])) {
                    if (filter[key].length < 1) {
                        return
                    }
                    let filterItemValues = Object.values(filter[key]);
                    filterItemValues.forEach(value => {
                        url += `${key}=${value}&`;
                    })
                } else {
                    url += `${key}=${filter[key]}&`;
                }
            })
        }
        (Object.keys(filter).length == 0) ? url += `?file_name=${value.trim()}` : url += `file_name=${value.trim()}`;
        let data = {
            fields: getDataTOExport().join(',')
        };
        postExport(url, data).catch(function () {
            showAlert('Ошибка при загрузке файла');
        });
    }, () => {
    });
}

function getDataTOExport() {
    let $fealds = $('#sort-form').find('input');
    let filter = [];
    $fealds.each(function () {
        if ($(this).is(':checked')) {
            filter.push($(this).prop('id'))
        }
    });
    return filter;
}

function createCSV(data) {
    let filename = "";
    let disposition = data.getResponseHeader('Content-Disposition');
    if (disposition && disposition.indexOf('attachment') !== -1) {
        let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        let matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
    }
    let type = data.getResponseHeader('Content-Type') + ';charset=UTF-8';
    return {
        file: new Blob(["\ufeff" + data.responseText], {type: type, endings: 'native'}),
        filename: filename
    };
}