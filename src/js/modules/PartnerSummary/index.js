'use strict';
import URLS from '../Urls/index';
import getData, {postData} from "../Ajax/index";
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
        input.attr('data-value', actualVal);
        $(this).closest('.edit').addClass('active').find('input').prop('disabled', false).prop('readonly', false).select();
    });
    $('#managersPlan').find('table').on('click', '.cancel_plan', function (e) {
        e.preventDefault();
        let input = $(this).closest('.edit').find('input'),
            value = input.attr('data-value');
        $(this).closest('.edit').removeClass('active')
               .find('input').val(value).prop('disabled', true).prop('readonly', true);
    });
    $('#managersPlan').find('table form').on('submit', function (e) {
        e.preventDefault();
        let id = $(this).closest('.edit').removeClass('active').find('input').attr('data-id'),
            value = $(this).closest('.edit').find('input').val(),
            sum_pay = $(this).closest('tr').find('.sum_pay').text(),
            sum_pay_tithe = $(this).closest('tr').find('.sum_pay_tithe').text(),
            data = {
                plan_sum: value,
            },
            percent = (100 / (value / (+sum_pay + +sum_pay_tithe))).toFixed(1),
            perVal = isFinite(+percent) ? percent : 0;
        postData(URLS.partner.set_managers_plan(id), data).then(res => {
            showAlert(res.message);
            $(this).closest('.edit').removeClass('active').find('input').prop('disabled', true).prop('readonly', true);
            $(this).closest('tr').find('.percent_of_plan').text(`${perVal} %`);
        }).catch(err => {
            showAlert(err.message, 'Ошибка');
        })
    });
    fixedTableHead();
    new OrderTableByClient().sortByClient(makePartnershipSummaryTable, ".table-wrap th", data);
    new OrderTableByClient().searchByClient(makePartnershipSummaryTable, data, oldData);
    $('.preloader').css('display', 'none');
}