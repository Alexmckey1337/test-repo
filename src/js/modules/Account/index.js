'use strict';
import moment from 'moment/min/moment.min.js';
import URLS from '../Urls/index';
import {postData} from "../Ajax/index";
import ajaxRequest from '../Ajax/ajaxRequest';
import {showAlert} from '../ShowNotifications/index';
import {getCountries, getRegions, getCities} from '../GetList/index';
import {makeCountriesList, makeRegionsList, makeCityList} from '../MakeList/index';

export function sendNote(profileId, text, box) {
    let data = {
        "text": text
    };
    let json = JSON.stringify(data);
    ajaxRequest(URLS.summit_profile.create_note(profileId), json, function (note) {
        box.before(function () {
            return '<div class="rows"><div><p>' + note.text + ' — ' + moment(note.date_created).format("DD.MM.YYYY HH:mm:ss")
                + ' — Author: ' + note.owner_name
                + '</p></div></div>'
        });
        showAlert('Примечание добавлено');
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}

export function changeLessonStatus(lessonId, profileId, checked) {
    let data = {
        "anket_id": profileId
    };
    let url;
    if (checked) {
        url = URLS.summit_lesson.add_viewer(lessonId);
    } else {
        url = URLS.summit_lesson.del_viewer(lessonId);
    }
    let json = JSON.stringify(data);
    ajaxRequest(url, json, function (data) {
        if (data.checked) {
            showAlert('Урок ' + data.lesson + ' просмотрен.');
        } else {
            showAlert('Урок ' + data.lesson + ' не просмотрен.');
        }
        $('#lesson' + data.lesson_id).prop('checked', data.checked);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            data = data.responseJSON;
            showAlert(data.detail);
            $('#lesson' + data.lesson_id).prop('checked', data.checked);
        }
    });
}

export function initLocationSelect(config) {
    let $countrySelector = $('#' + config.country);
    let $regionSelector = $('#' + config.region);
    let $citySelector = $('#' + config.city);
    let selectCountry = $countrySelector.val();
    let selectRegion = $regionSelector.val();
    let selectCity = $citySelector.val();
    getCountries().then(function (data) {
        if (typeof data == "object") {
            let list = makeCountriesList(data, selectCountry);
            $countrySelector.html(list);
        }
        return $countrySelector.find(':selected').data('id');
    }).then(function (id) {
        if (!selectCountry || !id) return null;
        let config = {};
        config.country = id;
        getRegions(config).then(function (data) {
            if (typeof data == "object") {
                let list = makeRegionsList(data, selectRegion);
                $regionSelector.html(list);
            }
            return $regionSelector.find(':selected').data('id')
        }).then(function (id) {
            if (!selectRegion || !id) return null;
            let config = {};
            config.region = id;
            getCities(config).then(function (data) {
                if (typeof data == "object") {
                    let list = makeCityList(data, selectCity);
                    $citySelector.html(list);
                }
            });
        })
    });
    $countrySelector.on('change', function () {
        let config = {};
        config.country = $countrySelector.find(':selected').data('id');
        selectCountry = $countrySelector.find(':selected').val();
        getRegions(config).then(function (data) {
            let list = makeRegionsList(data, selectRegion);
            $regionSelector.html(list);
        }).then(function () {
            $citySelector.html('');
        })
    });
    $regionSelector.on('change', function () {
        let config = {};
        config.region = $regionSelector.find(':selected').data('id');
        selectRegion = $regionSelector.find(':selected').val();
        getCities(config).then(function (data) {
            let list = makeCityList(data, selectCity);
            $citySelector.html(list);
        })
    });
}

export function btnNeed() {
    $('.a-note, .a-sdelki').find('.editText').on('click', function () {
        $(this).toggleClass('active');
        let textArea = $(this).parent().siblings('textarea'),
            select = $(this).closest('.note_wrapper').find('select'),
            btn = $(this).closest('.access_wrapper').find('#delete_access');
        if ($(this).hasClass('active')) {
            textArea.attr('readonly', false);
            select.attr('readonly', false).attr('disabled', false);
            btn.attr('disabled', false);
        } else {
            textArea.attr('readonly', true);
            select.attr('readonly', true).attr('disabled', true);
            btn.attr('disabled', true);
        }
    });

    $('.a-note, .a-sdelki').find('.send_need').on('click', function () {
        let partnerID = $(this).attr('data-partner'),
            textArea = $(this).parent().siblings('textarea'),
            need_text = textArea.val(),
            url = URLS.partner.update_need(partnerID),
            data = {'need_text': need_text};
        if (!partnerID) {
            showAlert('Пользователь не является партнёром в данном блоке');
            return
        }
        postData(url, data, {method: 'PUT'}).then(() => {
            showAlert('Нужда сохранена.');
        }).catch(err => {
            showAlert(err.detail);
        });
        $(this).siblings('.editText').removeClass('active');
        textArea.attr('readonly', true);
    });
}