function showPaymentEditForm(data, id) {
    $('#sent_date').val(data.date);
    $('#new_payment_sum').val(data.sum);
    $('#new_payment_currency').find(`option[value="${data.currency}"]`).prop('selected', true);
    $('#new_payment_rate').val(data.rate);
    $('#payment-description').val(data.description);
    $('#operation').val(data.operation);
    $('#complete-payment').attr('data-payment-id', id);
    $('#popup-edit_payment').css('display', 'block');
}

$(document).ready(function () {
    "use strict";

    $('.edit_payment').on('click', function () {
        let payment_id = $(this).attr('data-payment-id'),
            date = $(this).attr('data-payment-date').split('-').reverse().join('.'),
            sum = $(this).attr('data-payment-sum'),
            currencyName = $(this).attr('data-payment-currency-name'),
            currencyId = $(this).attr('data-payment-currency-id'),
            rate = $(this).attr('data-payment-rate'),
            description = $(this).attr('data-payment-description'),
            operation = $(this).attr('data-payment-operation'),
            data = {
            'date': date,
            'sum': sum,
            'rate': rate,
            'description': description,
            'operation': operation
        };
        sumChangeListener(currencyName, currencyId);
        showPaymentEditForm(data, payment_id);
        sumCurrency(sum, operation, rate, $('#in_user_currency'), currencyName)
    });
    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
        let id = $('#complete-payment').attr('data-payment-id'),
            popup = $('#popup-edit_payment'),
            data = {
            'sent_date': popup.find('#sent_date').val().split('.').reverse().join('-'),
            'sum': popup.find('#new_payment_sum').val(),
            'currency_sum': popup.find('#new_payment_currency').val(),
            'rate': popup.find('#new_payment_rate').val(),
            'description': popup.find('#payment-description').val()
        };
        let json = JSON.stringify(data);
        ajaxRequest(URLS.payment.edit_payment(id), json, function (JSONobj) {
            showPopup('Сохранено.');
            setTimeout(function () {
                window.location.reload()
            }, 1500);
        }, 'PATCH', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showPopup(data.detail);
            }
        });

        $('#popup-edit_payment').css('display', 'none');
    });
    $('#close-payment').on('click', function (e) {
        e.preventDefault();
        $('#popup-edit_payment').css('display', 'none');
    });

    $("#popup-edit_payment .top-text span").on('click', function () {
        $('#popup-edit_payment').css('display', 'none');
    });

    $('.delete_payment').on('click', function () {
        let id = $(this).data('payment-id');
        ajaxRequest(URLS.payment.edit_payment(id), null, function (JSONobj) {
            showPopup('Удалено.');
            setTimeout(function () {
                window.location.reload()
            }, 1500);
        }, 'DELETE', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showPopup(data.detail);
            }
        });
    });

    $('#sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

});
