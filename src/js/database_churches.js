'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import URLS from './modules/Urls/index';
import {deleteData} from "./modules/Ajax/index";
import {createChurchesTable, clearAddChurchData, saveChurches, addChurch} from './modules/Church/index';
import {makePastorList} from './modules/MakeList/index';
import {getPastorsByDepartment} from './modules/GetList/index';
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index";
import {applyFilter, refreshFilter} from "./modules/Filter/index";

$('document').ready(function () {
    let $departmentsFilter = $('#departments_filter'),
        $treeFilter = $('#tree_filter'),
        $pastorFilter = $('#pastor_filter'),
        init = false;
    const USER_ID = $('body').data('user'),
          PATH = window.location.href.split('?')[1];

    // function filterInit(set = null) {
    //     if (!init) {
    //         if (set != null) {
    //             $('#departments_filter').find(`option[value='${set.department_id}']`).prop('selected', true);
    //             $('.apply-filter').trigger('click');
    //         } else {
    //             getPastorsByDepartment({
    //                 master_tree: USER_ID
    //             }).then(res => {
    //                 let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
    //                 $treeFilter.html('<option>ВСЕ</option>').append(leaders);
    //                 $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
    //             });
    //         }
    //         init = true;
    //     }
    // }

    let filterInit = (function () {
        let init = false;
        const USER_ID = $('body').data('user');
        return function () {
            if (!init) {
                getPastorsByDepartment({
                    master_tree: USER_ID
                }).then(res => {
                    let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
                    $treeFilter.html('<option>ВСЕ</option>').append(leaders);
                    $pastorFilter.html('<option>ВСЕ</option>').append(leaders);
                });
                init = true;
            }
        }
    })();

    createChurchesTable();

    $('.selectdb').select2();

    $('#added_churches_date, #search_date_open, #opening_date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });

//    Events
    $('#add').on('click', function () {
        let department_id = parseInt($('#department_select').val());
        clearAddChurchData();
        makePastorList(department_id, '#pastor_select');
        setTimeout(function () {
            $('#addChurch').css('display', 'block');
        }, 100);
    });
    $('#department_select').on('change', function () {
        $('#pastor_select').prop('disabled', true);
        let department_id = parseInt($('#department_select').val());
        makePastorList(department_id, '#pastor_select');
    });

    $('#sort_save').on('click', function () {
        $('.preloader').css('display', 'block');
        updateSettings(createChurchesTable);
    });

    $('#filter_button').on('click', function () {
        filterInit();
        $('#filterPopup').css('display', 'block');
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

    $departmentsFilter.on('change', function () {
        let departamentID = $(this).val();
        let config = {
            level_gte: 2
        };
        if (!departamentID) {
            departamentID = null;
        } else {
            config.department = departamentID;
        }
        getPastorsByDepartment({
            department_id: departamentID
        })
            .then(function (data) {
                const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $('#pastor_filter').html('<option>ВСЕ</option>').append(pastors);
                $('#tree_filter').html('<option>ВСЕ</option>').append(pastors);
            });
    });

    $treeFilter.on('change', function () {
        let config = {};
        if ($(this).val() != "ВСЕ") {
            config = {
                master_tree: $(this).val()
            };
        }
        getPastorsByDepartment(config).then(function (data) {
             const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
                $('#pastor_filter').html('<option>ВСЕ</option>').append(pastors);
        });
    });

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
    // if (PATH != undefined) {
    //     let filterParam = parseUrlQuery();
    //     console.log(filterParam);
    //     filterInit(filterParam);
    // }

});