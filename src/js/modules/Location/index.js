"use strict";

export function chooseLocation() {
    $(window).on('storage', function (event) {
        if (event.key === 'location') {
            let location = JSON.parse(localStorage.location);
            $('#chooseCity').text(location.city ? location.city : '').attr('data-id', location.id ? location.id : null);
            $('#chooseCountry').text(location.country ? location.country : '');
            $('#chooseRegion').text(location.area ? location.area : '');
            $('#chooseDistrict').text(location.district ? location.district : '');
            localStorage.removeItem('location');
        }
    });

    $('.search_city_link').on('click', function (e) {
        e.preventDefault();
        let link = $(this).attr('href');
        window.open(link, 'searchCity');
    })
}