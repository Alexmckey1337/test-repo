'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import URLS from './modules/Urls/index';
import ajaxRequest from './modules/Ajax/ajaxRequest';
import moment from 'moment/min/moment.min.js';
import {showAlert} from "./modules/ShowNotifications/index";

$(document).ready(function () {
    $('#date_field_stats').datepicker({
        maxDate: new Date(),
        startDate: new Date(),
        autoClose: true,
    });
    $('#stats_manager').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
    if (!$('#statistic_block').hasClass('no_visible')) {
        filterByMonth();
    }
});

function filterByMonth(params = {}) {
    let url = `${URLS.partner.stats_payment()}?`,
        partner_id = $('#stats_manager').val();
    if (partner_id) {
        params.partner_id = partner_id;
    }
    fetch(url + $.param(params), {'credentials': 'include'})
        .then(function (response) {
            $('#statistic_block').removeClass('no_visible');
            return response.json();
        })
        .then(function (data) {
            let deals, partners;
            let total_partners = 0;
            let total_deals = 0;

            partners = data.partners;
            deals = data.deals;

            for (let k in partners) {
                if (!partners.hasOwnProperty(k)) continue;
                document.getElementById(`partners_${k}`).innerHTML = String(partners[k]).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
                total_partners += partners[k];
            }
            for (let k in deals) {
                if (!deals.hasOwnProperty(k)) continue;
                document.getElementById(`deals_${k}`).innerHTML = String(deals[k]).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
                total_deals += deals[k];
            }
            document.getElementById('total_partners').innerHTML = '' + String(total_partners / 2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
            document.getElementById('total_deals').innerHTML = '' + String(total_deals / 2).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
            // document.getElementById('active_partners').innerHTML = ''+String(data.active_partners).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
            // let inertPartners = (total_deals/2) - data.active_partners;
            // document.getElementById('inert_partners').innerHTML = ''+String(inertPartners).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');

            return data.sum;
        })
        .then(function (sum) {
            let a = '';
            for (let code in sum) {
                if (!sum.hasOwnProperty(code)) continue;
                let tmpl = $('#stats_money').html();
                let rendered = _.template(tmpl)(sum[code]);
                a += rendered;
            }
            $('.deaals').html(a);

            $('#ohoho').html('');
        })
        .catch(alert);
}

$('#apply_date').click(function () {
    let date, month, year;
    date = $('#date_field_stats').val();
    if (date) {
        date = date.split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            filterByMonth({month: month, year: year})
        } else {
            showAlert('Неверный формат даты')
        }
    } else {
        date = moment().format('MM/YYYY').split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            filterByMonth({month: month, year: year});
        }
    }
});

function renderDealTable(params = {}) {
    let url = `${URLS.partner.stats_deal()}?`,
        partner_id = $('#stats_manager').val();
    if (partner_id) {
        params.partner_id = partner_id;
    }
    ajaxRequest(url + $.param(params), null, function (data) {
        $('#ohoho').html(data);
    });
}

function renderPaymentTable(params = {}) {
    let url = `${URLS.partner.stat_payment()}?`,
        partner_id = $('#stats_manager').val();
    if (partner_id) {
        params.partner_id = partner_id;
    }
    ajaxRequest(url + $.param(params), null, function (data) {
        $('#ohoho').html(data);
    });
}

$('#detail-payments').on('click', function () {
    let date, month, year;
    date = $('#date_field_stats').val();
    if (date) {
        date = date.split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            renderPaymentTable({month: month, year: year})
        } else {
            showAlert('Неверный формат даты')
        }
    } else {
        date = moment().format('MM/YYYY').split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            renderPaymentTable({month: month, year: year});
        }
    }
});
$('#detail-deals').on('click', function () {
    let date, month, year;
    date = $('#date_field_stats').val();
    if (date) {
        date = date.split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            renderDealTable({month: month, year: year})
        } else {
            showAlert('Неверный формат даты')
        }
    } else {
        date = moment().format('MM/YYYY').split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            renderDealTable({month: month, year: year});
        }
    }
});
