'use strict';
import URLS from './modules/Urls/index';
import getData from "./modules/Ajax/index";
import errorHandling from './modules/Error';

$('document').ready(function () {

    $('#search_city').on('keyup', _.debounce(function () {
        rebuild();
    }, 500));

    $('#cities').on('click', 'li', function () {
       let id = $(this).attr('data-id') || null,
           city = $(this).attr('data-city') || null,
           country = $(this).attr('data-country') || null,
           area = $(this).attr('data-area') || null,
           district = $(this).attr('data-district') || null,
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

    function rebuild() {
        const city = $('#search_city').val();
        if (city.length < 3) return;

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
        }).catch(err => {
            errorHandling(err);
            $('.preloader').css('display', '');
        });
    }

    function renderCities (cities) {
        let li = (cities.length > 0) ?
            cities.map(city => `<li data-id="${city.pk}" 
                                        data-city="${city.city}" 
                                        data-country="${city.country}" 
                                        data-area="${city.area}" 
                                        data-district="${city.district}">
                                        ${city.city} -- ${city.country} -- ${city.area} -- ${city.district}
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
});
