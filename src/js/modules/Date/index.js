'use strict';

export default function (date, flag) {
    if (flag == '.') {
        return date.trim().split('-').reverse().join('.');
    } else if (flag == '-') {
        return date.trim().split('.').reverse().join('-');
    }
}