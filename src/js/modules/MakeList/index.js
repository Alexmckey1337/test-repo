'use strict';
import {getResponsible, getChurchesListINDepartament, getHomeGroupsINChurches,
        getDepartmentsOfUser, getShortUsers} from '../GetList/index';
import {getSummitAuthors, getSummitAuthorsByMasterTree} from "../GetList";

export function makeResponsibleList(department, status, flag = false, include = false) {
    let $selectResponsible = $('#selectResponsible'),
        activeMaster = $selectResponsible.find('option:selected').val(),
        include_id = (include) ? activeMaster : '';
    getResponsible(department, status, '', include_id).then(function (data) {
        let defaultOption = `<option value="none" disabled="disabled" selected="selected">Выберите ответственного</option>`
        let options = data.map(option =>
            `<option value="${option.id}" ${(activeMaster == option.id) ? 'selected' : ''}>${option.fullname}</option>`);
        if (flag) {
            if (status > 60) {
                $selectResponsible.empty()
                    .html(defaultOption)
                    .append(`<option value="">Нет ответственного</option>`)
                    .append(options);
            } else {
                $selectResponsible.empty().html(defaultOption).append(options);
            }
        } else {
            $selectResponsible.empty().html(defaultOption).append(options);
        }
    })
}

export function makeChurches() {
    let $selectDepartment = $('#departments'),
        departmentID = $selectDepartment.val();
    if (departmentID && typeof parseInt(departmentID) == "number") {
        getChurchesListINDepartament(departmentID).then(function (data) {
            console.log(departmentID);
            let selectedChurchID = $('#church_list').val();
            let options = [];
            let option = document.createElement('option');
            $(option).val('').text('Выберите церковь').attr('selected', true).attr('disabled', true);
            options.push(option);
            data.forEach(function (item) {
                let option = document.createElement('option');
                $(option).val(item.id).text(item.get_title);
                if (selectedChurchID == item.id) {
                    $(option).attr('selected', true);
                }
                options.push(option);
            });
            $('#church_list').html(options).on('change', function () {
                let churchID = $(this).val();
                if (churchID && typeof parseInt(churchID) == "number") {
                    makeHomeGroupsList(churchID).then(function (data) {
                        let $homeGroupsList = $('#home_groups_list');
                        let homeGroupsID = $homeGroupsList.val();
                        let options = [];
                        let option = document.createElement('option');
                        $(option).val('').text('Выберите домашнюю группу').attr('selected', true);
                        options.push(option);
                        data.forEach(function (item) {
                            let option = document.createElement('option');
                            $(option).val(item.id).text(item.get_title);
                            if (homeGroupsID == item.id) {
                                $(option).attr('selected', true);
                            }
                            options.push(option);
                        });
                        $homeGroupsList.html(options);
                    });
                }
            }).trigger('change');
        });
    }
}

export function makeHomeGroupsList(ID) {
    let churchID = ID || $('#church_list').val();
    if (churchID && typeof parseInt(churchID) == "number") {
        return getHomeGroupsINChurches(churchID)
    }
    return new Promise(function (reject) {
        reject(null);
    })
}

export function makeCountriesList(data, selectCountry) {
    let rendered = [];
    let option = document.createElement('option');
    $(option).val('').text('Выберите страну').attr('disabled', true).attr('selected', true);
    rendered.push(option);
    data.forEach(function (item) {
        let option = document.createElement('option');
        $(option).val(item.title).text(item.title).attr('data-id', item.id);
        if (item.title == selectCountry) {
            $(option).attr('selected', true);
        }
        rendered.push(option);
    });
    return rendered
}

export function makeRegionsList(data, selectRegion) {
    let rendered = [];
    let option = document.createElement('option');
    $(option).val('').text('Выберите регион').attr('disabled', true).attr('selected', true);
    rendered.push(option);
    data.forEach(function (item) {
        let option = document.createElement('option');
        $(option).val(item.title).text(item.title).attr('data-id', item.id);
        if (item.title == selectRegion) {
            $(option).attr('selected', true);
        }
        rendered.push(option);
    });
    return rendered
}

export function makeCityList(data, selectCity) {
    let rendered = [];
    let option = document.createElement('option');
    $(option).val('').text('Выберите город').attr('disabled', true).attr('selected', true);
    rendered.push(option);
    data.forEach(function (item) {
        let option = document.createElement('option');
        $(option).val(item.title).text(item.title).attr('data-id', item.id);
        if (item.title == selectCity) {
            $(option).attr('selected', true);
        }
        rendered.push(option);
    });
    return rendered
}

export function makePastorList(departmentId, selector, active = null) {
    getResponsible(departmentId, 2).then(function (data) {
        let options = [];
        data.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.fullname);
            if (active == item.id) {
                $(option).attr('selected', true);
            }
            options.push(option);
        });
        $(selector).html(options).prop('disabled', false).select2();
    });
}

export function makeDepartmentList(selector, active = null) {
    return getDepartmentsOfUser($("body").attr("data-user")).then(function (data) {
        let options = [];
        let department = data;
        department.forEach(function (item) {
            let option = document.createElement('option');
            $(option).val(item.id).text(item.title);
            if (active == item.id) {
                $(option).attr('selected', true);
            }
            options.push(option);
        });
        $(selector).html(options).prop('disabled', false).select2();
    });
}

export function makePastorListNew(departmentId, summitId, selector = [], active = null) {
    getSummitAuthors(departmentId, summitId, 2).then(function (data) {
        let options = '<option selected>ВСЕ</option>';
        data.forEach(function (item) {
            options += `<option value="${item.id}"`;
            if (active == item.id) {
                options += 'selected';
            }
            options += `>${item.title}</option>`;
        });
        selector.forEach(item => {
            $(item).html(options).prop('disabled', false).select2();
        })
    });
}

export function makePastorListWithMasterTree(config, summitId, selector, active = null) {
    getSummitAuthorsByMasterTree(summitId, config).then(data => {
        let options = '<option selected>ВСЕ</option>';
        data.forEach(function (item) {
            options += `<option value="${item.id}"`;
            if (active == item.id) {
                options += 'selected';
            }
            options += `>${item.title}</option>`;
        });
        selector.forEach(item => {
            $(item).html(options).prop('disabled', false).select2();
        })
    })
}