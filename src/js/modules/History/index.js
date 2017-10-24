'use strict';

export default function updateHistoryUrl(data) {
    let url,
        filterKeys = Object.keys(data);
    if (filterKeys && filterKeys.length) {
        let items = filterKeys.length,
            count = 0;
        url = '?';
        filterKeys.forEach(function (key) {
            count++;
            url += key + '=' + data[key];
            if (count != items) {
                url += '&';
            }
        });
        history.replaceState(null, null, `${url}`);
    } else {
        history.replaceState(null, null, window.location.pathname);
    }
}