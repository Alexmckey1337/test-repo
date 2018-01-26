'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'whatwg-fetch';
import URLS from '../Urls/index';
import {CONFIG} from "../config";
import WaveSurfer from 'wavesurfer.js';
import {getFilterParam} from "../Filter/index";
import {postData, getDataPhone, getAudioFile} from '../Ajax/index';
import getSearch from '../Search/index';
import OrderTable from '../Ordering/index';
import makePagination from '../Pagination/index';
import updateHistoryUrl from '../History/index';
import makeSelect from '../MakeAjaxSelect/index';

function parseFunc(data, params) {
    params.page = params.page || 1;
    const results = [];
    data.results.forEach(function makeResults(element) {
        results.push({
            id: element.id,
            name: element.title,
        });
    });
    return {
        results: results,
        pagination: {
            more: (params.page * 100) < data.count
        }
    };
}
function formatRepo(data) {
    if (data.id === '') {
        return 'ВСЕ';
    } else {
        return `<option value="${data.id}">${data.name}</option>`;
    }
}

export function PhoneTable(config) {
    getDataPhone(URLS.phone.list(), config).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText');
            $('#tablePhone').append(err);
        } else {
            makePhoneTable(data);
        }
    });

}

function makePhoneTable(data, config = {}) {
    let count = data.pages,
        page = config['page'] || 1,
        pages = Math.ceil(count / CONFIG.pagination_count),
        showCount = (count < CONFIG.pagination_count) ? count : data.result.length,
        text = `Показано ${showCount} из ${count}`,
        paginationConfig = {
            container: ".users__pagination",
            currentPage: page,
            pages: pages,
            callback: makePhoneTable
        };
    makePagination(paginationConfig);
    $('.table__count').text(text);
    $('#tablePhoneWrap').html('');
    makeIptelTable(data, '#tablePhoneWrap');
    new OrderTable().sort(phoneTable, ".table-wrap th");
    $('.preloader').hide();
}

export function phoneTable(config = {}) {
    Object.assign(config, getSearch('search_fio'));
    Object.assign(config, getFilterParam());
    updateHistoryUrl(config);
    getDataPhone(URLS.phone.list(), config).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText');
            $('#tablePhone').append(err);
        } else {
            makePhoneTable(data, config);
        }
    });
}

function addUserToPhone(data, block) {
    console.log(data);
    let wrap = `${data.result.map(item => {
        return `<form class="form-addUser">
                    <p class="form-addUser__phone">${item.extension}</p>
                    <label>
                        <input class="${(item.fullname != null) ? 'inputPh active' : 'inputPh'}" type="text" value="${(item.fullname != null) ? item.fullname : ''}" disabled>
                        <select name="user" class="${(item.fullname != null) ? 'selectPh' : 'selectPh active'}"></select>
                    </label>
                    <button class="${(item.fullname != null) ? 'add' : 'add active'}" type="submit" disabled></button>
                    <button class="${(item.fullname != null) ? 'change active' : 'change'}" type="button"></button>
                    <button class="close" type="button"></button>
                    <span class="saved">Сохранено</span>
                </form>`;
    }).join('')}`;
    $(block).append(wrap);
    $('.selectPh').on('change', function () {
        $(this).parent().parent().find('.add').removeAttr('disabled');
    });
    $('.change').on('click', function () {
        $(this).removeClass('active');
        $(this).parent().children('.add').addClass('active');
        $(this).parent().children('.close').addClass('active');
        $(this).parent().find('.inputPh').removeClass('active');
        $(this).parent().find('.selectPh').addClass('active');
        makeSelect($('.selectPh.active'), '/api/users/for_select/', parseFunc, formatRepo);
    });
    $('.close').on('click', function () {
        $(this).removeClass('active');
        $(this).parent().children('.change').addClass('active');
        $(this).parent().find('.inputPh').addClass('active');
        $(this).parent().children('.add').removeClass('active');
        $(this).parent().find('.selectPh').removeClass('active').select2('destroy');
    });
    $('.form-addUser').on('submit', function (e) {
        e.preventDefault();
        let phone = $(this).find('.form-addUser__phone').text(),
            userId = $(this).find('.selectPh').val(),
            data = {
                "user_id": userId,
                "extension": phone
            };
        postData(URLS.phone.changeUser(), data).then(() => {
            let userName = $(this).find('span option[value=' + userId + ']').text();
            console.log(userName);
            $(this).find('.add').removeClass('active');
            $(this).find('.close').removeClass('active');
            $(this).find('.change').addClass('active');
            $(this).find('.inputPh').addClass('active').val(userName);
            $(this).find('.selectPh').removeClass('active').select2('destroy');
            $(this).find('.saved').addClass('active');
            setTimeout(function () {
                $(this).find('.saved').removeClass('active');
            }, 1000);
        });
    });
    makeSelect($('.selectPh.active'), '/api/users/for_select/', parseFunc, formatRepo);
}

export function getDataUserPhone() {
    $('#tableAddUserToPhone').html('');
    getDataPhone(URLS.phone.user()).then(data => {
        if (data.status === '503') {
            let err = document.createElement('p');
            $(err).text(data.message).addClass('errorText');
            $('#popupAddUserToPhone').find('.main-text').append(err);
        } else {
            addUserToPhone(data, '#tableAddUserToPhone');
        }
    });
}

