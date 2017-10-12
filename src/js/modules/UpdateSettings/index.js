'use strict';
import URLS from '../Urls/index';
import {VOCRM} from "../config"
import {postData} from "../Ajax/index";
import {getFilterParam} from "../Filter/index";

export default function updateSettings(callback, path) {
    let data = [];
    let iteration = 1;
    $("#sort-form input").each(function () {
        if ($(this).data('editable')) {
            let item = {};
            item['id'] = $(this).val();
            item['number'] = ++iteration;
            item['active'] = $(this).prop('checked');
            data.push(item);
        }
    });
    postData(URLS.update_columns(), data).then((JSONobj) => {
        $(".bgsort").remove();
            VOCRM['column_table'] = JSONobj['column_table'];

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