'use strict';
import 'whatwg-fetch';

let defaultOption = {
    method: 'GET',
    credentials: 'same-origin',
    headers: new Headers({
        'Content-Type': 'application/json',
    })
};

export default function getData(url, options = {}, config = {}) {
    let keys = Object.keys(options);
    if (keys.length) {
        url += '?';
        keys.forEach(item => {
            url += item + '=' + options[item] + "&"
        });
    }
    let initConfig = Object.assign({}, defaultOption, config);
    if (typeof url === "string") {

        return fetch(url, initConfig).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp.json();
            } else {
                return resp.json().then(err => {
                    throw err;
                });
            }
        });
    }
}

export function deleteData(url) {
    let initConfig = Object.assign({}, defaultOption, {method: 'DELETE'});
    if (typeof url === "string") {

        return fetch(url, initConfig).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp;
            } else {
                return resp.json().then(err => {
                    throw err;
                });
            }
        });
    }
}