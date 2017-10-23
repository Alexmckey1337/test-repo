'use strict';
import URLS from '../Urls/index';
import getData, {postData} from "../Ajax/index";
import newAjaxRequest from '../Ajax/newAjaxRequest';
import makeSortForm from '../Sort/index';
import {showAlert} from "../ShowNotifications/index";
import fixedTableHead from '../FixedHeadTable/index';
import {OrderTableByClient} from "../Ordering/index";

export function PartnershipSummaryTable(config, flag = true) {
    $('.preloader').css('display', 'block');
    getData(URLS.partner.managers_summary(), config).then(data => {
        let newData = makeData(data);
        (flag) ? newData.flag = true : newData.flag = false;
        makePartnershipSummaryTable(newData);
    });
}

export function partnershipSummaryTable(config = {}, flag = true) {
    let month = $('#date_field_stats').val().split('/')[0],
        year = $('#date_field_stats').val().split('/')[1];
    config.year = year;
    config.month = month;
    getData(URLS.partner.managers_summary(), config).then(data => {
        let newData = makeData(data);
        (flag) ? newData.flag = true : newData.flag = false;
        makePartnershipSummaryTable(newData);
    })
}

function makeData(data) {
    let results = data.results.map(elem => {
            elem.not_active_partners = elem.total_partners - elem.active_partners;
            let percent = (100 / (elem.plan / (+elem.sum_pay + +elem.sum_pay_tithe))).toFixed(1);
            elem.percent_of_plan = isFinite(percent) ? percent : 0;
            return elem;
        }),
        allPlans = data.results.reduce((sum, current) => sum + current.plan, 0),
        allPays = data.results.reduce((sum, current) => sum + current.sum_pay, 0),
        allTithe = data.results.reduce((sum, current) => sum + current.sum_pay_tithe, 0),
        newRow = {
            manager: 'СУММАРНО:',
            plan: allPlans,
            potential_sum: data.results.reduce((sum, current) => sum + current.potential_sum, 0),
            sum_deals: data.results.reduce((sum, current) => sum + current.sum_deals, 0),
            sum_pay: allPays,
            sum_pay_tithe: allTithe,
            percent_of_plan: (100 / (allPlans / (+allPays + +allTithe))).toFixed(1),
            total_partners: data.results.reduce((sum, current) => sum + current.total_partners, 0),
            active_partners: data.results.reduce((sum, current) => sum + current.active_partners, 0),
            not_active_partners: data.results.reduce((sum, current) => sum + current.not_active_partners, 0),
        };
    results.push(newRow);
    return {
        table_columns: data.table_columns,
        results: results
    };
}

function makePartnershipSummaryTable(data, oldData = {}) {
    let tmpl = $('#databasePartnershipSummary').html();
    console.log(data);
    let rendered = _.template(tmpl)(data);
    $('#managersPlan').html(rendered);
    makeSortForm(data.table_columns);
    $('#managersPlan').find('table').on('click', '.edit_btn', function (e) {
        let input = $(this).closest('.edit').find('.edit_plan'),
            actualVal = input.val();
        input.attr('data-value', actualVal).prop('disabled', false).prop('readonly', false).focus();
    });
    $('#managersPlan').find('table .edit_plan').keyup(function (e) {
        if (e.keyCode == 13) {
            let id = e.target.getAttribute('data-id');
            data.plan_sum = e.target.value;
            postData(URLS.partner.set_managers_plan(id), data).then(res => {
                showAlert(res.message);
                $(this).prop('disabled', true).prop('readonly', true);
            }).catch(err => {
                showAlert(err.message, 'Ошибка');
            })
        } else if (e.keyCode == 27) {
            let value = $(this).attr('data-value');
            $(this).val(value).prop('disabled', true).prop('readonly', true);
        }
    });
    fixedTableHead();
    new OrderTableByClient().sortByClient(makePartnershipSummaryTable, ".table-wrap th", data);
    new OrderTableByClient().searchByClient(makePartnershipSummaryTable, data, oldData);
    $('.preloader').css('display', 'none');
}

function updateManagersPlan(id, data) {
    let url = URLS.partner.set_managers_plan(id);
    let config = {
        method: 'POST',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify(data),
    };

    return fetch(url, config).then(data => data.json()).catch(err => err);
}