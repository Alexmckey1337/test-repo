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
            if (typeof(options[item]) === 'object') {
                for (let i = 0; i < options[item].length; i++) {
                    url += item + '=' + options[item][i] + "&";
                }

            } else {
                url += item + '=' + options[item] + "&";
            }

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

export function deleteData(url, config = {}) {
    let initConfig = Object.assign({}, defaultOption, {method: 'DELETE'}, config);
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

export function postData(url, data = {}, config = {}) {
    let postConfig = {
            method: 'POST',
            body: JSON.stringify(data),
        },
        initConfig = Object.assign({}, defaultOption, postConfig, config);
    console.log(initConfig);
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

export function postExport(url, data = {}) {
        let postConfig = {
            method: 'POST',
            body: JSON.stringify(data),
        },
        initConfig = Object.assign({}, defaultOption, postConfig);
    if (typeof url === "string") {

        return fetch(url, initConfig).then(resp => resp).catch(err => err);
    }
}