'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import moment from 'moment/min/moment.min.js';
import parseUrlQuery from './modules/ParseUrl/index';
import getSearch from './modules/Search/index';
import {getFilterParam} from "./modules/Filter/index"
import {getPastorsByDepartment, getChurchesListINDepartament, getChurches} from "./modules/GetList/index";
import updateSettings from './modules/UpdateSettings/index';
import {showAlert} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {ChurchReportsTable, churchReportsTable} from "./modules/Reports/church";
import {createChurchPayment} from "./modules/Reports/church";

$('document').ready(function () {
    let dateReports = new Date(),
        thisMonday = (moment(dateReports).day() === 1) ? moment(dateReports).format('DD.MM.YYYY') : (moment(dateReports).day() === 0) ? moment(dateReports).subtract(6, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).format('DD.MM.YYYY'),
        thisSunday = (moment(dateReports).day() === 0) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(7).format('DD.MM.YYYY'),
        lastMonday = (moment(dateReports).day() === 1) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).subtract(7, 'days').format('DD.MM.YYYY'),
        lastSunday = (moment(dateReports).day() === 0) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(7).subtract(7, 'days').format('DD.MM.YYYY'),
        $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#tree_filter'),
        $pastorFilter = $('#pastor_filter'),
        $churchFilter = $('#church_filter');
    const USER_ID = $('body').data('user');
    $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
    let configData = {
        from_date: thisMonday.split('.').reverse().join('-'),
        to_date: thisSunday.split('.').reverse().join('-')
    },
        init = false,
        path = window.location.href.split('?')[1];

    function filterInit(pastorID=null) {
        if (!init) {
            getPastorsByDepartment({
                master_tree: USER_ID
            }).then(res => {
                let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                if (pastorID != null) {
                    $pastorFilter.find(`option[value='${pastorID}']`).prop('selected', true).trigger('change');
                    $('.apply-filter').trigger('click');
                }
            });
            getChurchesListINDepartament().then(res => {
                let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
            init = true;
        }
    }

    (path == undefined) && ChurchReportsTable(configData);

    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').css('display', 'block');
        let status = $(this).data('status');
        let config = {
            status: status
        };
        Object.assign(config, getFilterParam());
        Object.assign(config, getSearch('search_title'));
        ChurchReportsTable(config);
        $statusTabs.find('li').removeClass('current');
        $(this).closest('li').addClass('current');
    });
    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
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

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(ChurchReportsTable);
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

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {},
            config2 = {};
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
            config2.department_id = departamentID;
        }
        getPastorsByDepartment(config2).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(pastors);
                $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
            });

        getChurchesListINDepartament(departamentID).then(res => {
                    let churches = res.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
    });

    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config.master_tree = $(this).val();
        }

        getPastorsByDepartment(config).then(function (data) {
             const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
        });
        getChurches(config).then(res => {
                    let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
    });

    $pastorFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config.pastor = $(this).val();
        }
        getChurches(config).then(res => {
            let churches = res.results.map(church=> `<option value="${church.id}">${church.get_title}</option>`);
            $churchFilter.html('<option>ВСЕ</option>').append(churches);
        });
    });

        //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        $('.week').removeClass('active');
        $('.week_all').addClass('active');
        $('#date_range').val('');
        $('#statusTabs').find('li').removeClass('current');
        $('#statusTabs').find(`button[data-status='${filterParam.type}']`).parent().addClass('current');
        filterInit(filterParam.pastor);
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

    $('#complete-payment').on('click', _.debounce(function (e) {
        e.preventDefault();
        $(this).prop('disabled', true);
        let id = $(this).attr('data-id'),
            sum = $('#new_payment_sum').val(),
            description = $('#popup-create_payment textarea').val();
        createChurchPayment(id, sum, description).then(() => {
            churchReportsTable();
            $('#new_payment_sum').val('');
            $('#popup-create_payment textarea').val('');
            $('#popup-create_payment').css('display', 'none');
            showAlert('Оплата прошла успешно.');
            $('#complete-payment').prop('disabled', false);
        }).catch((res) => {
            let error = JSON.parse(res.responseText),
                errKey = Object.keys(error),
                html = errKey.map(errkey => `${error[errkey].map(err => `<span>${JSON.stringify(err)}</span>`)}`);
            $('#complete-payment').prop('disabled', false);
            showAlert(html);
        });
    }, 500));

    $('#sent_date').datepicker({
        dateFormat: "dd.mm.yyyy",
        startDate: new Date(),
        maxDate: new Date(),
        autoClose: true
    });
});
