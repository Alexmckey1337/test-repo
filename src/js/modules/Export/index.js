'use strict';
import getSearch from '../Search/index';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import {getFilterParam} from "../Filter/index";

export default function exportTableData(el, additionalFilter = {}, search = 'search_fio') {
    let _self = el;
    return new Promise(function (resolve, reject) {
        let url, filter, filterKeys, items, count;
        url = $(_self).attr('data-export-url');
        filter = Object.assign(getFilterParam(), getSearch(search), additionalFilter);
        filterKeys = Object.keys(filter);
        if (filterKeys && filterKeys.length) {
            url += '?';
            items = filterKeys.length;
            count = 0;
            filterKeys.forEach(function (key) {
                count++;
                url += key + '=' + filter[key];
                if (count != items) {
                    url += '&';
                }
            })
        }
        let data = {
            url: url,
            method: 'POST',
            data: {
                fields: getDataTOExport().join(',')
            }
        };
        let status = {
            200: function (data, statusText, req) {
                // check for a filename
                let file = createCSV(req);
                if (typeof window.navigator.msSaveBlob !== 'undefined') {
                    // IE workaround for "HTML7007"
                    window.navigator.msSaveBlob(file.file, file.filename);
                } else {
                    let URL = window.URL || window.webkitURL;
                    let downloadUrl = URL.createObjectURL(file.file);

                    if (file.filename) {
                        // use HTML5 a[download] attribute to specify filename
                        let a = document.createElement("a");
                        // safari doesn't support this yet
                        if (typeof a.download === 'undefined') {
                            window.location = downloadUrl;
                        } else {
                            a.href = downloadUrl;
                            a.download = file.filename;
                            document.body.appendChild(a);
                            a.click();
                        }
                    } else {
                        window.location = downloadUrl;
                    }

                    setTimeout(function () {
                        URL.revokeObjectURL(downloadUrl);
                    }, 100); // cleanup
                    resolve(req);
                }
            }
        };
        newAjaxRequest(data, status, reject);
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