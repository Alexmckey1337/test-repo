'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import moment from 'moment/min/moment.min.js';
import URLS from './modules/Urls/index';
import getData, {postData} from './modules/Ajax/index';
import parseUrlQuery from './modules/ParseUrl/index';
import updateSettings from './modules/UpdateSettings/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {
    ChurchReportsTable,
    churchReportsTable,
    sendReport,
    deleteReport,
    calcTransPayments
} from "./modules/Reports/church";
import reverseDate from './modules/Date/index';
import errorHandling from './modules/Error';
import {convertNum} from "./modules/ConvertNum/index";

$('document').ready(function () {
    const USER_ID = $('body').data('user'),
        urlPastors = URLS.church.available_pastors(),
        urlChurch = URLS.church.for_select();
    let dateReports = new Date(),
        thisMonday = (moment(dateReports).day() === 1) ? moment(dateReports).format('DD.MM.YYYY') : (moment(dateReports).day() === 0) ? moment(dateReports).subtract(6, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).format('DD.MM.YYYY'),
        thisSunday = (moment(dateReports).day() === 0) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(7).format('DD.MM.YYYY'),
        lastMonday = (moment(dateReports).day() === 1) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).subtract(7, 'days').format('DD.MM.YYYY'),
        lastSunday = (moment(dateReports).day() === 0) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(7).subtract(7, 'days').format('DD.MM.YYYY'),
        $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#tree_filter'),
        $pastorFilter = $('#pastor_filter'),
        $churchFilter = $('#church_filter'),
        init = false,
        path = window.location.href.split('?')[1];

    function initFilterAfterParse(set) {
        if (set.from_date && set.to_date) {
            $('.tab-home-stats').find('.week').removeClass('active');
            $('.set-date').find('input').val(`${reverseDate(set.from_date, '.')}-${reverseDate(set.to_date, '.')}`);
        } else {
            $('.tab-home-stats').find('.week').removeClass('active');
            $('.tab-home-stats').find('.week_all').addClass('active');
            $('.set-date').find('input').val('');
        }
        if (set.is_submitted) {
            $('#statusTabs').find('li').removeClass('current');
            $('#statusTabs').find(`button[data-is_submitted='${set.is_submitted}']`).parent().addClass('current');
        }
        $departmentsFilter.val(set.department).trigger('change');
        (async () => {
            if (set.department) {
                let config = {
                    department_id: set.department
                };
                await getData(urlPastors, config).then(data => {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(pastors);
                    $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
                    return data;
                });
                await getData(urlChurch, config).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
                    return data;
                });
            } else {
                let config = {
                    master_tree: USER_ID,
                };
                await getData(urlPastors, config).then(data => {
                    const leaders = data.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                    $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                    return data;
                });
                await getData(urlChurch).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
                    return data;
                });
            }
            if (set.master_tree) {
                $treeFilter.val(set.master_tree).trigger('change');
                let config = {
                    master_tree: set.master_tree
                };
                await getData(urlPastors, config).then(function (data) {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
                    return data;
                });
                await getData(urlChurch, config).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
                    return data;
                });
            }
            if (set.pastor) {
                $pastorFilter.val(set.pastor).trigger('change');
                let config = {
                    pastor_id: set.pastor
                };
                await getData(urlChurch, config).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
                    return data;
                });
            }
            (set.church) && $churchFilter.val(set.church).trigger('change');
            (set.payment_status) && $('#payment_status').val(set.payment_status).trigger('change');
            $('.apply-filter').trigger('click');
            filterChange();
        })();
    }

    function filterInit(set = null) {
        if (!init) {
            if (set != null) {
                initFilterAfterParse(set);
            } else {
                let config = {
                    master_tree: USER_ID,
                };
                getData(urlPastors, config).then(res => {
                    const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                    $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                getData(urlChurch).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
                });
            }
            init = true;
        }
    }

    if (path === undefined) {
        ChurchReportsTable();
        filterChange();
    }

    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').css('display', 'block');
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
        churchReportsTable();
    });
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });
    $('#date_range').datepicker({
        dateFormat: 'dd.mm.yyyy',
        range: true,
        autoClose: true,
        multipleDatesSeparator: '-',
        onSelect: function (date) {
            if (date.length > 10) {
                $('.preloader').css('display', 'block');
                churchReportsTable();
                $('.tab-home-stats').find('.week').removeClass('active');
            }
        }
    });

    $('.tab-home-stats').find('.week').on('click', function () {
        $('.preloader').css('display', 'block');
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('week_now')) {
            $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
        } else if ($(this).hasClass('week_prev')) {
            $('.set-date').find('input').val(`${lastMonday}-${lastSunday}`);
        } else {
            $('.set-date').find('input').val('');
        }
        churchReportsTable();
    });

     $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        churchReportsTable();
    }, 500));

    $('.selectdb').select2();

     $('#delete_report').on('click', function (e) {
        e.preventDefault();
        let page = $('.pagination__input').val();
        deleteReport(churchReportsTable.bind(this, {page}));
    });

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(churchReportsTable, 'church_report');
    });

    //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, churchReportsTable)
    });

    // $('#departments_filter').on('change', function () {
    //     let department_id = parseInt($('#departments_filter').val());
    //     makePastorList(department_id, '#pastor_filter');
    // });

    function filterChange() {
        $departmentsFilter.on('change', function () {
            let departamentID = $(this).val(),
                config = {};
            if (!departamentID) {
                departamentID = null;
            } else {
                config.department_id = departamentID;
            }
            getData(urlPastors, config).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(pastors);
                $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
            });
            getData(urlChurch, config).then(data => {
                const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
            });
        });

        $treeFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.master_tree = $(this).val();
            }
            getData(urlPastors, config).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
            });
            getData(urlChurch, config).then(data => {
                const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
            });
        });

        $pastorFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.pastor_id = $(this).val();
            }
            getData(urlChurch, config).then(data => {
                const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
            });
        });
    }

    $("#popup-create_payment .top-text span").on('click', () => {
        $('#new_payment_sum').val('');
        $('#popup-create_payment textarea').val('');
        $('#popup-create_payment').css('display', 'none');
    });

    $("#close-payment").on('click', function (e) {
        e.preventDefault();
        $('#new_payment_rate').val(1);
        $('#in_user_currency').text('');
        $('#popup-create_payment').css('display', 'none');
    });

    $('#payment-form').on('submit', function (e) {
        e.preventDefault();
    });

    $('#sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

    $.validate({
        lang: 'ru',
        form: '#chReportForm',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            sendReport();

            return false;
        }
    });

    function submitPayment() {
        let id = $('#complete-payment').attr('data-id'),
            data = {
                "sum": convertNum($('#new_payment_sum').val(), '.'),
                "description": $('#popup-create_payment textarea').val(),
                "rate": convertNum($('#new_payment_rate').val(), '.'),
                "sent_date": $('#sent_date').val().split('.').reverse().join('-'),
                "operation": $('#operation').val()
            };
        postData(URLS.event.church_report.create_uah_payment(id), data).then(() => {
            churchReportsTable();
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#popup-create_payment').css('display', 'none');
            showAlert('Оплата прошла успешно.');
            $('#complete-payment').prop('disabled', false);
        }).catch(err => {
            errorHandling(err);
            $('#complete-payment').prop('disabled', false);
        });
    }

    $.validate({
        lang: 'ru',
        form: '#payment-form',
        onError: function () {
            showAlert(`Введены некорректные данные либо заполнены не все поля`)
        },
        onSuccess: function () {
            submitPayment();
            $('#complete-payment').prop('disabled', true);

            return false;
        }
    });

    calcTransPayments();
});
