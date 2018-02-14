'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls/index';
import getData from './modules/Ajax/index';
import parseUrlQuery from './modules/ParseUrl/index';
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import {createUsersTable} from "./modules/Users/index";
import {saveUser, initAddNewUser} from "./modules/User/addUser";
import {createNewUser} from "./modules/User/addUser";

$('document').ready(function () {
    let $departmentsFilter = $('#department_filter'),
        $churchFilter = $('#church_id_filter'),
        $treeFilter = $("#master_tree_filter"),
        $partnerFilter = $('#is_partner_filter'),
        $masterFilter = $('#master_filter'),
        $hierarchyFilter = $('#hierarchy_filter'),
        urlChurch = URLS.church.for_select(),
        urlUserShort = URLS.user.short();
    const USER_ID = $('body').data('user'),
        path = window.location.href.split('?')[1];

    if (path == undefined) {
        createUsersTable({});
        filterChange();
    }

    $('.selectdb').select2().on('select2:open', function () {
        $('.select2-search__field').focus();
    });
    $('.select_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        selectOtherYears: false,
        showOtherYears: false,
        moveToOtherYearsOnSelect: false,
        minDate: new Date((new Date().getFullYear()), 0, 1),
        maxDate: new Date((new Date().getFullYear()), 11, 31),
        position: "left top",
        autoClose: true
    });

    $('.select_rep_date_filter').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
        position: "left top",
    });

    //Events
    $('#filter_button').on('click', function () {
        //$('#filterPopup').css('display', 'block');
        $('#filterPopup').addClass('active');
        $('.bg').addClass('active');
    });

    $('.pop_cont').on('click', function (e) {
        e.stopPropagation();
    });

    $('.editprofile').on('click', function (e) {
        e.stopPropagation();
    });

    $('input[name="fullsearch"]').on('keyup', _.debounce(function(e) {
        $('.preloader').css('display', 'block');
        createUsersTable({});
    }, 500));

    $('#sort_save').on('click', function () {
        updateSettings(createUsersTable, 'user');
    });

    $('#export_table').on('click', function () {
        exportTableData(this);
    });

    $('#quickEditCartPopup').find('.close').on('click', function () {
        let $input = $(this).closest('.pop_cont').find('input');
        let $select = $(this).closest('.pop_cont').find('select');
        let $button = $(this).closest('.pop_cont').find('.save-user');
        let $info = $(this).closest('.pop_cont').find('.info');
        $button.css('display', 'inline-block');
        $button.removeAttr('disabled');
        $button.text('Сохранить');
        $info.each(function () {
            $(this).css('display', 'none');
        });
        $input.each(function () {
            $(this).removeAttr('readonly');
        });
        $select.each(function () {
            $(this).removeAttr('disabled');
        });
    });

    $('#add').on('click', function () {
        $('body').addClass('no_scroll');
        //$('#addNewUserPopup').css('display', 'block');
        $('#addNewUserPopup').addClass('active');
        $('.bg').addClass('active');
        $(".editprofile-screen").animate({right: '0'}, 300, 'linear');
        initAddNewUser();
    });

    //Filter
    $('.clear-filter').on('click', function () {
        refreshFilter(this);
    });

    $('.apply-filter').on('click', function () {
        applyFilter(this, createUsersTable)
    });

    function filterChange() {
        $departmentsFilter.on('change', function () {
            let departamentID = $(this).val();
            let config = {
                    level_gte: 2
                },
                config2 = {};
            if (!departamentID) {
                departamentID = null;
            } else {
                config.department = departamentID;
                config2.department_id = departamentID;
            }
            getData(urlChurch, config2).then(data => {
                const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                $churchFilter.html('<option value="">ВСЕ</option><option value="any">ЛЮБАЯ</option><option value="nothing">НЕТ</option>')
                             .append(churches);
            });
            getData(urlUserShort, config).then(data => {
                const users = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
                $treeFilter.html('<option value="ВСЕ">ВСЕ</option>').append(users);
            });
        });
        // $churchFilter.on('change', function () {
        //     let churchID = $(this).val();
        //     let config = {};
        //     if (churchID) {
        //         config.church = churchID;
        //     }
        //     getData(urlHGliders, config).then(data => {
        //         const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
        //         $treeFilter.html('<option value="">ВСЕ</option>').append(pastors);
        //     });
        // });
        $treeFilter.on('change', function () {
            let config = {};
            if ($(this).val() != "ВСЕ") {
                config = {
                    master_tree: $(this).val()
                };
            }
            getData(urlUserShort, config).then(data => {
                const users = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
                $masterFilter.html('<option value="ВСЕ">ВСЕ</option>').append(users);
            });
        });
    }

    $('.save-user').on('click', function () {
        saveUser(this);
    });

    function filterInit(set) {
        $departmentsFilter.val(set.department).trigger('change');
        if (set.home_group_id) {
            $('#home_group_filter').val(set.home_group_id).trigger('change');
        }
        if (set.spiritual_level) {
            $('#spiritual_level_filter').val(set.spiritual_level).trigger('change');
        }
        (async () => {
            if (set.department) {
                let config = {
                        level_gte: 2
                    },
                    config2 = {};
                config.department = set.department;
                config2.department_id = set.department;
                await getData(urlChurch, config2).then(data => {
                    const churches = data.map(option => `<option value="${option.id}">${option.get_title}</option>`);
                    $churchFilter.html('<option value="">ВСЕ</option><option value="any">ЛЮБАЯ</option><option value="nothing">НЕТ</option>')
                                 .append(churches);
                    return data;
                });
                await getData(urlUserShort, config).then(data => {
                    const users = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
                    $treeFilter.html('<option value="ВСЕ">ВСЕ</option>').append(users);
                    return data;
                });
            }
            (set.church_id) && $churchFilter.val(set.church_id).trigger('change');
            (set.master_tree) && $treeFilter.val(set.master_tree).trigger('change');
            if (set.master_tree) {
                let config = {
                    master_tree: set.master_tree
                };
                getData(urlUserShort, config).then(data => {
                    const users = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
                    $masterFilter.html('<option value="ВСЕ">ВСЕ</option>').append(users);
                });
            }
            (set.master) && $masterFilter.val(set.master).trigger('change');
            (set.hierarchy) && $hierarchyFilter.val(set.hierarchy).trigger('change');
            for (let [key, value] of Object.entries(set)) {
                $('#filterPopup').find(`input[data-filter="${key}"]`).val(value);
            }
            (set.is_partner) && $partnerFilter.val(set.is_partner).trigger('change');
            $('.apply-filter').trigger('click');
            filterChange();
        })();
    }

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        console.log(filterParam);
        filterInit(filterParam);
    }

    $.validate({
        lang: 'ru',
        form: '#createUser',
        onError: function (form) {
            showAlert(`Введены некорректные данные`);
            let top = $(form).find('div.has-error').first().offset().top;
            $(form).find('.body').animate({scrollTop: top}, 500);
        },
        onSuccess: function (form) {
            if ($(form).attr('name') == 'createUser') {
                $(form).find('#saveNew').attr('disabled', true);
                createNewUser(null);
            }
            return false; // Will stop the submission of the form
        },
    });

});