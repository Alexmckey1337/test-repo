'use strict';
import sendPassToEmail from './modules/sendPassToEmail';

$("document").ready(function () {
    document.getElementById('getpass').addEventListener('click', function () {
        sendPassToEmail();
    })
});