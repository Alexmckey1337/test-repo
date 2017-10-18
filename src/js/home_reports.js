'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import moment from 'moment/min/moment.min.js';
import URLS from './modules/Urls/index';
import getData from './modules/Ajax/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import getSearch from './modules/Search/index';
import {getFilterParam, getTabsFilterParam} from "./modules/Filter/index";
import parseUrlQuery from './modules/ParseUrl/index';
import {HomeReportsTable, homeReportsTable} from "./modules/Reports/home_group";
import updateSettings from './modules/UpdateSettings/index';
import reverseDate from './modules/Date/index';

$('document').ready(function () {
    let dateReports = new Date(),
        thisMonday = (moment(dateReports).day() === 1) ? moment(dateReports).format('DD.MM.YYYY') : (moment(dateReports).day() === 0) ? moment(dateReports).subtract(6, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).format('DD.MM.YYYY'),
        thisSunday = (moment(dateReports).day() === 0) ? moment(dateReports).format('DD.MM.YYYY') : moment(dateReports).day(7).format('DD.MM.YYYY'),
        lastMonday = (moment(dateReports).day() === 1) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(1).subtract(7, 'days').format('DD.MM.YYYY'),
        lastSunday = (moment(dateReports).day() === 0) ? moment(dateReports).subtract(7, 'days').format('DD.MM.YYYY') : moment(dateReports).day(7).subtract(7, 'days').format('DD.MM.YYYY'),
        $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#master_tree_filter'),
        $churchFilter = $('#church_filter'),
        $homeGroupFilter = $('#home_group_filter'),
        $liderFilter = $('#masters_filter');
    const USER_ID = $('body').data('user'),
        urlPastors = URLS.church.available_pastors(),
        urlChurches = URLS.church.for_select(),
        urlHGleaders = URLS.home_group.leaders(),
        urlHG = URLS.home_group.for_select();
    $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
    let configData = {
            from_date: reverseDate(thisMonday, '-'),
            to_date: reverseDate(thisSunday, '-'),
        },
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
        if (set.type) {
            $('#tabs').find('li').removeClass('active');
            $('#tabs').find(`button[data-id='${set.type}']`).parent().addClass('active');
        } else {
            $('#tabs').find('li').removeClass('active');
            $('#tabs').find(`button[data-id='0']`).parent().addClass('active');
        }
        if (set.status) {
            $('#statusTabs').find('li').removeClass('current');
            $('#statusTabs').find(`button[data-status='${set.status}']`).parent().addClass('current');
        }
        $departmentsFilter.val(set.department).trigger('change');
        (async () => {
            if (set.department) {
                let config = {
                        department: set.department
                    },
                    config2 = {
                        department_id: set.department
                    };
                await getData(urlPastors, config2).then(function (res) {
                    const pastors = res.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(pastors);
                    return res;
                });
                await getData(urlChurches, config2).then(res => {
                    let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                    return res;
                });
                await getData(urlHG, config2).then(res => {
                    let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                    return res;
                });
                await getData(urlHGleaders, config).then(res => {
                    let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                    return res;
                });
            } else {
                let config = {
                    master_tree: USER_ID
                };
                await getData(urlPastors, config).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                    return res;
                });
                await getData(urlChurches).then(res => {
                    let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                    return res;
                });
                await getData(urlHG).then(res => {
                    let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                    return res;
                });
                await getData(urlHGleaders).then(res => {
                    let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                    return res;
                });
            }
            if (set.master_tree) {
                $treeFilter.val(set.master_tree).trigger('change');
                let config = {
                    master_tree: set.master_tree
                };
                await getData(urlChurches, config).then(res => {
                    let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                    return res;
                });
                await getData(urlHG, config).then(res => {
                    let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                    return res;
                });
                await getData(urlHGleaders, config).then(res => {
                    let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                    return res;
                });
            }
            if (set.church) {
                $churchFilter.val(set.church).trigger('change');
                let config = {
                        church: set.church
                    },
                    config2 = {
                        church_id: set.church
                    };
                await getData(urlHG, config2).then(res => {
                    let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                    return res;
                });
                await getData(urlHGleaders, config).then(res => {
                    let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                    return res;
                });
            }
            if (set.owner) {
                $liderFilter.val(set.owner).trigger('change');
                let config = {
                    leader_id: set.owner
                };
                await getData(urlHG, config).then(res => {
                    let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                    return res;
                });
            }
            $homeGroupFilter.val(set.home_group).trigger('change');
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
                    master_tree: USER_ID
                };
                getData(urlPastors, config).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                getData(urlChurches).then(res => {
                    let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                    $churchFilter.html('<option>ВСЕ</option>').append(churches);
                });
                getData(urlHG).then(res => {
                    let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                    $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
                });
                getData(urlHGleaders).then(res => {
                    let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                    $liderFilter.html('<option>ВСЕ</option>').append(liders);
                });
            }
            init = true;
        }
    }

    if (path == undefined) {
        HomeReportsTable(configData);
        filterChange();
    }

    // Events
    let $statusTabs = $('#statusTabs');
    $statusTabs.find('button').on('click', function () {
        $('.preloader').css('display', 'block');
        let status = $(this).attr('data-status');
        let config = {
            status: status
        };
        Object.assign(config, getFilterParam());
        Object.assign(config, getSearch('search_title'));
        Object.assign(config, getTabsFilterParam());
        HomeReportsTable(config);
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
                $('#filterPopup').css('display', 'block');
                homeReportsTable();
                $('.tab-home-stats').find('.week').removeClass('active');
            }
        }
    });

    $('.selectdb').select2();

    // Sort table
    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(HomeReportsTable);
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
        $('.preloader').css('display', 'block');
        homeReportsTable();
    }, 500));

    $('.tab-home-stats').find('.type').on('click', function () {
        $(this).closest('#tabs').find('li').removeClass('active');
        $(this).parent().addClass('active');
        homeReportsTable();
    });

    $('.tab-home-stats').find('.week').on('click', function () {
        $(this).closest('.tab-home-stats').find('.week').removeClass('active');
        $(this).addClass('active');
        if ($(this).hasClass('week_now')) {
            $('.set-date').find('input').val(`${thisMonday}-${thisSunday}`);
        } else if ($(this).hasClass('week_prev')) {
            $('.set-date').find('input').val(`${lastMonday}-${lastSunday}`);
        } else {
            $('.set-date').find('input').val('');
        }
        homeReportsTable();
    });

    //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, homeReportsTable);
    });

    function filterChange() {
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
            getData(urlPastors, config2).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $treeFilter.html('<option>ВСЕ</option>').append(pastors);
            });
            getData(urlChurches, config2).then(res => {
                let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
            getData(urlHG, config2).then(res => {
                let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
            });
            getData(urlHGleaders, config).then(res => {
                let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                $liderFilter.html('<option>ВСЕ</option>').append(liders);
            });
        });

        $treeFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.master_tree = $(this).val();
            }
            getData(urlChurches, config).then(res => {
                let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
                $churchFilter.html('<option>ВСЕ</option>').append(churches);
            });
            getData(urlHG, config).then(res => {
                let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
            });
            getData(urlHGleaders, config).then(res => {
                let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                $liderFilter.html('<option>ВСЕ</option>').append(liders);
            });
        });

        $churchFilter.on('change', function () {
            let config = {},
                config2 = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.church = $(this).val();
                config2.church_id = $(this).val();
            }
            getData(urlHG, config2).then(res => {
                let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
            });
            getData(urlHGleaders, config).then(res => {
                let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
                $liderFilter.html('<option>ВСЕ</option>').append(liders);
            });
        });

        $liderFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config.leader_id = $(this).val();
            }
            getData(urlHG, config).then(res => {
                let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
                $homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
            });
        });
    }

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        console.log(filterParam);
        filterInit(filterParam);
    }
});
