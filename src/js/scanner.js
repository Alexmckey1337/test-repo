'use strict';
import URLS from './modules/Urls/index';
import getData from './modules/Ajax';

$(document).ready(function () {
    $('#scanner_form').on('submit', function (e) {
        e.preventDefault();
        let code = $(this).find('input').val().trim(),
            options = { code },
            config = {
                headers: new Headers({
                    'Content-Type': 'application/json',
                    'Visitors-Location-Token': '4ewfeciss6qdbmgfj9eg6jb3fdcxefrs4dxtcdrt10rduds2sn'
                })
            },
            img = $('#user_photo'),
            imgWrapp = $('.photo_wrapper'),
            imgUrl =  img.attr('data-img_default');

        $('.preloader').css('display', 'block');
        getData(URLS.scan_code(), options, config).then( data => {
            $('.preloader').css('display', 'none');
            $('#user_name').text(data.fullname);
            $('#count').text(data.passes_count);
            (data.active) ? imgWrapp.removeClass('active') : imgWrapp.addClass('active');
            (data.avatar_url) ? img.attr('src', data.avatar_url) : img.attr('src', imgUrl);
            $('#code').val('').focus();
        }).catch(() => {
            $('.preloader').css('display', 'none');
            $('#user_name').text('Пользователь не найден');
            $('#count').text('0');
            imgWrapp.removeClass('active');
            img.attr('src', imgUrl);
            $('#code').val('').focus();
        });
    })
});