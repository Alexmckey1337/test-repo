(function ($) {
    $(document).ready(function () {
        $('#date_field_stats').datepicker({
            maxDate: new Date(),
            startDate: new Date()
        });
        $('#stats_manager').select2();
        if( !$('#statistic_block').hasClass('no_visible')) {
                filterByMonth();
        }
    });

    function filterByMonth(params = {}) {
        let url = '/api/v1.1/partnerships/stats/?',
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
                for (let k in data) {
                    if (!data.hasOwnProperty(k)) continue;
                    if (k != 'partners' && k != 'unpaid_sum_deals') {
                        document.getElementById(k).innerHTML = data[k];
                    }
                }

                let percent = data['paid_sum_deals'] / data['planned_sum_deals'] * 100;
                document.getElementById('percent_paid_sum_deals').innerHTML = percent.toFixed(1) + '%';

                return data.partners;
            }).then(function (partners) {
            $('#partners_table tbody tr').remove();
            let tr = '';
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

                alert('Неверный формат даты')
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
})(jQuery);
