'use strict';
import URLS from '../Urls/index';
import {postData} from "../Ajax/index";
import {getFilterParam} from "../Filter/index";

export default function updateSettings(callback, table_name, path) {
    let data = [];
    let iteration = 1;
    $("#sort-form input").each(function () {
        if ($(this).data('editable')) {
            let item = {};
            item['number'] = ++iteration;
            item['active'] = $(this).prop('checked');
            item['name'] = $(this).attr('data-key');
            data.push(item);
        }
    });
    postData(URLS.update_columns(), {name: table_name, 'columns': data}).then((JSONobj) => {
        $(".bgsort").remove();

            if (callback) {
                let param = {};
                if (path !== undefined) {
                    let extendParam = $.extend({}, param, getFilterParam());
                    callback(extendParam);
                } else {
                    let param = getFilterParam();
                    callback(param);
                }
            }
    })
}