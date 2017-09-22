'use strict';

export default function accordionInfo() {
    $('.info-title').on('click', function () {
        $(this).next('.info').slideToggle().siblings('.info:visible').slideUp();
        $(this).toggleClass('info-title_active').siblings('.info-title').removeClass('info-title_active');
    });
}