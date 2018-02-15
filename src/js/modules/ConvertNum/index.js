'use strict';

export const convertNum =  function (num, flag) {
    if (flag === '.') {
        return +num.trim().replace(/[,]/, ".")
    } else if (flag == ',') {
        return num.toString().trim().replace(/[.]/, ",")
    }
};