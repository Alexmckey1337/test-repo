'use strict';
import 'jquery-ui/ui/widgets/sortable.js';
import 'jquery-ui/themes/base/sortable.css';

export default function makeSortForm(data) {
    let sortFormTmpl, obj, rendered;
    sortFormTmpl = document.getElementById("sortForm").innerHTML;
    obj = {};
    obj.user = [];
    obj.user.push("");
    obj.user.push(data);
    rendered = _.template(sortFormTmpl)(obj);
    document.getElementById('sort-form').innerHTML = rendered;
    $("#sort-form").sortable({revert: true, items: "li:not([disable])", scroll: false});
}