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
            } else if (resp.status >= 500 && resp.status < 505) {
                throw new Error('К сожалению, сервер временно недоступен. Повторите попытку позже');
            } else {
                return resp.json().then(err => {
                    throw err;
                });
            }
        });
    }
}

export function getDataPhone(url, options = {}, config = {}) {

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
            }else if (resp.status === 503) {
                let error = {
                    status: '503',
                    message: 'Служба Asterisk временно недоступна, повторите попытку позже'
                };
                return error;
            }else {
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
            } else if (resp.status >= 500 && resp.status < 505) {
                throw new Error('К сожалению, сервер временно недоступен. Повторите попытку позже');
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
            body: (data === null) ? null : JSON.stringify(data),
        },
        initConfig = Object.assign({}, defaultOption, postConfig, config);
    if (typeof url === "string") {

        return fetch(url, initConfig).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp.json();
            } else if (resp.status >= 500 && resp.status < 505) {
                throw new Error('К сожалению, сервер временно недоступен. Повторите попытку позже');
            } else {
                return resp.json().then(err => {
                    throw err;
                });
            }
        });
    }
}

export function postFormData(url, data = {}, config = {}) {
    let postConfig = {
            method: 'POST',
            credentials: 'same-origin',
            body: data,
        },
        initConfig = Object.assign({}, postConfig, config);
    if (typeof url === "string") {

        return fetch(url, initConfig).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp;
            } else if (resp.status >= 500 && resp.status < 505) {
                throw new Error('К сожалению, сервер временно недоступен. Повторите попытку позже');
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

export function loadTickets(url, data = {}) {
	let postConfig = {
			method: 'POST',
			body: JSON.stringify(data),
		},
		initConfig = Object.assign({}, defaultOption, postConfig);
	if (typeof url === "string") {

		return fetch(url, initConfig).then(resp => resp).catch(err => err);
	}
}

export function getAudioFile(url) {
    let config = {
            mode: 'cors',
            headers: new Headers({
                'Content-Type': 'text / html',
                'Access-Control-Allow-Origin': '*',
                'Record-Token': 'g6jb3fdcxefrs4dxtcdrt10r4ewfeciss6qdbmgfj9eduds2sn',
            })
        },
        initConfig = Object.assign({}, defaultOption, config);
    if (typeof url === "string") {

        return fetch(url, initConfig).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp.blob();
            }else if (resp.status === 503) {
                throw Error('Служба Asterisk временно недоступна, повторите попытку позже');
            }else if (resp.status === 404) {
                let error = {
                    status: 404,
                    message: "Файл не найден"
                };
                throw error;
            } else {
                return resp.json().then(err => {
                    throw err;
                });
            }
        });
    }
}
