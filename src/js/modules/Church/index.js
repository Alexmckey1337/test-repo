'use strict';
import {CONFIG} from '../config';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import newAjaxRequest from '../Ajax/newAjaxRequest';
import getSearch from '../Search/index';
import {getFilterParam} from '../Filter/index';
import OrderTable, {getOrderingData} from '../Ordering/index';
import {getChurches} from '../GetList/index';
import {makePastorList, makeDepartmentList} from '../MakeList/index';
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';
import {showAlert} from "../ShowNotifications/index";
import {hidePopup} from "../Popup/popup";

export function createChurchesTable(config = {}) {
    Object.assign(config, getSearch('search_title'));
    Object.assign(config, getFilterParam());
    Object.assign(config, getOrderingData());
    getChurches(config).then(function (data) {
        let count = data.count;
        let page = config['page'] || 1;
        let pages = Math.ceil(count / CONFIG.pagination_count);
        let showCount = (count < CONFIG.pagination_count) ? count : CONFIG.pagination_count;
        let text = `Показано ${showCount} из ${count}`;
        let tmpl = $('#databaseUsers').html();
        let filterData = {};
        filterData.user_table = data.table_columns;
        filterData.results = data.results;
        let rendered = _.template(tmpl)(filterData);
        $('#tableChurches').html(rendered);
        $('.quick-edit').on('click', function () {
            let id = $(this).closest('.edit').find('a').attr('data-id');
            ajaxRequest(URLS.church.detail(id), null, function (data) {
                let quickEditCartTmpl, rendered;
                quickEditCartTmpl = document.getElementById('quickEditCart').innerHTML;
                rendered = _.template(quickEditCartTmpl)(data);
                $('#quickEditCartPopup').find('.popup_body').html(rendered);
                $('#openingDate').datepicker({
                    dateFormat: 'yyyy-mm-dd',
                    autoClose: true
                });
                makePastorList(data.department, '#editPastorSelect', data.pastor);
                makeDepartmentList('#editDepartmentSelect', data.department).then(function () {
                    $('#editDepartmentSelect').on('change', function () {
                        let id = parseInt($(this).val());
                        makePastorList(id, '#editPastorSelect');
                    })
                });
                setTimeout(function () {
                    $('#quickEditCartPopup').css('display', 'block');
                }, 100)
            })
        });

        makeSortForm(filterData.user_table);
        let paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: createChurchesTable
        };
        makePagination(paginationConfig);
        fixedTableHead();
        $('.table__count').text(text);
        $('.preloader').css('display', 'none');
        new OrderTable().sort(createChurchesTable, ".table-wrap th");
    });
}

export function clearAddChurchData() {
    $('#added_churches_date').val('');
    $('#added_churches_is_open').prop('checked', false);
    $('#added_churches_title').val('');
    $('#added_churches_country').val('');
    $('#added_churches_city').val('');
    $('#added_churches_address').val('');
    $('#added_churches_phone').val('');
    $('#added_churches_site').val('');
}

export function saveChurches(el) {
    let $input, $select, phone_number, opening_date, data, id;
    id = parseInt($($(el).closest('.pop_cont').find('#churchID')).val());
    opening_date = $($(el).closest('.pop_cont').find('#openingDate')).val();
    if (!opening_date && opening_date.split('-').length !== 3) {
        $($(el).closest('.pop_cont').find('#openingDate')).css('border-color', 'red');
        return
    }
    data = {
        title: $($(el).closest('.pop_cont').find('#church_title')).val(),
        pastor: $($(el).closest('.pop_cont').find('#editPastorSelect')).val(),
        department: $($(el).closest('.pop_cont').find('#editDepartmentSelect')).val(),
        phone_number: $($(el).closest('.pop_cont').find('#phone_number')).val(),
        website: ($(el).closest('.pop_cont').find('#web_site')).val(),
        opening_date: $($(el).closest('.pop_cont').find('#openingDate')).val() || null,
        is_open: $('#is_open_church').is(':checked'),
        country: $($(el).closest('.pop_cont').find('#country')).val(),
        region: $($(el).closest('.pop_cont').find('#region')).val(),
        city: $($(el).closest('.pop_cont').find('#city')).val(),
        address: $($(el).closest('.pop_cont').find('#address')).val(),
        report_currency: $($(el).closest('.pop_cont').find('#EditReport_currency')).val(),
    };
    saveChurchData(data, id).then(function () {
        $(el).text("Сохранено");
        $(el).closest('.popap').find('.close-popup.change__text').text('Закрыть');
        $(el).attr('disabled', true);
        $input = $(el).closest('.popap').find('input');
        $select = $(el).closest('.popap').find('select');

        $select.on('change', function () {
            $(el).text("Сохранить");
            $(el).closest('.popap').find('.close-popup').text('Отменить');
            $(el).attr('disabled', false);
        });

        $input.on('change', function () {
            $(el).text("Сохранить");
            $(el).closest('.popap').find('.close-popup').text('Отменить');
            $(el).attr('disabled', false);
        })
    }).catch(function (res) {
        let error = JSON.parse(res.responseText);
        let errKey = Object.keys(error);
        let html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
        showAlert(html);
    });
}

function saveChurchData(data, id) {
    if (id) {
        let json = JSON.stringify(data);
        return new Promise(function (resolve, reject) {
            let data = {
                url: URLS.church.detail(id),
                data: json,
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            let status = {
                200: function (req) {
                    resolve(req);
                },
                400: function (req) {
                    reject(req);
                }
            };
            newAjaxRequest(data, status, reject)
        });
    }
}

export function addChurch(e, el, callback) {
    e.preventDefault();
    let data = getAddChurchData();
    let json = JSON.stringify(data);
    addChurchTODataBase(json).then(function (data) {
        hidePopup(el);
        clearAddChurchData();
        callback();
        showAlert(`Церковь ${data.get_title} добавлена в базу`);
    }).catch(function (data) {
        hidePopup(el);
        showAlert('Ошибка при создании домашней группы');
    });
}

function getAddChurchData() {
    return {
        "opening_date": $('#added_churches_date').val(),
        "is_open": $('#added_churches_is_open').prop('checked'),
        "title": $('#added_churches_title').val(),
        "department": $('#department_select').val(),
        "pastor": $('#pastor_select').val(),
        "country": $('#added_churches_country').val(),
        "city": $('#added_churches_city').val(),
        "address": $('#added_churches_address').val(),
        "phone_number": $('#added_churches_phone').val(),
        "website": $('#added_churches_site').val()
    }
}

function addChurchTODataBase(config) {
    return new Promise(function (resolve, reject) {
        let data = {
            url: URLS.church.list(),
            data: config,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        };
        let status = {
            201: function (req) {
                resolve(req)
            },
            403: function () {
                reject('Вы должны авторизоватся')
            }

        };
        newAjaxRequest(data, status, reject)
    });
}