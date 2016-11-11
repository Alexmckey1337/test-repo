/**
 * Created by pluton on 08.11.16.
 */

$(document).ready(function () {
    filterByMonth();
});

function getParameterByName(name, url) {
    if (!url) {
        url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function filterByMonth(params) {
    params = params || {};
    var url = '/api/v1.1/partnerships/stats/?';

    var partner_id = getParameterByName('partner_id');
    if (partner_id) {
        params.partner_id = partner_id;
    }
    fetch(url + $.param(params), {'credentials': 'include'})
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            for (k in data) {
                if (!data.hasOwnProperty(k)) continue;
                if (k != 'partners' && k != 'unpaid_sum_deals') {
                    document.getElementById(k).innerHTML = data[k];
                }
            }

            var percent = data['paid_sum_deals'] / data['planned_sum_deals'] * 100;
            document.getElementById('percent_paid_sum_deals').innerHTML = percent.toFixed(1) + '%';

            return data.partners;
        }).then(function (partners) {
        $('#partners_table tbody tr').remove();
        var tr = '';
        partners.forEach(function (partner) {
            if (partner.is_paid) {
                tr += '<tr class="success">'
            } else {
                tr += '<tr class="danger">'
            }
            tr += '<td>' + partner.partner_name + '</td>';
            tr += '<td>' + partner.total_deals + '</td>';
            tr += '<td>' + partner.paid_deals + '</td>';
            tr += '<td>' + partner.unpaid_deals + '</td>';
            tr += '<td>' + partner.paid_sum_deals + '</td>';
            tr += '<td>' + partner.unpaid_sum_deals + '</td>';
            tr += '<td>' + partner.value + '</td>';
            tr += '</tr>';
        });
        $('#partners_table tbody').append(tr)

    })
        .catch(alert);
}

$(function () {
    $('#datepicker10').datetimepicker({
        viewMode: 'months',
        format: 'MM/YYYY',
        locale: 'ru',
        useCurrent: 'month',
        maxDate: moment()
    });
});

$('#apply_date').click(function () {
    var date, month, year;
    date = $('#date_field').val();

    if (date) {
        console.log(date);
        date = date.split('/');
        if (date.length == 2) {
            month = date[0];
            year = date[1];
            filterByMonth({month: month, year: year})

        } else {
            alert('Неверный формат даты')
        }
    } else {
        alert('Выберите месяц')
    }
});