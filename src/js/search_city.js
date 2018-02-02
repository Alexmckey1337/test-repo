'use strict';

$('document').ready(function () {
    $('#search_city').on('keyup', _.debounce(function (e) {
        rebuild();
    }, 500));
    $('#countries').on('click', 'ul li', function () {
       let country = $(this).find('span').text();
       $('.selected_block').append(`<span class="selected_country">${country}</span>`);
        rebuild();
    });
    $('#areas').on('click', 'ul li', function () {
        let area = $(this).find('span').text();
        $('.selected_block').append(`<span class="selected_area">${area}</span>`);
        rebuild();
    });
    $('#districts').on('click', 'ul li', function () {
        let district = $(this).find('span').text();
        $('.selected_block').append(`<span class="selected_district">${district}</span>`);
        rebuild();
    });
    $('.selected_block').on('click', 'span', function () {
        $(this).remove();
        rebuild();
    });
    function rebuild() {
        const city = $('#search_city').val();
        const $country = $('.selected_country');
        const $area = $('.selected_area');
        const $district = $('.selected_district');
        let country = Array();
        let area = Array();
        let district = Array();

        if (city.length < 3) {
            return
        }
        $country.each(function (i) {
            country.push($(this).text())
        });
        $area.each(function (i) {
            area.push($(this).text())
        });
        $district.each(function (i) {
            district.push($(this).text())
        });
        // console.log(city);
        // console.log(country);
        // console.log(area);
        let url = '/api/city/';
        let options = {
            'city': city,
        };
        if (country.length > 0) {
            options.country = country
        }
        if (area.length > 0) {
            options.area = area
        }
        if (district.length > 0) {
            options.district = district
        }
        let keys = Object.keys(options);
        if (keys.length) {
            url += '?';
            keys.forEach(item => {
                if (options[item] instanceof Array) {
                    options[item].forEach(i => {
                        url += item + '=' + i + "&"
                    });
                } else {
                    url += item + '=' + options[item] + "&"
                }
            });
        }
        let defaultOption = {
            method: 'GET',
            credentials: 'same-origin',
            headers: new Headers({
                'Content-Type': 'application/json',
            })
        };
        let initConfig = Object.assign({}, defaultOption, {});

        fetch(url, initConfig).then(resp => {
            if (resp.status >= 200 && resp.status < 300) {
                return resp.json();
            } else {
                return resp.json().then(err => {
                    throw err;
                });
            }
        }).then(data => {
            let cities = data.cities,
                countries = data.filters.countries,
                districts = data.filters.districts,
                areas = data.filters.areas;
            $('#cities').html(buildCities(cities));
            $('#countries').html(buildCountries(countries));
            $('#areas').html(buildAreas(areas));
            $('#districts').html(buildDistricts(districts));
        });
    }
    function buildCities(cities) {
        let html = '<ul>';
        cities.forEach(function(city) {
            html += `<li>${city.city} -- ${city.country} -- ${city.area} -- ${city.district} (${city.score})`;
        });
        html += '</ul>';
        return html
    }
    function buildCountries(countries) {
        let html = '<ul>';
        countries.forEach(function(country) {
            html += `<li><span>${country.name}</span> -- ${country.count}`;
        });
        html += '</ul>';
        return html
    }
    function buildAreas(areas) {
        let html = '<ul>';
        areas.forEach(function(area) {
            html += `<li><span>${area.name}</span> -- ${area.count}`;
        });
        html += '</ul>';
        return html
    }
    function buildDistricts(districts) {
        let html = '<ul>';
        districts.forEach(function(d) {
            html += `<li><span>${d.name}</span> -- ${d.count}`;
        });
        html += '</ul>';
        return html
    }
});
