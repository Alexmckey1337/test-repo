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

    init();

    $('input[name=fullsearch]').on('keyup', function () {
        let config = {};
        config.search = $(this).val();
        getExpiredDeals(config);
        getDoneDeals(config);
        getUndoneDeals(config);
    });

    function sumCurrency(sum, operation, rate, currencyEl, currencyName) {
        let userPay;
        if (operation == "*") {
            userPay = parseFloat(sum) * parseFloat(rate);
        } else if (operation == "/") {
            userPay = parseFloat(sum) * (1 / parseFloat(rate));
        }
        currencyEl.text(parseInt(userPay) + currencyName);
    }

    let sumChangeListener = (function () {
        let $form = $('#payment-form');
        let currencyID, currencyName, new_payment_sum, new_payment_rate, operation;
        let $currencies = $form.find('#new_payment_currency');
        let $currencyOptions = $currencies.find('option');
        let $operation = $form.find('#operation');
        let $operationLabel = $form.find('label[for="operation"]');
        let $newPaymentSumEl = $form.find('#new_payment_sum');
        let $newPaymentRateEl = $form.find('#new_payment_rate');
        let $inUserCurrencyEl = $form.find('#in_user_currency');

        $operationLabel.on('click', function () {
            let operation = $operation.val();
            let newOperation = (operation == '*') ? '/' : '*';
            $operation.val(newOperation);
            operation = newOperation;
            new_payment_rate = $newPaymentRateEl.val();
            new_payment_sum = $newPaymentSumEl.val();
            sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        });
        $currencies.on('change', function () {
            if ($(this).val() != currencyID) {
                $('#new_payment_rate').prop('readonly', false);
            } else {
                $('#new_payment_rate').prop('readonly', true).val('1.000').trigger('change');
            }
        });
        $form.on('keypress', function (e) {
            return e.keyCode != 13;
        });

        $newPaymentSumEl.on('change', function () {
            new_payment_sum = $newPaymentSumEl.val();
            operation = $operation.val();
            sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        });

        $newPaymentSumEl.on('keypress', function (e) {
            if (e.keyCode == 13) {
                new_payment_sum = $newPaymentSumEl.val();
                operation = $operation.val();
                sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
            }
        });
        $newPaymentRateEl.on('change', function () {
            new_payment_rate = $newPaymentRateEl.val();
            sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        });
        $newPaymentRateEl.on('keypress', function (e) {
            if (e.keyCode == 13) {
                new_payment_rate = $newPaymentRateEl.val();
                operation = $operation.val();
                sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
            }
        });
        // $operation.on('change', function () {
        //     operation = $operation.val();
        //     new_payment_rate = $newPaymentRateEl.val();
        //     new_payment_sum = $newPaymentSumEl.val();
        //     sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        // });
        return function (currency_name, currency_id) {
            currencyID = currency_id;
            currencyName = currency_name;
            new_payment_sum = $newPaymentSumEl.val();
            new_payment_rate = $newPaymentRateEl.val();
            operation = $operation.val();
            $currencyOptions.each(function () {
                $(this).prop('selected', false);
                if ($(this).val() == currencyID) {
                    $(this).prop('selected', true);
                }
            });
            $form.find('#new_payment_rate').val('1.000');

            $('#new_payment_rate').prop('readonly', true);
            sumCurrency(new_payment_sum, operation, new_payment_rate, $inUserCurrencyEl, currencyName);
        }

    })();

    $("#close-payment").on('click', function (e) {
        e.preventDefault();
        $('#new_payment_rate').val(1);
        $('#in_user_currency').text('');
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

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
        let id = $(this).find('button[type="submit"]').attr('data-id'),
            sum = $('#new_payment_sum').val(),
            description = $('#popup-create_payment textarea').val();
        let data = $(this).serializeArray();
        createPayment(id, sum, description).then(function () {
            $('#' + id + ' > .rows').css({
                'background-color': '#dfedd6',
                'border-color': '#aedd94',
            });
        });
        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', 'none');
    });
    $('#show-all-expired').on('click', function () {
        $('#expired_datepicker_from').val();
        $('#expired_datepicker_to').val();
    });
    $('#complete').on('click', function () {
        let id = $(this).attr('data-id'),
            description = $('#deal-description').val();
        updateDeals(id, description);
    });

    function updateDeals(id, description) {
        let data = {
            "done": true,
            "description": description
        };
        let config = JSON.stringify(data);
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/deals/' + id + '/', config, function () {
            init();
            document.getElementById('popup').style.display = '';
        }, 'PATCH', true, {
            'Content-Type': 'application/json'
        }, {
            403: function (data) {
                data = data.responseJSON;
                showPopup(data.detail);
            }
        });
    }

    function createPayment(id, sum, description) {
        return new Promise(function (resolve, reject) {
            let data = {
                "sum": sum,
                "description": description,
                "rate": $('#new_payment_rate').val(),
                "currency": $('#new_payment_currency').val(),
                "sent_date": $('#sent_date').val(),
                "operation": $('#operation').val()
            };
            let json = JSON.stringify(data);
            ajaxRequest(CONFIG.DOCUMENT_ROOT + `api/v1.0/deals/${id}/create_payment/`, json, function (JSONobj) {
                init();
                showPopup('Оплата прошла успешно.');
                setTimeout(function () {
                    resolve()
                }, 1500);
            }, 'POST', true, {
                'Content-Type': 'application/json'
            }, {
                403: function (data) {
                    data = data.responseJSON;
                    showPopup(data.detail);
                    reject();
                }
            });
        })
    }

    function showPayments(id) {
        getPayment(id).then(function (data) {
            let payments_table = '';
            let sum, date_time;
            data.forEach(function (payment) {
                sum = payment.effective_sum_str.replace('.000', '');
                date_time = payment.created_at;
                payments_table += `<tr><td>${sum}</td><td>${date_time}</td></tr>`
            });
            $('#popup-payments table').html(payments_table);
            $('#popup-payments').css('display', 'block');
        })
    }

    function getExpiredDeals(data) {
        let config = data || null;
        let search = document.getElementsByName('fullsearch')[0].value;
        if (search) {
            config.search = search;
        }
        getOverdueDeals(config).then(function (data) {
            let tmpl = document.getElementById('showDeals').innerHTML;
            let rendered = _.template(tmpl)(data);
            let count = data.count;
            $('#overdue-count').text(count);
            data = data.results;
            let page = config['page'] || 1,
                pages = Math.ceil(count / CONFIG.pagination_count);
            document.getElementById('overdue').innerHTML = rendered;
            let paginationConfig = {
                container: ".expired__pagination",
                currentPage: page,
                pages: pages,
                callback: getExpiredDeals
            };
            makePagination(paginationConfig);
            $('.show_payments').on('click', function () {
                let id = $(this).data('id');
                showPayments(id);
            });
            $("button.pay").on('click', function () {
                let id = $(this).data('id');
                let value = parseInt($(this).data('value'));
                let total_sum = parseInt($(this).data('total_sum'));
                let currencyName = $(this).data('currency-name');
                let currencyID = $(this).data('currency-id');
                let diff = value - total_sum;
                diff = diff > 0 ? diff : 0;
                $('#new_payment_sum').val(diff);
                $('#complete-payment').attr('data-id', id);
                $('#purpose-id').val(id);
                $('#popup-create_payment').css('display', 'block');
                sumChangeListener(currencyName, currencyID);
            });
            $("button.complete").on('click', function () {
                $('#complete').attr('data-id', $(this).data('id'));
                $('#popup').css('display', 'block');
            });

        })
    }

    function getDoneDeals(data) {
        let config = data || null;
        let search = document.getElementsByName('fullsearch')[0].value;
        if (search) {
            config.search = search;
        }
        getFinishedDeals(config).then(function (data) {
            let count = data.count;
            let tmpl = document.getElementById('showDeals').innerHTML;
            let rendered = _.template(tmpl)(data);
            let page = config['page'] || 1,
                pages = Math.ceil(count / CONFIG.pagination_count),
                html = '';
            let paginationConfig = {
                container: ".done__pagination",
                currentPage: page,
                pages: pages,
                callback: getDoneDeals
            };
            $('#completed-count').html(count);
            makePagination(paginationConfig);

            $('#completed').html(rendered);
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
            config.search = search;
        }
        getIncompleteDeals(config).then(function (data) {
            let tmpl = document.getElementById('showDeals').innerHTML;
            let rendered = _.template(tmpl)(data);
            let count = data.count;
            $('#incomplete-count').html(count);
            let page = config['page'] || 1,
                pages = Math.ceil(count / CONFIG.pagination_count);

            let paginationConfig = {
                container: ".undone__pagination",
                currentPage: page,
                pages: pages,
                callback: getUndoneDeals
            };
            makePagination(paginationConfig);

            document.getElementById('incomplete').innerHTML = rendered;

            $('.show_payments').on('click', function () {
                let id = $(this).data('id');
                showPayments(id);
            });
            $("button.pay").on('click', function () {
                let id = $(this).data('id');
                let value = $(this).data('value');
                let total_sum = $(this).data('total_sum');
                let diff = numeral(value).value() - numeral(total_sum).value();
                let currencyName = $(this).data('currency-name');
                let currencyID = $(this).data('currency-id');
                diff = diff > 0 ? diff : 0;
                $('#new_payment_sum').val(diff);
                $('#complete-payment').attr('data-id', id);
                $('#purpose-id').val(id);
                $('#popup-create_payment').css('display', 'block');
                sumChangeListener(currencyName, currencyID);
            });
            $("button.complete").on('click', function () {
                let client_name = $(this).attr('data-name'),
                    deal_date = $(this).attr('data-date'),
                    responsible_name = $(this).attr('data-responsible');
                $('#complete').attr('data-id', $(this).data('id'));
                $('#client-name').val(client_name);
                $('#deal-date').val(deal_date);
                $('#responsible-name').val(responsible_name);
                $('#popup').css('display', 'block');
            });
        })
    }

    function sortDoneDeals(from, to) {
        let config = {};
        config["to_date"] = to;
        config["from_date"] = from;
        getDoneDeals(config);
    }

    function sortExpiredDeals(from, to) {
        let config = {};
        config["to_date"] = to;
        config["from_date"] = from;
        getExpiredDeals(config);
    }

    $.datepicker.setDefaults($.datepicker.regional["ru"]);

    $("#done_datepicker_from").datepicker({
        dateFormat: "yyyy-mm-dd",
        maxDate: new Date(),
        autoClose: true,
        setDate: '-1m',
        onSelect: function (date) {
            let doneToDate = $('#done_datepicker_to').val();
            sortDoneDeals(date, doneToDate);
        }
    });

    $("#done_datepicker_to").datepicker({
        dateFormat: "yyyy-mm-dd",
        setDate: new Date(),
        autoClose: true,
        onSelect: function (date) {
            let doneFromDate = $('#done_datepicker_from').val();
            sortDoneDeals(doneFromDate, date);
        }
    });

    $("#expired_datepicker_from").datepicker({
        dateFormat: "yyyy-mm-dd",
        maxDate: new Date(),
        setDate: '-1m',
        autoClose: true,
        onSelect: function (date) {
            let expiredToDate = $('#expired_to_date').val();
            sortExpiredDeals(date, expiredToDate);
        }
    });

    $("#expired_datepicker_to").datepicker({
        dateFormat: "yy-mm-dd",
        maxDate: new Date(),
        setDate: '-1m',
        autoClose: true,
        onSelect: function (date) {
            let expiredFromDate = $('#expired_from_date').val();
            sortExpiredDeals(expiredFromDate, date);
        }
    });
    $('#sent_date').datepicker({
        dateFormat: "yyyy-mm-dd",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });
});

