'use strict';
import URLS from './modules/Urls/index';
import getData from "./modules/Ajax/index";
import parseUrlQuery from './modules/ParseUrl/index';
import {deleteMarkers} from "./modules/Map/index";

$('document').ready(function () {
    const path = window.location.href.split('?')[1];

    $('#search_city').on('keyup', _.debounce(function () {
        rebuild();
    }, 800));

    $('#cities').on('click', 'li', function () {
       let id = $(this).find('span').attr('data-id') || null,
           city = $(this).find('span').attr('data-city') || null,
           country = $(this).find('span').attr('data-country') || null,
           area = $(this).find('span').attr('data-area') || null,
           district = $(this).find('span').attr('data-district') || null,
           location = {
               id,
               city,
               country,
               area,
               district
           };
        localStorage.location = JSON.stringify(location);
        window.close();
    });

    $('#cities').on('click', 'button', function (e) {
        if (!$('#map-popup').hasClass('active')) {
            $('#map-popup').addClass('active');
        }
        e.stopPropagation();
        let lat = +$(this).attr('data-lat'),
            lng = +$(this).attr('data-lng'),
            title = $(this).attr('data-title'),
            LatLng = new google.maps.LatLng(lat, lng);
        deleteMarkers();
        marker = new google.maps.Marker({
            position: LatLng,
            map: map,
            title: title
        });
        map.setCenter(LatLng);
        markers.push(marker);
    });

    $('#countries, #areas, #districts').on('click', 'li', function () {
       let item = $(this).find('span').text(),
           container = $(this).closest('ul').attr('id');
       $('.selected_block').find(`span[data-id="${container}"]`).text(item);
        rebuild();
    });

    $('.selected_block').on('click', 'span', function () {
        $(this).text('');
        rebuild();
    });

    $(".btnMap").on('click', function () {
       $('#map-popup').toggleClass('active');
    });

    function rebuild() {
        const city = $('#search_city').val();
        if (city.length < 1) return;

        let country = $('#selected_country').text(),
            area = $('#selected_area').text(),
            district = $('#selected_district').text(),
            options = {city};
        $('.preloader').css('display', 'block');
        country && (options.country = country);
        area && (options.area = area);
        district && (options.district = district);
        getData(URLS.town(), options).then(data => {
            renderCities(data.cities);
            renderHelperChoose(data.filters.countries, '#countries');
            renderHelperChoose(data.filters.areas, '#areas');
            renderHelperChoose(data.filters.districts, '#districts');
            $('.preloader').css('display', '');
        }).catch(_ => $('.preloader').css('display', ''));
    }

    function renderCities (cities) {
        let li = (cities.length > 0) ?
            cities.map(city => `<li>
                                    <span data-id="${city.pk}"
                                    data-city="${city.city}"
                                    data-country="${city.country}"
                                    data-area="${city.area}"
                                    data-district="${city.district}">
                                    ${city.city} -- ${city.country} -- ${city.area} -- ${city.district}
                                    </span>
                                    ${(city.location.lat !=null && city.location.lon != null) ?
                                        `<button data-title="${city.city} - ${city.country} - ${city.area} - ${city.district}"
                                            data-lat="${city.location.lat}"
                                            data-lng="${city.location.lon}">
                                        <i class="material-icons">&#xE55B;</i>
                                    </button>`
                                    :
                                        ''
                                    }
                                   
                                </li>`).join('')
            :
            `<li>Результат отсутствует</li>`;
        $('#cities').html(li);
    }

    function renderHelperChoose (items, selector) {
        let li = (items.length > 0) ?
            items.map(item => `<li><span>${item.name}</span> -- ${item.count}</li>`).join('')
            :
            `<li>Результат отсутствует</li>`;
        $(selector).html(li);
    }

    function initCity(set) {
        let city = set.old_city.replace('_', ' ');
        $('#search_city').val(city);
        rebuild();
    }

    //Parsing URL
    if (path != undefined) {
        let filterParam = parseUrlQuery();
        initCity(filterParam);
    }
});