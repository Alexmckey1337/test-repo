'use strict';
import moment from 'moment/min/moment.min.js';
import WavPlayer from 'webaudio-wav-stream-player';
import 'howler';
import URLS from '../Urls/index';
import getData,{getDataPhone,postData} from "../Ajax/index";
import ajaxRequest from '../Ajax/ajaxRequest';
import {showAlert} from '../ShowNotifications/index';
import {
    getCountries,
    getRegions,
    getCities
} from '../GetList/index';
import {
    makeCountriesList,
    makeRegionsList,
    makeCityList
} from '../MakeList/index';

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
    getDataPhone(url).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText')
            $('#iptelBlock').append(err);
        } else {
            makeIptelTable(data, '#iptelBlock');
        }
    });

}
export function dataIptelMonth(url) {
    getDataPhone(url).then(data => {
        if (data.status === '503'){
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText')
            $('#popupMonth').find('.main-text').append(err);
            $('.preloader').css('display', 'none');
        }else{
            makeIptelTable(data,'#tableMonthIptel');
            $('.preloader').css('display', 'none');
        }
    });
}
export function makeIptelTable(data,block) {
    let wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'violet',
        progressColor: 'purple'
    });
    wavesurfer.load('/media/audio/80s_vibe.mp3');
    let table = `<table class="tableIptel">
                        <thead>
                            <tr>
                                <th>Тип</th>
                                <th>Дата</th>
                                <th>Кто</th>
                                <th>Куда</th>                                        
                                <th>Длительность(сек)</th>
                                <th>Запись</th>
                            </tr>
                        </thead>
                        <tbody>${data.result.map(item => {
        
        return `<tr>
                            <td>
                                ${item.type === 'out' ? `<svg fill="#81C784" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                                                            <path d="M0 0h24v24H0z" fill="none"/>
                                                            <path d="M18 11l5-5-5-5v3h-4v4h4v3zm2 4.5c-1.25 0-2.45-.2-3.57-.57-.35-.11-.74-.03-1.02.24l-2.2 2.2c-2.83-1.44-5.15-3.75-6.59-6.59l2.2-2.21c.28-.26.36-.65.25-1C8.7 6.45 8.5 5.25 8.5 4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.5c0-.55-.45-1-1-1z"/>
                                                        </svg>` : `<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                                                           xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
                                                           xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="6.3499999mm"
                                                           height="6.3499999mm" viewBox="0 0 6.3499999 6.3499999" version="1.1" id="svg8"
                                                           inkscape:version="0.92.1 r15371" sodipodi:docname="incoming.svg"> <defs id="defs2" />
                                                          <sodipodi:namedview id="base" pagecolor="#ffffff" bordercolor="#666666"
                                                             borderopacity="1.0" inkscape:pageopacity="0.0"
                                                             inkscape:pageshadow="2" inkscape:zoom="11.2"
                                                             inkscape:cx="20.38665" inkscape:cy="4.7593318"
                                                             inkscape:document-units="mm" inkscape:current-layer="g3702"
                                                             showgrid="false" inkscape:window-width="1920"
                                                             inkscape:window-height="1017" inkscape:window-x="-8"
                                                             inkscape:window-y="-8" inkscape:window-maximized="1" />
                                                          <metadata  id="metadata5">
                                                            <rdf:RDF> <cc:Work
                                                                 rdf:about=""> <dc:format>image/svg+xml</dc:format>
                                                                <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
                                                                <dc:title> </dc:title> </cc:Work>
                                                            </rdf:RDF> </metadata>
                                                          <g inkscape:label="1"
                                                             inkscape:groupmode="layer"                                                             id="layer1"
                                                             style="display:inline"                                                             transform="translate(0,-290.65)" />
                                                          <g                                                             id="g3702"
                                                             inkscape:groupmode="layer"                                                             inkscape:label="2"
                                                             style="display:inline"                                                             transform="translate(0,-290.65)">
                                                            <g                                                               id="g3713"
                                                               transform="translate(211.0619,231.17024)">                                                              <g
                                                                 transform="matrix(0.26458333,0,0,0.26458333,-211.0619,59.479762)"                                                                 id="g3694"
                                                                 style="display:inline;fill:#64B5F6">                                                                <path
                                                                   style="fill:none"                                                                   inkscape:connector-curvature="0"
                                                                   d="M 0,0 H 24 V 24 H 0 Z"                                                                   id="path3680" />
                                                                <path                                                                   sodipodi:nodetypes="sccccccssssssss"
                                                                   inkscape:connector-curvature="0"                                                                   d="m 20,15.5 c -1.25,0 -2.45,-0.2 -3.57,-0.57 -0.35,-0.11 -0.74,-0.03 -1.02,0.24 l -2.2,2.2 C 10.38,15.93 8.06,13.62 6.62,10.78 L 8.82,8.57 C 9.1,8.31 9.18,7.92 9.07,7.57 8.7,6.45 8.5,5.25 8.5,4 8.5,3.45 8.05,3 7.5,3 H 4 C 3.45,3 3,3.45 3,4 c 0,9.39 7.61,17 17,17 0.55,0 1,-0.45 1,-1 v -3.5 c 0,-0.55 -0.45,-1 -1,-1 z"
                                                                   id="path3682" />                                                              </g>
                                                              <g                                                                 style="fill:#64B5F6"
                                                                 id="g3700"                                                                 transform="matrix(0.26458333,0,0,0.26458333,-211.0619,59.479762)">
                                                                <path                                                                   id="path3696"
                                                                   d="M 0,0 H 24 V 24 H 0 Z"                                                                   inkscape:connector-curvature="0"
                                                                   style="fill:none" />                                                                <path
                                                                   sodipodi:nodetypes="cccccccc"                                                                   id="path3698"
                                                                   d="M 19,11 14,6 19,1 v 3 h 4 v 4 h -4 z"                                                                   inkscape:connector-curvature="0" />
                                                              </g>                                                            </g>                                                          </g>                                                        </svg>`}
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
                             <td class="recordIptel" onclick="wavesurfer.playPause()">
                                <p class=''>${item.record}</p>
                                <a href="" class="linkFile" download=""><svg class="btnPlay active" fill="#000000" height="30" viewBox="0 0 24 24" width="30" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M0 0h24v24H0z" fill="none"/>
                                    <path d="M10 16.5l6-4.5-6-4.5v9zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                                </svg></a>
                                <svg class="btnStop" fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M0 0h24v24H0z" fill="none"/>
                                    <path d="M6 6h12v12H6z"/>
                                </svg>
                            </td>
                        </tr>
                            `;
    }).join('')}</tbody>
                        </table>`;
    $(block).append(table);

        // $('.recordIptel').on('click', function () {
    //     let defaultOption = {
    //             method: 'GET',
    //             credentials: 'same-origin',
    //             mode: 'cors',
    //             headers: new Headers({
    //                 'Content-Type': 'text / html',
    //                 'Access-Control-Allow-Origin': '*',
    //                 'Record-Token': 'g6jb3fdcxefrs4dxtcdrt10r4ewfeciss6qdbmgfj9eduds2sn',
    //             })
    //         },
    //         target = $(this).find('p').text().trim(),
    //         url = 'http://192.168.240.47:7000/file/?file_name=' + target,
    //
    //     fetch(url, defaultOption).then(function (response) {
    //         wavesurfer.load('/media/audio/80s_vibe.mp3');
    //
    //         $('.linkFile').attr('href',response.url).attr('download',response.url);
    //
    //     })
    // });

}


