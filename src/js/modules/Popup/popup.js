'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';

export function showPopup(text, title, callback) {
    text = text || '';
    title = title || 'Информационное сообщение';
    let popup = document.getElementById('create_pop');
    if (popup) {
        popup.parentElement.removeChild(popup)
    }
    let div = document.createElement('div');

    let html = `<div class="pop_cont" >
            <div class="top-text"><h3>${title}</h3><span id="close_pop">×</span></div>
            <div class="main-text"><p>${text}</p></div>
        </div>`;
     $(div).html(html)
            .attr({
                id: "create_pop"
            })
            .addClass('pop-up-universal');
    $('body').append(div);

    $('#close_pop').on('click', function () {
        $('.pop-up-universal').css('display', 'none').remove();
    });
}

export function showPopupHTML(block) {
    let popup = document.createElement('div');
    popup.className = "pop-up-universal";
    $(popup).append(block);
    $('body').append(popup);

    $('#close_pop').on('click', function () {
        $(popup).hide().remove();
    });
}

export function showStatPopup(body, title, callback) {
    title = title || 'Информационное сообщение';
    let popup = document.getElementById('create_pop');
    if (popup) {
        popup.parentElement.removeChild(popup)
    }
    let div = document.createElement('div');

    let html = `<div class="pop_cont" >
        <div class="top-text">
            <h3>${title}</h3><span id="close_pop">×</span></div>
            <div class="main-text">${body}</div>
            <div><button class="make">СФОРМИРОВАТЬ</button></div>
        </div>`;
    $(div)
        .html(html)
        .attr({
            id: "create_pop"
        })
        .addClass('pop-up__stats')
        .find('.date').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });
    $(div).find('select').select2();
    $(div).find('.make').on('click', function (e) {
        e.stopPropagation();
        let data = {
            id: $(div).find('.master').val(),
            attended: $(div).find('.attended').val(),
            date: $(div).find('.date').val()
        };
        callback(data);
    });
    $('body').append(div);

    $('#close_pop').on('click', function () {
        $('.pop-up__stats').css('display', 'none').remove();
    });
}

export function hidePopup(el) {
    if ($(el).closest('.popap').find('.save-user').length) {
        $(el).closest('.popap').find('.save-user').attr('disabled', false);
        $(el).closest('.popap').find('.save-user').text('Сохранить');
    }
    $(el).closest('.popap').css('display', 'none');
    $(el).closest('.popap_slide').removeClass('active');
    $(el).closest('.popap_slide').css('display', 'block');
    $('.bg').removeClass('active');
}

export function closePopup(el) {
    $(el).closest('.pop-up-splash').hide();
}

