'use strict';
import {hidePopup} from '../Popup/popup';

export function getFilterParam() {
    let $filterFields,
        data = {};
    $filterFields = $('#filterPopup select, #filterPopup input');
    $filterFields.each(function () {
        if ($(this).val() == "ВСЕ") {
            return
        }
        let prop = $(this).data('filter');
        if (prop) {
            if ($(this).attr('type') === 'checkbox') {
                data[prop] = ucFirst($(this).is(':checked').toString());
            } else {
                if ($(this).val()) {
                    data[prop] = $(this).val();
                }
            }
        }
    });

    if ('master_tree' in data && ('pastor' in data || 'master' in data || 'leader' in data)) {
        delete data.master_tree;
    }

    return data;
}

export function getTabsFilterParam() {
    let data = {},
        dataTabs = {},
        dataRange = {},
        type = $('#tabs').find('li.active').find('button').attr('data-id');
    if (type > "0") {
        dataTabs.type = type;
        Object.assign(data, dataTabs);
    }
    let rangeDate = $('.tab-home-stats').find('.set-date').find('input').val();
    if (rangeDate) {
        let dateArr = rangeDate.split('-');
        dataRange.from_date = dateArr[0].split('.').reverse().join('-');
        dataRange.to_date = dateArr[1].split('.').reverse().join('-');
        Object.assign(data, dataRange);
    }
    return data
}

export function getTabsFilter() {
    const $tabsFilter = $('.tabs-filter');
    let data = {};
    const $button = $tabsFilter.find('.active').find('button[data-filter]');
    const $input = $tabsFilter.find('input[data-filter]');

    $button.each(function () {
        let field = $(this).data('filter');
        let value = $(this).data('filter-value');
        console.log(field, value);
        data[field] = value;
    });

    $input.each(function () {
        let field = $(this).data('filter');
        let value = $(this).val();
        data[field] = value;
    });
    return data
}

function ucFirst(str) {
    // только пустая строка в логическом контексте даст false
    if (!str) return str;

    return str[0].toUpperCase() + str.slice(1);
}

export function applyFilter(el, callback) {
    let self = el, data;
    data = getFilterParam();
    $('.preloader').css('display', 'block');
    callback(data);
    setTimeout(function () {
        hidePopup(self);
    }, 300);

    let count = getCountFilter();
    $('#filter_button').attr('data-count', count);
}

export function refreshFilter(el) {
    let $input = $(el).closest('.popap').find('input'),
        $select = $(el).closest('.popap').find('select'),
        $selectCustom = $(el).closest('.popap').find('select.select__custom');
    $(el).addClass('refresh');
    setTimeout(function () {
        $(el).removeClass('refresh');
    }, 700);
    $input.each(function () {
        $(this).val('')
    });
    $select.each(function () {
        $(this).val(null).trigger("change");
    });
    $selectCustom.each(function () {
        $(this).val('ВСЕ').trigger("change");
    });
}

export function hideFilter() {
    if ($('.top input').length && !$('.top input').val().length) {
        $('.top .search').animate({width: "50%"});
    }
}

export function getCountFilter() {
    let $filterFields,
        count = 0;
    $filterFields = $('#filterPopup select, #filterPopup input');
    $filterFields.each(function () {
        if ($(this).val() == "ВСЕ") {
            return
        }
        if ($(this).val()) {
            count++;
        }
    });

    return count;
}

export function getPreSummitFilterParam() {
    let $filterFields,
        data = {};
    $filterFields = $('.charts_head select');
    $filterFields.each(function () {
        if ($(this).val() == "ВСЕ") {
            return
        }
        let prop = $(this).data('filter');
        if (prop) {
            if ($(this).val()) {
                data[prop] = $(this).val();
            }
        }
    });

    return data;
}



