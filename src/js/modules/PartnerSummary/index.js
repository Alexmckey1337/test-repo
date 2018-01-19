'use strict';
import moment from 'moment';
import 'moment/locale/ru';
import URLS from '../Urls/index';
import getData, {postData} from "../Ajax/index";
import makeSortForm from '../Sort/index';
import {showAlert} from "../ShowNotifications/index";
import fixedTableHead from '../FixedHeadTable/index';
import {OrderTableByClient} from "../Ordering/index";

export function PartnershipSummaryTable(config = {}) {
    const dateReports = new Date();
    let date = window.state.firstDate;
    $('.preloader').css('display', 'block');
    if (date) {
        Object.assign(config, {
            year: moment(date).format('YYYY'),
            month: moment(date).format('MM')
        })
    }
    getData(URLS.partner.managers_summary(), config).then(data => {
        let newData = makeData(data),
            flag = (moment(dateReports).format('MMM YYYY') === (date ? moment(date).format('MMM YYYY') : moment(dateReports).format('MMM YYYY')));
        (flag) ? newData.flag = true : newData.flag = false;
        window.state = Object.assign(window.state, {
            result: data.results,
            table_columns: data.table_columns,
            firstDate: date ? date : moment(dateReports).toISOString(),
            canEdit: flag,
        });
        makePartnershipSummaryTable(newData);
    });
}

export function updatePartnershipSummaryTable() {
    $('.preloader').css('display', 'block');
    let data = $.extend(true, {}, window.state);
    let newData = makeData({results: data.result, table_columns: data.table_columns});
    (window.state.canEdit) ? newData.flag = true : newData.flag = false;
    makePartnershipSummaryTable(newData);
}

export function updatePartnershipCompareSummaryTable() {
    $('.preloader').css('display', 'block');
    makeCompareSummaryTable();
}

export function PartnershipCompareSummaryTable(config = {}, firstDate = false) {
    $('.preloader').css('display', 'block');
    let url = URLS.partner.managers_summary(),
        date = (firstDate) ?
            $('#date_field_stats').val().split('/')
            :
            $('#date_field_compare').val().split('/');
        Object.assign(config, {month: date[0], year: date[1]});
    (async () => {
        await getData(url, config).then(data => {
            window.state = (firstDate) ?
                Object.assign(window.state, {result: data.results})
                :
                Object.assign(window.state, {resultCompare: data.results});
            makeCompareSummaryTable();
        });
    })();
}

export function partnershipCompareSummaryTable(config = {}) {
    $('.preloader').css('display', 'block');
    let url = URLS.partner.managers_summary(),
        date = window.state.secondDate,
        year = moment(date).format('YYYY'),
        month = moment(date).format('MM');
    Object.assign(config, {month, year});
    (async () => {
        await getData(url, config).then(data => {
                Object.assign(window.state, {table_columns: data.table_columns});
            makeCompareSummaryTable();
        });
    })();
}

export function partnershipSummaryTable(config = {}) {
    $('.preloader').css('display', 'block');
    let month = $('#date_field_stats').val().split('/')[0],
        year = $('#date_field_stats').val().split('/')[1];
    config.year = year;
    config.month = month;
    getData(URLS.partner.managers_summary(), config).then(data => {
        let newData = makeData(data);
        (window.state.canEdit) ? newData.flag = true : newData.flag = false;
        makePartnershipSummaryTable(newData);
    })
}

