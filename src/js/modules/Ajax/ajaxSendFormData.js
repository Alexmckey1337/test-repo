'use strict';

export default function ajaxSendFormData(data = {}) {
    let sendData = {
        method: 'POST'
    };
    Object.assign(sendData, data);
    return new Promise(function (resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open(sendData.method, sendData.url, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    let response = JSON.parse(xhr.responseText);
                    resolve(response);
                } else if (xhr.status == 201) {
                    let response = JSON.parse(xhr.responseText);
                    resolve(response);
                } else if (xhr.status == 400) {
                    let response = JSON.parse(xhr.responseText);
                    reject(response);
                } else if (xhr.status == 404) {
                    reject("У вас нет прав для редактирования");
                } else {
                    reject(xhr.responseText);
                }
            }
        };
        xhr.send(sendData.data);
    });
}