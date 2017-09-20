'use strict';
import {getResponsible} from '../GetList/index';

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