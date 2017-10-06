'use strict';

export default function parseUrlQuery() {
    let data = {};
    if (location.search) {
        let pair = (location.search.substr(1)).split('&');
        for (let i = 0; i < pair.length; i++) {
            let param = pair[i].split('=');
            data[param[0]] = decodeURI(param[1]);
        }
    }
    return data;
}