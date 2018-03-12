'use strict';

export const deleteMarkers = function () {
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = [];
};

export const btnLocationControls = function () {
    $('#choose_adress').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        let title = $(this).attr('data-title'),
            lat = $(this).attr('data-lat'),
            lng = $(this).attr('data-lng');
        (lat && lng ) && $('#adress').attr('data-title', title)
            .attr('data-lat', lat)
            .attr('data-lng', lng)
            .text(title);
    });

    $('#address_choose').on('click', function (e) {
        e.preventDefault();
        $(".a-map").addClass('active');
        $('#pac-input').css('display', 'block');
    })

    $('#address_show').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(".a-map").addClass('active');
        $('#pac-input').css('display', 'none');
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

    $('.btnMap').on('click', function () {
        $(".a-map").toggleClass('active');
    })
};