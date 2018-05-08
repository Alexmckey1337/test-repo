'use strict';
import URLS from './modules/Urls';
import getData from './modules/Ajax';
import {centerZoomClasterPrint, customPrint} from './modules/Map';
import errHandling from './modules/Error';

$('document').ready(function () {
	const path = window.location.href.split('?')[1];
	let url = (path === undefined) ? URLS.home_group.on_map() : `${URLS.home_group.on_map()}?${path}`;

	function makeInfoContent(hg) {
		let content = `<div class="map_info">
										<p><strong>Домашняя группа:</strong> ${hg.title}</p>
										<p><strong>Церковь:</strong> <a target="_blank" href="/churches/${hg.church.id}">${hg.church.title}</a></p>
										<p><strong>Лидер:</strong> <a target="_blank" href="/account/${hg.leader.id}">${hg.leader.fullname}</a></p>
										<p><strong>К-во людей:</strong> ${hg.count_users}</p>
									</div>`;

		return content;
	}

	getData(url).then(data => {
		data.map((hg, index) => {
			let LatLng = new google.maps.LatLng(hg.latitude, hg.longitude),
				marker = new google.maps.Marker({
					position: LatLng,
					map: map,
					optimized: false,
					title: hg.title
				}),
				infowindow = new google.maps.InfoWindow({
					content: makeInfoContent(hg),
					optimized: false,
				});
			markers.push(marker);
			markers[index].addListener('click', function () {
				infowindow.open(map, marker);
			});
		});
		centerZoomClasterPrint();
	}).catch(err => errHandling(err));

	customPrint();

});