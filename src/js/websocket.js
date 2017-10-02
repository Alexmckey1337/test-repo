'use strict';
import alertify from 'alertifyjs/build/alertify.min.js';
import 'alertifyjs/build/css/alertify.min.css';
import 'alertifyjs/build/css/themes/default.min.css';
import {makeExports} from "./modules/Notifications/notify";

const USERID = $('body').attr('data-user');
let url = `wss://${window.location.host}/ws/user/${USERID}/`;
let socket = new WebSocket(url);
socket.onmessage = function (e) {
    let data = JSON.parse(e.data),
        count = $('.sms').attr('data-count');
    if (data.type == 'SUMMIT_TICKET') {
        $("#without_notifications").remove();
        if ($('#ticket_notifications').length > 0) {
            let el = `<li><a href='${data.ticket_url}'>${data.ticket_title}</a></li>`;
            $('#ticket_notifications').append(el);
        } else {
            let el = `<p><a href='${MAINURLS.ticketsURL}'>Сгенерированы новые билеты:</a></p>
                        <ul id='ticket_notifications'><li><a href='${data.ticket_url}'>${data.ticket_title}</a></li></ul>`;
            $('.massage-hover .bottom-box:first').append(el);
        }
        $('.sms').attr('data-count', +count + 1);
        let message_text = `Summit id: ${data.summit_id}, User id: ${data.user_id}, Url: ${data.file}`;
        alertify.set('notifier', 'position', 'bottom-right');
        alertify.notify(`${message_text}`, 'success', 10);
    }
    if (data.type == 'EXPORT') {
        $("#without_notifications").remove();
        $('.sms').attr('data-count', +count + 1);
        if ($('#export_notifications').length > 0) {
            let exportCount = $('#export_notifications').find('span').text();
            $('#export_notifications').find('span').text(+exportCount + 1);
        } else {
            let el = `<div id="export_notifications" class="notification_row notification_row__export" data-type="export">
                        <p>Доступный экспорт: <span>1</span></p></div>`;
            $('.massage-hover').find('.hover-wrapper').append(el);
            $('#export_notifications').on('click', function () {
                makeExports();
            });
        }
        let message_text = `Файл ${data.name} сформирован для выгрузки`;
        alertify.set('notifier', 'position', 'bottom-right');
        alertify.notify(`${message_text}`, 'success', 10);
    } else {
        if (true || +data.user_id != USERID) {
            let message_text = data.editor_name + ' создал платеж на ' + data.sum;
            alertify.set('notifier', 'position', 'bottom-right');
            alertify.notify(`${message_text}`, 'success', 10);
        }
    }
};
socket.onopen = function () {
};