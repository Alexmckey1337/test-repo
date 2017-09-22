'use strict';
import numeral from 'numeral/min/numeral.min.js';

export function btnDeals() {
    $("button.pay").on('click', function () {
        let id = $(this).attr('data-id'),
            val = $(this).attr('data-value'),
            value = numeral(val).value(),
            total = $(this).attr('data-total_sum'),
            total_sum = numeral(total).value(),
            diff = numeral(value).value() - numeral(total_sum).value(),
            currencyName = $(this).attr('data-currency-name'),
            currencyID = $(this).attr('data-currency-id'),
            payer = $(this).attr('data-name'),
            responsible = $(this).attr('data-responsible'),
            date = $(this).attr('data-date');
        $('#complete-payment').attr('data-id', id);
        diff = diff > 0 ? diff : 0;
        $('#payment_name').text(payer);
        $('#payment_responsible').text(responsible);
        $('#payment_date').text(date);
        $('#payment_sum, #all_payments').text(`${value} ${currencyName}`);
        clearSumChange(total_sum);
        sumChange(diff, currencyName, currencyID, total_sum);
        $('#popup-create_payment').css('display', 'block');
        $('#new_payment_rate').focus();
    });
}

function clearSumChange(total) {
    $('#new_payment_sum').val('');
    $('#new_payment_rate').val('').prop('readonly', false);
    $('#sent_date').val(moment(new Date()).format('DD.MM.YYYY'));
    $('#payment-form').find('textarea').val('');
    $('#user_payment').text(total);
}

function sumChange(diff, currencyName, currencyID, total) {
    let currencies = $('#new_payment_rate'),
        payment = $('#new_payment_sum'),
        curr;
    $('#close_sum').text(`${diff} ${currencyName}`);
    currencies.on('keyup', _.debounce(function () {
        if (currencyID != 2) {
            curr = $(this).val();
            let uah = Math.round(diff * curr);
            payment.val(uah);
            $('#user_payment').text(`${+diff + +total} ${currencyName}`);
        }
    }, 500));
    payment.on('keyup', _.debounce(function () {
        if (currencyID != 2) {
            let pay = $(this).val();
            curr = currencies.val();
            let result = Math.round(pay / curr);
            $('#user_payment').text(`${result + +total} ${currencyName}`);
        } else {
            let pay = $(this).val();
            $('#user_payment').text(`${+pay + +total} ${currencyName}`);
        }
    }, 500));
    if (currencyID == 2) {
        currencies.val('1.0').prop('readonly', true);
        payment.val(diff);
        $('#user_payment').text(`${diff + total} ${currencyName}`);
    }
}