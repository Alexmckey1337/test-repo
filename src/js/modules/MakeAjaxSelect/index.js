"use strict";
import 'select2';
import 'select2/dist/css/select2.css';

export default function makeSelect(selector, url, parseFunc, formatRepo = formatRepo) {
    selector.select2({
        ajax: {
            url: url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    search: params.term,
                    page: params.page
                };
            },
            processResults: parseFunc,
            cache: true
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        templateResult: formatRepo,
        templateSelection: formatRepo
    });
}

function formatRepo(data) {
    if (data.id === '') {
        return '-------';
    }
    return `<option value="${data.id}">${data.text}</option>`;
}