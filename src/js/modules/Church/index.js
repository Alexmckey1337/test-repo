'use strict';
import {CONFIG} from '../config';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import getSearch from '../Search/index';
import {getFilterParam} from '../Filter/index';
import OrderTable, {getOrderingData} from '../Ordering/index';
import {getChurches} from '../GetList/index';
import {makePastorList, makeDepartmentList} from '../MakeList/index';
import makeSortForm from '../Sort/index';
import makePagination from '../Pagination/index';
import fixedTableHead from '../FixedHeadTable/index';

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