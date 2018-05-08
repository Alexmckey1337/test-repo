'use strict';
import html2canvas from 'html2canvas';

const mapSelector = document.querySelector('#google_map');

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
	});

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

export function centerZoomClasterPrint() {
	let bounds = (markers.length > 0) ? createBoundsForMarkers(markers) : null;
	map.setCenter(bounds.getCenter());
	map.fitBounds(bounds);
	if (map.getZoom() > 15) {
		map.setZoom(15);
	}
	setTimeout(function () {
		new MarkerClusterer(map, markers, {imagePath: imgClasterPath});
		map.controls[google.maps.ControlPosition.TOP_RIGHT].push(printMapControl(map));
	}, 100);
}

function createBoundsForMarkers(markers) {
	let bounds = new google.maps.LatLngBounds();
	$.each(markers, function () {
		bounds.extend(this.getPosition());
	});

	return bounds;
}

function printMapControl() {
	if (!isCanvasSupported()) {
		return null;
	}
	let controlDiv = printMapButton("Печать", "printMap");
	google.maps.event.addDomListener(controlDiv, "click", print);
	return controlDiv;
}

export function customPrint() {

	(function () {
		let afterPrint = function () {
			let canvas = document.querySelector('canvas');
			canvas && canvas.parentNode.removeChild(canvas);
			document.querySelector('#google_map').classList.remove('print');
		};

		if (window.matchMedia) {
			let mediaQueryList = window.matchMedia('print');
			mediaQueryList.addListener(function (mql) {
				if (!mql.matches) {
					afterPrint();
				}
			});
		}

		window.onafterprint = afterPrint;
	}());

	document.addEventListener("keydown", keyDownHandler, false);

	function keyDownHandler(e) {
		console.log(e);
		let keyCode = e.keyCode;
		if ((e.ctrlKey || e.metaKey) && keyCode == 80) {
			e.preventDefault();
			print();

			return false;
		}
	}
}

function print() {
	let transform;
	if (window.chrome) {// Fix for Chrome
		transform = $(".gm-style>div:first>div").css("transform");
		let comp = transform.split(","), //split up the transform matrix
			mapleft = parseFloat(comp[4]), //get left value
			maptop = parseFloat(comp[5]);  //get top value
		$(".gm-style>div:first>div").css({ //get the map container. not sure if stable
			"transform": "none",
			"left": mapleft,
			"top": maptop,
		});
	}
	html2canvas($('#google_map').get(0), {
		useCORS: true,
	})
		.then(canvas => {
			document.body.appendChild(canvas);
			if (window.chrome) {// Fix for Chrome
				$(".gm-style>div:first>div").css({
					left: 0,
					top: 0,
					"transform": transform
				});
			}
			let printContent = document.querySelector('canvas');
			mapSelector.classList.add('print');
			printContent.style.width = '297mm';
			printContent.style.height = 'auto';
			window.print();
		});
}

function isCanvasSupported() {
	const elem = document.createElement("canvas");
	return !!(elem.getContext && elem.getContext("2d"));
}

function printMapButton(text, className) {
	const controlDiv = document.createElement("div");
	controlDiv.className = className;
	controlDiv.index = 1;
	controlDiv.style.padding = "10px";
	// set CSS for the control border.
	const controlUi = document.createElement("div");
	controlUi.style.backgroundColor = "rgb(255, 255, 255)";
	controlUi.style.color = "#565656";
	controlUi.style.cursor = "pointer";
	controlUi.style.textAlign = "center";
	controlUi.style.boxShadow = "rgba(0, 0, 0, 0.298039) 0px 1px 4px -1px";
	controlDiv.appendChild(controlUi);
	// set CSS for the control interior.
	const controlText = document.createElement("div");
	controlText.style.fontFamily = "Roboto,Arial,sans-serif";
	controlText.style.fontSize = "11px";
	controlText.style.paddingTop = "8px";
	controlText.style.paddingBottom = "8px";
	controlText.style.paddingLeft = "8px";
	controlText.style.paddingRight = "8px";
	controlText.innerHTML = text;
	controlUi.appendChild(controlText);
	$(controlUi).on("mouseenter", function () {
		controlUi.style.backgroundColor = "rgb(235, 235, 235)";
		controlUi.style.color = "#000";
	});
	$(controlUi).on("mouseleave", function () {
		controlUi.style.backgroundColor = "rgb(255, 255, 255)";
		controlUi.style.color = "#565656";
	});
	return controlDiv;
}

