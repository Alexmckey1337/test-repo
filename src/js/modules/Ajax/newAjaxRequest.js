'use strict';

export default function (data, codes, fail) {
    let resData = {
        method: 'GET'
    };
    Object.assign(resData, data);
    $.ajax(resData).statusCode(codes).fail(fail);
};