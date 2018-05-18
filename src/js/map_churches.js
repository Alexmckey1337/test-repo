'use strict';
import URLS from './modules/Urls';
import getData from './modules/Ajax';
import {centerZoomClasterPrint, customPrint} from './modules/Map';
import errHandling from './modules/Error';

$('document').ready(function () {
	const path = window.location.href.split('?')[1];
	let url = (path === undefined) ? URLS.church.on_map() : `${URLS.church.on_map()}?${path}`;

	function makeInfoContent(church) {
		let content = `<div class="map_info">
										<p><strong>Церковь:</strong> <a target="_blank" href="/churches/${church.id}">${church.title}</a></p>
										<p><strong>Пастор:</strong> <a target="_blank" href="/account/${church.pastor.id}">${church.pastor.fullname}</a></p>
										<p><strong>К-во дом. групп:</strong> ${church.count_home_groups}</p>
										<p><strong>К-во людей:</strong> ${church.count_people}</p>
									</div>`;

		return content;
	}

	getData(url).then(data => {
		data.map((church, index) => {
			let LatLng = new google.maps.LatLng(church.latitude, church.longitude),
				marker = new google.maps.Marker({
					position: LatLng,
					map: map,
					optimized: false,
					title: church.title
				}),
				infowindow = new google.maps.InfoWindow({
					content: makeInfoContent(church),
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