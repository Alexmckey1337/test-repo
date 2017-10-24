'use strict';
import {setDataForPopup} from "../Summit/index";

export function addUserToSummit(data) {
    let id = data.id,
        fullName = data.fullname,
        masterFullName = data.master.fullname;
    let $summitVal = $('#summit-value');
    let $popup = $('#popup');
    $summitVal.val("0");
    $summitVal.attr('readonly', true);
    $popup.find('textarea').val('');
    setDataForPopup(id, fullName, masterFullName);
    $popup.show();
}