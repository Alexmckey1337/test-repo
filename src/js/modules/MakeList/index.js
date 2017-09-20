'use strict';
import {getResponsible, getChurchesListINDepartament, getHomeGroupsINChurches} from '../GetList/index';

export function makeResponsibleList(department, status, flag = false) {
    let $selectResponsible = $('#selectResponsible'),
        activeMaster = $selectResponsible.find('option:selected').val();
    getResponsible(department, status).then(function (data) {
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

function makeHomeGroupsList(ID) {
    let churchID = ID || $('#church_list').val();
    if (churchID && typeof parseInt(churchID) == "number") {
        return getHomeGroupsINChurches(churchID)
    }
    return new Promise(function (reject) {
        reject(null);
    })
}