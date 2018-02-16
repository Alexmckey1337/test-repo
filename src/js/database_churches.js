'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import getData from './modules/Ajax/index';
import URLS from './modules/Urls/index';
import {deleteData} from "./modules/Ajax/index";
import {createChurchesTable, clearAddChurchData, saveChurches, addChurch} from './modules/Church/index';
import {makePastorList} from './modules/MakeList/index';
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import parseUrlQuery from './modules/ParseUrl/index';

$('document').ready(function () {
    let $departmentsFilter = $('#department_filter'),
        $treeFilter = $('#master_tree_filter'),
        $pastorFilter = $('#pastor_filter'),
        init = false,
        pastorUrl = URLS.church.available_pastors();
    const USER_ID = $('body').data('user'),
          PATH = window.location.href.split('?')[1];

    function initFilterAfterParse(set) {
        $departmentsFilter.val(set.department).trigger('change');
        let config = {};
        if (set.department) {
            config.department = set.department;
        } else {
            config.master_tree = USER_ID;
        }
        (async () => {
            await getData(pastorUrl, config).then(res => {
                let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                (set.department) && $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                return res;
            });
            if (set.master_tree) {
                $treeFilter.val(set.master_tree).trigger('change');
                await getData(pastorUrl, {master_tree: set.master_tree}).then(data => {
                    const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                    $pastorFilter.html('<option>ВСЕ</option>').append(pastors);
                    return data;
                });
            }
            (set.pastor) && $pastorFilter.val(set.pastor).trigger('change');
            (set.is_open) && $('#is_open_filter').val(set.is_open).trigger('change');
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
                getData(pastorUrl, {
                    master_tree: USER_ID
                }).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    // $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                    $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                });
            }
            init = true;
        }
    }

    if (PATH == undefined) {
        createChurchesTable();
        filterChange();
    }

    $('.selectdb').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });

    $('#added_churches_date, #search_opening_date, #opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });

//    Events
    $('#add').on('click', function () {
        let department_id = parseInt($('#department_select').val());
        clearAddChurchData();
        makePastorList(department_id, '#pastor_select');
        setTimeout(function () {
            //$('#addChurch').css('display', 'block');
            $('#addChurch').addClass('active');
            $('.bg').addClass('active');
        }, 100);
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id, '#pastor_select');
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesTable, 'church');
    });

    $('#filter_button').on('click', function () {
        filterInit();
        //$('#filterPopup').css('display', 'block');
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createChurchesTable();
    }, 500));

    $('#export_table').on('click', function () {
        exportTableData(this);
    });

    //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createChurchesTable)
    });

    function filterChange() {
        $departmentsFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "")) {
                config = {
                    department_id: $(this).val()
                };
            }
            getData(pastorUrl, config).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $('#pastor_filter').html('<option>ВСЕ</option>').append(pastors);
                $('#master_tree_filter').html('<option>ВСЕ</option>').append(pastors);
            });
        });

        $treeFilter.on('change', function () {
            let config = {};
            if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
                config = {
                    master_tree: $(this).val()
                };
            }
            getData(pastorUrl, config).then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $('#pastor_filter').html('<option>ВСЕ</option>').append(pastors);
            });
        });
    }

    //Save churches
    $('#save_church').on('click', function () {
        saveChurches(this);
    });

    $('#addChurch').find('form').on('submit', function (event) {
        addChurch(event, this, createChurchesTable)
    });

    $('#delete-church').on('click', function (e) {
        e.preventDefault();
        let id = parseInt($('#churchID').val());
        showConfirm('Удаление', 'Вы действительно хотите удалить данную церковь?', function () {
            deleteData(URLS.church.detail(id)).then(() => {
                showAlert('Церковь успешно удалена!');
                $('#quickEditCartPopup').css('display', 'none');
                $('.preloader').css('display', 'block');
                let page = $('.pagination__input').val();
                createChurchesTable({page: page});
            }).catch((error) => {
                let errKey = Object.keys(error),
                    html = errKey.map(errkey => `${error[errkey]}`);
                showAlert(html[0], 'Ошибка');
            });
        }, () => {
        });
    });

    //Parsing URL
    if (PATH != undefined) {
        let filterParam = parseUrlQuery();
        filterInit(filterParam);
    }

});