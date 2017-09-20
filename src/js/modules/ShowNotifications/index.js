'use strict';
import alertify from 'alertifyjs/build/alertify.min.js';
import 'alertifyjs/build/css/alertify.min.css';
import 'alertifyjs/build/css/themes/default.min.css';

export function showAlert(message, title = 'Уведомление') {
    alertify.alert(title, message);
}