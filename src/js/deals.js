$(document).ready(function () {
    "use strict";

    function init() {
        let config = {};
        config["page"] = '1';
        getExpiredDeals(config);
        getDoneDeals(config);
        getUndoneDeals(config);
        makeTabs();
    }

    $('input[name=fullsearch]').on('keyup', function () {
        let config = {};
        config.search = $(this).val();
        getExpiredDeals(config);
        getDoneDeals(config);
        getUndoneDeals(config);
    });

    $("#close-payment").on('click', function () {
        $('#popup-create_payment').css('display', 'none');
    });

    $("#close-payments").on('click', function () {
        $('#popup-payments').css('display', 'none');
        $('#popup-payments table').html('');
    });

    $("#popup-create_payment .top-text span").on('click', function (el) {
        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', '');
    });

    $("#popup-payments .top-text span").on('click', function (el) {
        $('#popup-payments').css('display', '');
        $('#popup-payments table').html('');
    });

    $('#complete-payment').on('click', function () {
        let id = $(this).attr('data-id'),
            sum = $('#new_payment_sum').val(),
            description = $('#popup-create_payment textarea').val();
        createPayment(id, sum, description);
        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', 'none');
    });
    function createPayment(id, sum, description) {
    let data = {
        "sum": sum,
        "description": description,
    };

    let json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + `api/v1.0/deals/${id}/create_payment/`, json, function (JSONobj) {
        showPopup('Оплата прошла успешно.');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        403: function (data) {
            data = data.responseJSON;
            showPopup(data.detail)
        }
    });
}

    function setDataForPopup(id, name, date, responsible, value) {
        $('#complete').attr('data-id', id);
        $('#client-name').text(name);
        $('#deal-date').text(date);
        $('#responsible-name').text(responsible);
        $('#popup').css('display', 'block');
    }

    function showPayments(id) {
        getPayment(id).then(function (data) {
            let payments_table = '';
            let sum, date_time;
            data.forEach(function (payment) {
                sum = payment.effective_sum_str;
                date_time = payment.created_at;
                payments_table += `<tr><td>${sum}</td><td>${date_time}</td></tr>`
            });
            $('#popup-payments table').html(payments_table);
            $('#popup-payments').css('display', 'block');
        })
    }

    function getPaymentCompleteButton(deal, can_pay, can_close) {
        let action, title;
        if (deal.done) {
            return ``;
        } else if (parseInt(deal.value) > parseInt(deal.total_sum) && can_pay) {
            action = "pay";
            title = "Pay";
        } else if (parseInt(deal.value) <= parseInt(deal.total_sum) && can_close) {
            action = "complete";
            title = "Завершить";
        } else {
            return ``;
        }
        return `<button ` +
            `data-id="${deal.id}" data-action=${action} ` +
            `data-name="${deal.full_name}" ` +
            `data-date="${deal.date}" ` +
            `data-responsible="${deal.responsible_name}" ` +
            `data-total_sum="${deal.total_sum}" ` +
            `data-value="${deal.value}">` +
            title +
            `</button>`
    }

    function getDealSum(deal) {
        return `<p>Сумма: <a href="#" class="show_payments" data-id="${deal.id}">` +
            `<span>${deal.total_sum}/${deal.value} ₴</span></a></p>`
    }

    function getExpiredDeals(data) {
        let config = data || null;
        let search = document.getElementsByName('fullsearch')[0].value;
        if (search) {
            search = '&search=' + search;
        } else {
            search = '';
        }
        console.log(config);
        getOverdueDeals(search, config).then(function (data) {
            let count = data.count;
            let can_create_payment = data.can_create_payment;
            let can_close_deal = data.can_close_deal;
            data = data.results;
            let page = config['page'] || 1,
                pages = Math.ceil(count / CONFIG.pagination_count),
                html = '';
            if (data.length == 0) {
                document.getElementById('overdue').innerHTML = '<p class="info">Сделок нет</p>';
                document.getElementById('overdue-count').innerHTML = '0';
                Array.prototype.forEach.call(document.querySelectorAll('.expired-pagination'), function (el) {
                    el.innerHTML = '';
                    el.style.display = 'none';
                });
                return;
            }
            $('#overdue-count').text(count);

            let paginationConfig = {
                container: ".expired__pagination",
                currentPage: page,
                pages: pages,
                callback: getExpiredDeals
            };

            makePagination(paginationConfig);

            for (let i = 0; i < data.length; i++) {
                html +=
                    `<div class="rows-wrap">` +
                    getPaymentCompleteButton(data[i], can_create_payment, can_close_deal) +
                    `<div class="rows">` +
                    `<div class="col">` +
                    `<p><span>${data[i].full_name}</span></p>` +
                    `</div>` +
                    `<div class="col">` +
                    `<p>Сделка за: <span>${data[i].date_created}</span></p>` +
                    `<p>Ответственный: <span>${data[i].responsible_name}</span></p>` +
                    getDealSum(data[i]) +
                    `</div>` +
                    `</div>` +
                    `</div>`;
            }
            document.getElementById('overdue').innerHTML = html;
            $('#overdue a.show_payments').on('click', function (el) {
                let id = $(this).data('id');
                showPayments(id);
            });
            $("#overdue .rows-wrap button").on('click', function () {
                if ($(this).data('action') == 'pay') {
                    console.log('hogome', $(this).data('id'));
                    let id = $(this).data('id');
                    let value = parseInt($(this).data('value'));
                    let total_sum = parseInt($(this).data('total_sum'));
                    let diff = value - total_sum;
                    diff = diff > 0 ? diff : 0;
                    $('#new_payment_sum').val(diff);
                    $('#complete-payment').attr('data-id', id);

                    $('#popup-create_payment').css('display', 'block');
                } else {
                    getDataForPopup(
                        this.getAttribute('data-id'),
                        this.getAttribute('data-name'),
                        this.getAttribute('data-date'),
                        this.getAttribute('data-responsible'),
                        this.getAttribute('data-value') + ' ₴')
                }
            });
        })
    }

    function getDoneDeals(data) {
        let config = data || null;
        let search = document.getElementsByName('fullsearch')[0].value;
        if (search) {
            search = '&search=' + search;
        } else {
            search = '';
        }
        getFinishedDeals(search, config).then(function (data) {
            let count = data.count;
            console.log(data);
            data = data.results;
            let page = config['page'] || 1,
                pages = Math.ceil(count / CONFIG.pagination_count),
                html = '';
            if (data.length == 0) {
                $('#completed').html('<p class="info">Сделок нету</p>');
                $('#completed-count').html('0');
                $('.done-pagination').each(function (el) {
                    $(el).html('');
                    $(el).css('display', 'none');
                });
                return;
            }
            $('#completed-count').html(count);

            let paginationConfig = {
                container: ".done__pagination",
                currentPage: page,
                pages: pages,
                callback: getDoneDeals
            };
            makePagination(paginationConfig);

            for (let i = 0; i < data.length; i++) {
                html +=
                    `<div class="rows-wrap">` +
                    `<div class="rows">` +
                    `<div class="col">` +
                    `<p><span>${data[i].full_name}</span></p>` +
                    `</div>` +
                    `<div class="col">` +
                    `<p>Сделка за: <span>${data[i].date_created}</span></p>` +
                    `<p>Ответственный: <span>${data[i].responsible_name}</span></p>` +
                    getDealSum(data[i]) +
                    `</div>` +
                    `</div>` +
                    `</div>`;
            }
            $('#completed').html(html);
            $('#completed a.show_payments').on('click', function (el) {
                let id = $(this).data('id');
                showPayments(id);
            });
        })
    }

    function getUndoneDeals(data) {
        let config = data || null;
        let search = document.getElementsByName('fullsearch')[0].value;
        if (search) {
            search = '&search=' + search;
        } else {
            search = '';
        }
        getIncompleteDeals(search, config).then(function (data) {
            let count = data.count;
            console.log(data);
            let can_create_payment = data.can_create_payment;
            let can_close_deal = data.can_close_deal;
            data = data.results;
            let page = config['page'] || 1,
                pages = Math.ceil(count / CONFIG.pagination_count),
                html = '';
            if (data.length == 0) {
                let element = document.createElement('p');
                $(element).text('Сделок нету');
                $(element).addClass('info');
                $('#incomplete').appendChild(element);

                $('#incomplete-count').text('0');
                $('.undone-pagination').each(function (el) {
                    $(el).html('');
                    $(el).css('display', 'none');
                });
                return;
            }
            $('#incomplete-count').html(count);
            let paginationConfig = {
                container: ".undone__pagination",
                currentPage: page,
                pages: pages,
                callback: getUndoneDeals
            };
            makePagination(paginationConfig);

            let button;
            for (let i = 0; i < data.length; i++) {
                html +=
                    `<div class="rows-wrap">` +
                    getPaymentCompleteButton(data[i], can_create_payment, can_close_deal) +
                    `<div class="rows">` +
                    `<div class="col">` +
                    `<p><span>${data[i].full_name}</span></p>` +
                    `</div>` +
                    `<div class="col">` +
                    `<p>Сделка за: <span>${data[i].date_created}</span></p>` +
                    `<p>Ответственный: <span>${data[i].responsible_name}</span></p>` +
                    getDealSum(data[i]) +
                    `</div>` +
                    `</div>` +
                    `</div>`;
            }
            document.getElementById('incomplete').innerHTML = html;
            $('#incomplete a.show_payments').on('click', function (el) {
                let id = $(this).data('id');
                showPayments(id);
            });
            $("#incomplete .rows-wrap button").on('click', function () {
                if ($(this).data('action') == 'pay') {
                    console.log('gohome', $(this).data('id'));
                    let id = $(this).data('id');
                    let value = parseInt($(this).data('value'));
                    let total_sum = parseInt($(this).data('total_sum'));
                    let diff = value - total_sum;
                    diff = diff > 0 ? diff : 0;
                    $('#new_payment_sum').val(diff);
                    $('#complete-payment').attr('data-id', id);
                    $('#popup-create_payment').css('display', 'block');
                } else {
                    setDataForPopup(
                        this.getAttribute('data-id'),
                        this.getAttribute('data-name'),
                        this.getAttribute('data-date'),
                        this.getAttribute('data-responsible'),
                        this.getAttribute('data-value') + ' ₴')
                }
            });
        })
    }

    init();
})
;

