'use strict';
import alertify from 'alertifyjs/build/alertify.min.js';
import 'alertifyjs/build/css/alertify.min.css';
import 'alertifyjs/build/css/themes/default.min.css';

const USERID = $('body').attr('data-user');
let url =`ws://${window.location.host}/ws/user/${USERID}/`;
let socket = new WebSocket(url);
socket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    if (data.type == 'SUMMIT_TICKET') {
        let count = $('.sms').attr('data-count');
        console.log(count);
        console.log(data);
        console.log(+count + 1);
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
        alertify.logPosition("bottom right");
        alertify.delay(30000).maxLogItems(10).closeLogOnClick(true).log(message_text);
    } else {
        if (true || +data.user_id != USERID) {
            let message_text = data.editor_name + ' создал платеж на ' + data.sum;
            alertify.logPosition("bottom right");
            alertify.delay(30000).maxLogItems(10).closeLogOnClick(true).log(message_text);
        }
    }
};
socket.onopen = function () {
};