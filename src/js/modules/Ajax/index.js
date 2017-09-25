'use strict';

export default function getData(url, options = {}) {
    let keys = Object.keys(options);
    if (keys.length) {
        url += '?';
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }
    let defaultOption = {
        method: 'GET',
        credentials: 'same-origin',
        headers: new Headers({
            'Content-Type': 'application/json',
        })
    };
    if (typeof url === "string") {
        $('.preloader').css('display', 'none');
        return fetch(url, defaultOption).then(data => data.json()).catch(err => err);
    }
}