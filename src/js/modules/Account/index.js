'use strict';
import moment from 'moment/min/moment.min.js';
import WavPlayer from 'webaudio-wav-stream-player';
import 'howler';
import URLS from '../Urls/index';
import ajaxRequest from '../Ajax/ajaxRequest';
import {showAlert} from '../ShowNotifications/index';
import getData,{getDataAudio} from "../Ajax/index";
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

export function dataIptelTable(url) {
    getData(url).then(data => {
        makeIptelTable(data,'#iptelBlock');
    });
}
export function dataIptelMonth(url) {
    getData(url).then(data => {
        makeIptelTable(data,'#tableMonthIptel');
        $('.preloader').css('display', 'none');
    });
}
function makeIptelTable(data,block) {
    let table = `<table class="tableIptel">
                        <thead>
                            <tr>
                                <th>Тип</th>
                                <th>Дата</th>
                                <th>Номер оператора</th>
                                <th>Назначение</th>                                        
                                <th>Длительность</th>
                                <th>Запись</th>
                            </tr>
                        </thead>
                        <tbody>${data.map(item => {
        return `<tr>
                            <td>
                                ${item.type === 'out' ? `<svg fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M0 0h24v24H0z" fill="none"/>
                                                            <path d="M18 11l5-5-5-5v3h-4v4h4v3zm2 4.5c-1.25 0-2.45-.2-3.57-.57-.35-.11-.74-.03-1.02.24l-2.2 2.2c-2.83-1.44-5.15-3.75-6.59-6.59l2.2-2.21c.28-.26.36-.65.25-1C8.7 6.45 8.5 5.25 8.5 4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.5c0-.55-.45-1-1-1z"/>
                                                        </svg>` : `<svg xmlns:dc="http://purl.org/dc/elements/1.1/"
                                                           xmlns:cc="http://creativecommons.org/ns#"
                                                           xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                                           xmlns:svg="http://www.w3.org/2000/svg"
                                                           xmlns="http://www.w3.org/2000/svg"
                                                           xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                                           xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
                                                           width="6.3499999mm"
                                                           height="6.3499999mm"
                                                           viewBox="0 0 6.3499999 6.3499999"
                                                           version="1.1"
                                                           id="svg8"
                                                           inkscape:version="0.92.1 r15371"
                                                           sodipodi:docname="incoming.svg">
                                                          <defs
                                                             id="defs2" />
                                                          <sodipodi:namedview
                                                             id="base"
                                                             pagecolor="#ffffff"
                                                             bordercolor="#666666"
                                                             borderopacity="1.0"
                                                             inkscape:pageopacity="0.0"
                                                             inkscape:pageshadow="2"
                                                             inkscape:zoom="11.2"
                                                             inkscape:cx="20.38665"
                                                             inkscape:cy="4.7593318"
                                                             inkscape:document-units="mm"
                                                             inkscape:current-layer="g3702"
                                                             showgrid="false"
                                                             inkscape:window-width="1920"
                                                             inkscape:window-height="1017"
                                                             inkscape:window-x="-8"
                                                             inkscape:window-y="-8"
                                                             inkscape:window-maximized="1" />
                                                          <metadata
                                                             id="metadata5">
                                                            <rdf:RDF>
                                                              <cc:Work
                                                                 rdf:about="">
                                                                <dc:format>image/svg+xml</dc:format>
                                                                <dc:type
                                                                   rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                                                <dc:title></dc:title>
                                                              </cc:Work>
                                                            </rdf:RDF>
                                                          </metadata>
                                                          <g
                                                             inkscape:label="1"
                                                             inkscape:groupmode="layer"
                                                             id="layer1"
                                                             style="display:inline"
                                                             transform="translate(0,-290.65)" />
                                                          <g
                                                             id="g3702"
                                                             inkscape:groupmode="layer"
                                                             inkscape:label="2"
                                                             style="display:inline"
                                                             transform="translate(0,-290.65)">
                                                            <g
                                                               id="g3713"
                                                               transform="translate(211.0619,231.17024)">
                                                              <g
                                                                 transform="matrix(0.26458333,0,0,0.26458333,-211.0619,59.479762)"
                                                                 id="g3694"
                                                                 style="display:inline;fill:#000000">
                                                                <path
                                                                   style="fill:none"
                                                                   inkscape:connector-curvature="0"
                                                                   d="M 0,0 H 24 V 24 H 0 Z"
                                                                   id="path3680" />
                                                                <path
                                                                   sodipodi:nodetypes="sccccccssssssss"
                                                                   inkscape:connector-curvature="0"
                                                                   d="m 20,15.5 c -1.25,0 -2.45,-0.2 -3.57,-0.57 -0.35,-0.11 -0.74,-0.03 -1.02,0.24 l -2.2,2.2 C 10.38,15.93 8.06,13.62 6.62,10.78 L 8.82,8.57 C 9.1,8.31 9.18,7.92 9.07,7.57 8.7,6.45 8.5,5.25 8.5,4 8.5,3.45 8.05,3 7.5,3 H 4 C 3.45,3 3,3.45 3,4 c 0,9.39 7.61,17 17,17 0.55,0 1,-0.45 1,-1 v -3.5 c 0,-0.55 -0.45,-1 -1,-1 z"
                                                                   id="path3682" />
                                                              </g>
                                                              <g
                                                                 style="fill:#000000"
                                                                 id="g3700"
                                                                 transform="matrix(0.26458333,0,0,0.26458333,-211.0619,59.479762)">
                                                                <path
                                                                   id="path3696"
                                                                   d="M 0,0 H 24 V 24 H 0 Z"
                                                                   inkscape:connector-curvature="0"
                                                                   style="fill:none" />
                                                                <path
                                                                   sodipodi:nodetypes="cccccccc"
                                                                   id="path3698"
                                                                   d="M 19,11 14,6 19,1 v 3 h 4 v 4 h -4 z"
                                                                   inkscape:connector-curvature="0" />
                                                              </g>
                                                            </g>
                                                          </g>
                                                        </svg>`}
                            </td>
                            <td>
                                ${item.call_date}
                            </td>
                            <td>
                                ${item.src}
                            </td>
                            <td>
                                ${item.dst}
                            </td>
                            <td>
                                ${item.billsec}
                            </td> 
                            <td class="recordIptel">
                                <p class=''>${item.record}</p>
                                <svg class="btnPlay active" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                     viewBox="0 0 60 60" style="enable-background:new 0 0 60 60;" xml:space="preserve">
                                    <g>
                                        <path d="M45.563,29.174l-22-15c-0.307-0.208-0.703-0.231-1.031-0.058C22.205,14.289,22,14.629,22,15v30
                                            c0,0.371,0.205,0.711,0.533,0.884C22.679,45.962,22.84,46,23,46c0.197,0,0.394-0.059,0.563-0.174l22-15
                                            C45.836,30.64,46,30.331,46,30S45.836,29.36,45.563,29.174z M24,43.107V16.893L43.225,30L24,43.107z"/>
                                        <path d="M30,0C13.458,0,0,13.458,0,30s13.458,30,30,30s30-13.458,30-30S46.542,0,30,0z M30,58C14.561,58,2,45.439,2,30
                                            S14.561,2,30,2s28,12.561,28,28S45.439,58,30,58z"/>
                                    </g>
                                </svg>
                                <svg class="btnStop" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100.021 100.021" xmlns:xlink="http://www.w3.org/1999/xlink" enable-background="new 0 0 100.021 100.021">
                                  <g>
                                    <path d="M50.011,0C22.435,0,0,22.435,0,50.011s22.435,50.011,50.011,50.011s50.011-22.435,50.011-50.011S77.587,0,50.011,0z    M50.011,98.021C23.538,98.021,2,76.484,2,50.011S23.538,2,50.011,2s48.011,21.537,48.011,48.011S76.484,98.021,50.011,98.021z"/>
                                    <path d="m70.072,35.899c0-2.761-2.239-5-5-5h-30c-2.761,0-5,2.239-5,5v30c0,2.761 2.239,5 5,5h30c2.761,0 5-2.239 5-5v-30zm-2,30c0,1.657-1.343,3-3,3h-30c-1.657,0-3-1.343-3-3v-30c0-1.657 1.343-3 3-3h30c1.657,0 3,1.343 3,3v30z"/>
                                  </g>
                                </svg>
                            </td>
                        </tr>`;
    }).join('')}</tbody>
                        </table>`;
    $(block).append(table);

}