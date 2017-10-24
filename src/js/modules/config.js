'use strict';

export const CONFIG = {
    'DOCUMENT_ROOT': '/',
    'pagination_count': 30, //Количество записей при пагинации
    'pagination_count_small': 5,
    'pagination_duplicates_count': 10, //Количество записей при пагинации for duplicate users
    'pagination_patrnership_count': 30, //Количество записей при пагинации for patrnership
    'column_table': null
};

export const VOCRM = {};

export let delay = (function () {
    let timer = 0;
    return function (callback, ms) {
        clearTimeout(timer);
        timer = setTimeout(callback, ms);
    };
})();