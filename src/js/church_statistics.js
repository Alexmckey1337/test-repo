'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import * as moment from 'moment';
import 'moment/locale/ru';
import URLS from './modules/Urls/index';
import getData from './modules/Ajax/index';
import parseUrlQuery from './modules/ParseUrl/index';
import {churchStatistics} from "./modules/Statistics/church";
import {regLegendPlagin} from "./modules/Chart/config";

$('document').ready(function () {
    const USER_ID = $('body').data('user'),
        urlPastors = URLS.church.available_pastors(),
        urlChurch = URLS.church.for_select(),
        today = moment().format('MMMM YYYY');
    let $treeFilter = $('#tree_filter'),
        $pastorFilter = $('#pastor_filter'),
        $churchFilter = $('#church_filter'),
        init = false,
        path = window.location.href.split('?')[1],
        year = moment().year(),
        month = ("0" + (moment().month() + 1)).slice(-2),
        dateInterval = `m:${year}${month}`;

    regLegendPlagin();

    moment.locale('ru');

    $('#calendar_range').datepicker({
        autoClose: true,
        view: 'months',
        minView: 'months',
        dateFormat: 'MM yyyy',
        maxDate: new Date(),
        onSelect: function (formattedDate, date) {
            if (!date) return;
            let year = moment(date).year(),
                month = ("0" + (moment(date).month() + 1)).slice(-2),
                dateInterval = `m:${year}${month}`;
            $('#calendar_range').attr('data-interval', dateInterval);
            $('.tab-status ').find('.range').removeClass('active');
            churchStatistics(true);
        }
    }).val(today).attr('data-interval', dateInterval);

    function initFilterAfterParse(set) {
        if (set.last) {
            $('.tab-home-stats').find('.range').removeClass('active');
            $('.tab-home-stats').find(`.range[data-range='${set.last}']`).addClass('active');
        }
        if (set.interval) {
            let year = set.interval.slice(2, 6),
                month = set.interval.slice(6),
                date = moment(`${+month}-${+year}`, "MM-YYYY").format('MMMM YYYY');

            console.log(year, month, date);
            $('#calendar_range').attr('data-interval', set.interval).val(date);
        }
        (async () => {
            if (set.pastor_tree) {
                $treeFilter.val(set.pastor_tree).trigger('change');
                let config = {
                    master_tree: set.pastor_tree
                };
                await getData(urlPastors, config).then(function (data) {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $pastorFilter.html('<option value="ВСЕ">ВСЕ</option>').append(pastors);

                    return data;
                });
                await getData(urlChurch, config).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="ВСЕ">ВСЕ</option>').append(churches);

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
                    $churchFilter.html('<option value="ВСЕ">ВСЕ</option>').append(churches);

                    return data;
                });
            }
            (set.church) && $churchFilter.val(set.church).trigger('change');
            churchStatistics();
            filterChange();
        })();
    }

    function filterInit(set = null) {
        if (!init) {
            let config = {
                master_tree: USER_ID,
            };
            (async () => {
                await getData(urlPastors, config).then(res => {
                    const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option value="ВСЕ">ВСЕ</option>').append(leaders);
                    $pastorFilter.html('<option value="ВСЕ">ВСЕ</option>').append(leaders);

                    return res;
                });
                await getData(urlChurch).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="ВСЕ">ВСЕ</option>').append(churches);

                    return data;
                });
                (set != null) && initFilterAfterParse(set);
                init = true;
            })();
        }
    }

    if (path === undefined) {
        churchStatistics();
        filterInit();
        filterChange();
    }

    $('.tab-home-stats').find('.range').on('click', function () {
        $(this).closest('.tab-home-stats').find('.range').removeClass('active');
        $(this).addClass('active');
        $('#calendar_range').val('');
        churchStatistics(true);
    });

    $('.selectdb').select2();

    function filterChange() {
        $treeFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.master_tree = $(this).val();
            }
            (async () => {
                await getData(urlPastors, config).then(function (data) {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $pastorFilter.html('<option value="ВСЕ">ВСЕ</option>').append(pastors);

                    return data;
                });
                await getData(urlChurch, config).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="ВСЕ">ВСЕ</option>').append(churches);

                    return data;
                });
                churchStatistics(true);
            })();
        });

        $pastorFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.pastor_id = $(this).val();
            }
            (async () => {
                await getData(urlChurch, config).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="ВСЕ">ВСЕ</option>').append(churches);

                    return data;
                });
                churchStatistics(true);
            })();
        });

        $churchFilter.on('change', function () {
            churchStatistics(true);
        });
    }

    $('.resetFilter').on('click',function () {
        $treeFilter.val('ВСЕ').trigger('change');
    });

    $('#tab_currency').on('click', 'button', function () {
        $('#tab_currency').find('button').removeClass('active');
        $(this).addClass('active');
        churchStatistics(true);
    });

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        console.log(filterParam);
        filterInit(filterParam);
    }

});
