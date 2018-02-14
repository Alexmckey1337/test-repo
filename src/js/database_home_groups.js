'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import URLS from './modules/Urls/index';
import getData, {deleteData} from './modules/Ajax/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index";
import {updateLeaderSelect} from "./modules/GetList/index";
import {addHomeGroup, saveHomeGroups, clearAddHomeGroupData, createHomeGroupsTable} from "./modules/HomeGroup/index";
import {makePastorList} from "./modules/MakeList/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import parseUrlQuery from './modules/ParseUrl/index';

$('document').ready(function () {
    const PATH = window.location.href.split('?')[1],
          $churchSelect = $('#added_home_group_church_select'),
          urlHGliders = URLS.home_group.leaders(),
          urlChurch = URLS.church.for_select();
    let $departmentSelect = $('#department_select'),
        init = false,
        $departmentsFilter = $('#department_id_filter'),
        $churchFilter = $('#church_filter'),
        $treeFilter = $('#master_tree_filter'),
        $liderFilter = $('#leader_filter');

    function initFilterAfterParse(set) {
        $departmentsFilter.val(set.department_id).trigger('change');
        (async () => {
            if (set.department_id) {
                await getData(`${urlChurch}?department_id=${set.department_id}`).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
                    return data;
                });
            }
            if (set.church) {
                $churchFilter.val(set.church).trigger('change');
                await getData(urlHGliders, {church: set.church}).then(data => {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $treeFilter.html('<option value="">ВСЕ</option>').append(pastors);
                    return data;
                })
            }
            if (set.master_tree) {
                $treeFilter.val(set.master_tree).trigger('change');
                await getData(urlHGliders, {master_tree: set.master_tree}).then(data => {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $liderFilter.html('<option value="">ВСЕ</option>').append(pastors);
                    return data;
                });
            } else {
                await getData(urlHGliders).then(res => {
                    const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $liderFilter.html('<option value="">ВСЕ</option>').append(leaders);
                    return res;
                });
            }
            (set.leader) && ($liderFilter.val(set.leader).trigger('change'));
            for (let [key, value] of Object.entries(set)) {
                $('#filterPopup').find(`input[data-filter="${key}"]`).val(value);
            }
            $('.apply-filter').trigger('click');
            filterChange();
        })();
    }

    function filterInit(set = null) {
        if (!init) {
            if (set != null) {
                initFilterAfterParse(set);
            } else {
                getData(urlHGliders).then(res => {
                    const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    // $('#master_tree_filter').html('<option value="">ВСЕ</option>').append(leaders);
                    $('#leader_filter').html('<option value="">ВСЕ</option>').append(leaders);
                });
            }
            init = true;
        }
    }

    if (PATH == undefined) {
        createHomeGroupsTable();
        filterChange();
    }

    $departmentSelect.select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
    $('#pastor_select').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
    $('.selectdb').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
    $('#search_opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $('#added_home_group_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    // Events
    $('#add').on('click', function () {
        clearAddHomeGroupData();
        updateLeaderSelect();
        setTimeout(function () {
            //$('#addHomeGroup').css('display', 'block');
            $('#addHomeGroup').addClass('active');
            $('.bg').addClass('active');
        }, 100);
    });

    if ($churchSelect) {
        $churchSelect.on('change', function () {
            updateLeaderSelect();
        });
    }

    $departmentSelect.on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id);
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createHomeGroupsTable, 'home_group');
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createHomeGroupsTable();
    }, 500));

    $('#export_table').on('click', function () {
        exportTableData(this);
    });

    //Filter
    $('#filter_button').on('click', function () {
        filterInit();
        //$('#filterPopup').css('display', 'block');
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });

    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createHomeGroupsTable);
    });

    function filterChange() {
        $departmentsFilter.on('change', function () {
            let departamentID = $(this).val(),
                config = {};
            if (!departamentID) {
                departamentID = null;
            } else {
                config.department_id = departamentID;
            }
            getData(urlChurch, config).then(data => {
                const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                $churchFilter.html('<option value="">ВСЕ</option>').append(churches);
            });
        });
        $churchFilter.on('change', function () {
            let churchID = $(this).val();
            let config = {};
            if (churchID) {
                config.church = churchID;
            }
            getData(urlHGliders, config).then(data => {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $treeFilter.html('<option value="">ВСЕ</option>').append(pastors);
                $liderFilter.html('<option value="">ВСЕ</option>').append(pastors);
            });
        });
        $treeFilter.on('change', function () {
            let masterTreeID = $(this).val();
            let config = {};
            if (masterTreeID) {
                config = {
                    master_tree: masterTreeID
                }
            }
            getData(urlHGliders, config).then(data => {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $liderFilter.html('<option value="">ВСЕ</option>').append(pastors);
            });
        });
    }

    $('#added_home_group_church_select').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });

    $('.save-group').on('click', function () {
        saveHomeGroups(this, createHomeGroupsTable);
    });

    $('#addHomeGroup').find('form').on('submit', function (event) {
        addHomeGroup(event, this, createHomeGroupsTable);
    });

    $('#delete-hg').on('click', function (e) {
        e.preventDefault();
        let id = parseInt($('#homeGroupsID').val());
        showConfirm('Удаление', 'Вы действительно хотите удалить данную дом. группу?', function () {
            deleteData(URLS.home_group.detail(id)).then(() => {
                showAlert('Домашняя группа успешно удалена!');
                $('#quickEditCartPopup').removeClass('active');
                $('.bg').removeClass('active');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                createHomeGroupsTable({page: page});
            }).catch((error) => {
                let errKey = Object.keys(error),
                    html = errKey.map(errkey => `${error[errkey]}`);
                if (error.can_delete === 'true') {
                    let msg = `${html[0]} Все равно удалить?`;
                    showConfirm('Подтверждение удаления', msg, function () {
                        let force = JSON.stringify({"force": true});
                        deleteData(URLS.home_group.detail(id), {body: force}).then(() => {
                            showAlert('Домашняя группа успешно удалена!');
                            $('#quickEditCartPopup').removeClass('active');
                            $('.bg').removeClass('active');
                            $('.preloader').css('display', 'block');
                            let page = $('.pagination__input').val();
                            createHomeGroupsTable({page: page});
                        }).catch((error) => {
                            showAlert('При удалении сделки произошла ошибка');
                            console.log(error);
                        });
                    }, () => {
                    });
                } else {
                    showAlert(html[0], 'Ошибка');
                }
            });
        }, () => {
        });
    });

    //Parsing URL
    if (PATH != undefined) {
        let filterParam = parseUrlQuery();
        console.log(filterParam);
        filterInit(filterParam);
    }

});