function makeData(data) {
    let results = data.results.map(elem => {
            let total_sum = +elem.sum_pay + +elem.sum_pay_tithe + +elem.sum_pay_church,
                percent = (100 / (elem.plan / total_sum)).toFixed(1),
                totalPartners = +elem.total_partners + +elem.total_church_partners,
                activePartners = +elem.active_partners + +elem.active_church_partners,
                potentialSum = +elem.potential_sum + +elem.church_potential_sum,
                totalSumDeals = +elem.sum_deals + +elem.sum_church_deals;
            elem.total_partners = totalPartners;
            elem.active_partners = activePartners;
            elem.not_active_partners = totalPartners - activePartners;
            elem.potential_sum = potentialSum;
            elem.sum_deals = totalSumDeals;
            elem.percent_of_plan = isFinite(percent) ? percent : 0;
            elem.total_sum = total_sum;
            return elem;
        }),
        allPlans = data.results.reduce((sum, current) => sum + current.plan, 0),
        allSum = data.results.reduce((sum, current) => sum + current.total_sum, 0),
        newRow = {
            manager: 'СУММАРНО:',
            plan: allPlans,
            potential_sum: data.results.reduce((sum, current) => sum + current.potential_sum, 0),
            sum_deals: data.results.reduce((sum, current) => sum + current.sum_deals, 0),
            sum_pay: data.results.reduce((sum, current) => sum + current.sum_pay, 0),
            sum_pay_tithe: data.results.reduce((sum, current) => sum + current.sum_pay_tithe, 0),
            sum_pay_church: data.results.reduce((sum, current) => sum + current.sum_pay_church, 0),
            total_sum: allSum,
            percent_of_plan: (100 / (allPlans / allSum)).toFixed(1),
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
    let tmpl = $('#databasePartnershipSummary').html(),
        rendered = _.template(tmpl)(data);
    $('#managersPlan').html(rendered);
    makeSortForm(data.table_columns);
    btnControls();
    fixedTableHead();
    new OrderTableByClient().sortByClient(makePartnershipSummaryTable, ".table-wrap th", data);
    new OrderTableByClient().searchByClient(makePartnershipSummaryTable, data, oldData);
    $('.preloader').css('display', 'none');
}

function btnControls() {
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
            sum_pay_church = $(this).closest('tr').find('.sum_pay_church').text(),
            data = {
                plan_sum: value,
            },
            percent = (100 / (value / (+sum_pay + +sum_pay_tithe + +sum_pay_church))).toFixed(1),
            perVal = isFinite(+percent) ? percent : 0;

        postData(URLS.partner.set_managers_plan(id), data).then(res => {
            showAlert(res.message);
            $(this).closest('.edit').removeClass('active').find('input').prop('disabled', true).prop('readonly', true);
            $(this).closest('tr').find('.percent_of_plan').text(`${perVal} %`);
        }).catch(err => {
            showAlert(err.message, 'Ошибка');
        })
    });
}

function makeCompareSummaryTable() {
    let data = makeCompareDate();
    data.firstDate = moment(window.state.firstDate).locale('ru').format('MMM YYYY');
    data.secondDate = moment(window.state.secondDate).locale('ru').format('MMM YYYY');
    data.flag = window.state.canEdit;
    renderCompareTable(data);
}

function makeCompareDate() {
    let data = $.extend(true, {}, window.state),
        dif1 = _.differenceWith(data.result, data.resultCompare, (el1, el2) => el1.user_id === el2.user_id),
        dif2 = _.differenceWith(data.resultCompare, data.result, (el1, el2) => el1.user_id === el2.user_id),
        difference = _.uniqBy(_.concat(dif1, dif2), 'user_id');
    difference.map(el1 => {
        if (!_.some(data.result, ['user_id', el1.user_id])) {
            data.result.push({
                active_church_partners: 0,
                active_partners: 0,
                church_potential_sum: 0,
                manager: el1.manager,
                not_active_partners: 0,
                percent_of_plan: '0.0',
                plan: 0,
                potential_sum: 0,
                sum_church_deals: 0,
                sum_deals: 0,
                sum_pay: 0,
                sum_pay_church: 0,
                sum_pay_tithe: 0,
                total_church_partners: 0,
                total_partners: 0,
                total_sum: 0,
                user_id: el1.user_id,
            });
        }
        if (!_.some(data.resultCompare, ['user_id', el1.user_id])) {
            data.resultCompare.push({
                active_church_partners: 0,
                active_partners: 0,
                church_potential_sum: 0,
                manager: el1.manager,
                not_active_partners: 0,
                percent_of_plan: '0.0',
                plan: 0,
                potential_sum: 0,
                sum_church_deals: 0,
                sum_deals: 0,
                sum_pay: 0,
                sum_pay_church: 0,
                sum_pay_tithe: 0,
                total_church_partners: 0,
                total_partners: 0,
                total_sum: 0,
                user_id: el1.user_id,
            });
        }
    });
    let result = _.sortBy(data.result, el => el.manager),
        resultCompare = _.sortBy(data.resultCompare, el => el.manager),
        newResultData = makeData({
            table_columns: data.table_columns,
            results: result
        }),
        newResultCompareData = makeData({
            table_columns: data.table_columns,
            results: resultCompare
        });

    return {
        result: newResultData.results,
        table_columns: newResultData.table_columns,
        resultCompare: newResultCompareData.results,
    }
}

function renderCompareTable(data, oldData = {}) {
    console.log(data);
    let tmpl = $('#databaseCompareSummary').html(),
        rendered = _.template(tmpl)(data);
    $('#managersPlan').html(rendered);
    makeSortForm(data.table_columns);
    btnControls();
    fixedTableHead();
    new OrderTableByClient().searchCompareByClient(renderCompareTable, data, oldData);
    $('.preloader').css('display', 'none');
}