export function makeIptelTable(data,block) {
    let table = `<table class="tableIptel">
                        <thead>
                            <tr>
                                <th>Тип</th>
                                <th>Дата</th>
                                <th>Кто</th>
                                <th>Кому</th>                                        
                                <th>Длительность (сек)</th>
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
                             <td class="recordIptel" data-url='${item.record}'>
                                <div class="playerControll load">
                                    <i class="material-icons btnPlay">&#xE039;</i>
                                    <i class="material-icons btnStop">&#xE036;</i>
                                </div>
                                <a href="#" class="downloadFile"><i class="material-icons">&#xE2C4;</i></a>
                            </td>
                        </tr>
                            `;
    }).join('')}</tbody>
                        </table>`;
    $(block).append(table);
    btnPlayrecord();
    btnDownloadRecord();
    btnClosePlayer();
}
function btnClosePlayer() {
    $('.closePlayer').on('click',function(){
        wavesurfer.stop();
        $('#wavesurferPlayer').css({
            'display':'none'
        });
        $('.playerControll').removeClass('active').addClass('load');
    })
}

function btnPlayrecord() {
    $('.playerControll').on('click', function () {
        let file = $(this).parent().attr('data-url').trim(),
        btnPlay = $('.playerControll').not(this);
        getAudioFile(URLS.phone.play(file)).then(myBlob => {
            let objectURL = URL.createObjectURL(myBlob),
                player = $(this).parent().parent().parent().parent().parent().find('#wavesurferPlayer'),
                playerHeight = parseInt($(this).parent().parent().height()),
                playerPosition = $(this).parent().parent().position(),
                playerWidth = parseInt($(this).parent().parent().width()) - parseInt($(this).parent().width()) - 22;
            console.log($(player));

            $(btnPlay).addClass('load').removeClass('active');
            $(player).css({
                'height':playerHeight,
                'width':playerWidth,
                'display': 'block',
                'left': playerPosition.left + 'px',
                'top': playerPosition.top + 'px'

            });
            $('#wavesurfer').find('wave').css({
                'height': playerHeight + 'px',
                'width':playerWidth + 'px'

            });
            $(this).toggleClass('active');
            if ($(this).hasClass('load')) {
                $(this).removeClass('load');
                wavesurfer.load(objectURL);
            } else {
                wavesurfer.playPause();
            }
        }).catch(err => errorHandling(err));
    });
}

function btnDownloadRecord() {
    $('.downloadFile').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        let file = $(this).closest('td').attr('data-url').trim(),
            a = document.createElement("a");
        $('body').append(a);
        a.style = "display: none";
        $('body').append(a);
        getAudioFile(URLS.phone.play(file)).then(myBlob => {
            let url = window.URL.createObjectURL(myBlob);
            a.href = url;
            a.download = `audio-record-${myBlob.size}`;
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        }).catch(err => errorHandling(err));
    });
}


//PLAYER
    let m,
        s,
        totalTime,
        timeJump,
        currentTime,
        currentTimeJump,
        wavesurfer = WaveSurfer.create({
            barWidth: 1,
            container: '#wavesurfer',
            cursorWidth: 0,
            dragSelection: true,
            height: 500,
            hideScrollbar: true,
            interact: true,
            normalize: true,
            waveColor: 'rgba(101,109,112,0.25)',
            progressColor: '#3caeda'
    });

    $('#wavesurferPlayer').on('click', '#play', function () {
        if ($(this).hasClass('load')) {
            let url = $(this).attr('data-url');
            $(this).removeClass('load');
            wavesurfer.load(url);
        } else {
            wavesurfer.playPause();
        }
    });

    function getMinutes(convTime) {
        convTime = Number(convTime);
        m = Math.floor(convTime % 3600 / 60);
        return ((m < 10 ? "0" : "") + m);
    }

    function getSeconds(convTime) {
        convTime = Number(convTime);
        s = Math.floor(convTime % 3600 % 60);
        return ((s < 10 ? "0" : "") + s);
    }

    wavesurfer.on('ready', function () {
        totalTime = wavesurfer.getDuration();
        timeJump = 300 / totalTime;
        $('.wavesurfer__elem').addClass('show');
        $('.button__loader').fadeOut();
        $('.time__minutes').text(getMinutes(totalTime));
        $('.time__seconds').text(getSeconds(totalTime));
        $('.time, .progress').fadeIn();

        //Volume controls for player

        let volumeInput = $('#button__volume'),
            onChangeVolume = function (e) {
                e.stopPropagation();
                wavesurfer.setVolume(e.target.value);
            };
        wavesurfer.setVolume(1);
        volumeInput.val(wavesurfer.backend.getVolume());
        volumeInput.on('input', onChangeVolume);
        volumeInput.on('change', onChangeVolume);

        wavesurfer.play();
    });

    function progressJump() {
        currentTime = wavesurfer.getCurrentTime();
        currentTimeJump = currentTime * timeJump + 10;
        $('.progress__button').css({left: currentTimeJump + 'px'});
        $('.progress__indicator').css({width: currentTimeJump + 'px'});

        $('.time__minutes').text(getMinutes(currentTime));
        $('.time__seconds').text(getSeconds(currentTime));
    }

    wavesurfer.on('audioprocess', function () {
        progressJump();
    });

    wavesurfer.on('pause', function () {
        $('.button__play-iconplay').fadeIn();
        $('.button__play-iconpause').fadeOut();
        $('.recordplayer').removeClass('play');
        $('.recordplayer__disc').removeClass('animate');
    });

    wavesurfer.on('play', function () {
        $('.button__play-iconplay').fadeOut();
        $('.button__play-iconpause').fadeIn();
        $('.recordplayer').addClass('play');
        $('.recordplayer__disc').addClass('animate');
    });

    wavesurfer.on('loading', function (event) {
        $('.button__loader').css({height: event + 'px'});
    });

    // wavesurfer.on('seek', function (event) {
    //     progressJump();
    //     console.log('HERE');
    // });

