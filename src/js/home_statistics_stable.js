'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import URLS from './modules/Urls';
import getData from './modules/Ajax';
import updateSettings from './modules/UpdateSettings';
import parseUrlQuery from './modules/ParseUrl';
import {applyFilter, refreshFilter} from './modules/Filter';

function ready() {
	const
		USER_ID = document.querySelector('body').dataset.user,
		filterBtn = document.querySelector('#filter_button'),
		filterClearBtn = document.querySelector('.clear-filter'),
		filterApplyBtn = document.querySelector('.apply-filter'),
		filterPopup = document.querySelector('#filterPopup'),
		sortBtn = document.querySelector('#sort_save'),
		fullSearch = document.querySelector('input[name="fullsearch"]'),
		preloader = document.querySelector('.preloader'),
		PATH = window.location.href.split('?')[1];
	let
		init = false;

	function filterInit(set = null) {
		if (!init) {
			console.log(set);
			if (set != null) {

			} else {

			}
			init = true;
		}
	}

	//Parsing URL
	if (PATH == undefined) {
		HomeLiderReportsTable();
	} else {
		let filterParam = parseUrlQuery();
		filterInit(filterParam);
	}

	$('.selectdb').select2();

	// Sort table
	sortBtn.addEventListener('click', () => {
		preloader.style.display = 'block';
		updateSettings(HomeLiderReportsTable, 'meeting_summary');
	});

	//Search
	fullSearch.addEventListener('keyup', _.debounce(function () {
		preloader.style.display = 'block';
		homeLiderReportsTable();
	}, 500));

	//Filter
	filterBtn.addEventListener('click', () => {
		filterInit();
		filterPopup.style.display = 'block';
	});

	filterClearBtn.addEventListener('click', function () {
		refreshFilter(this);
	});

	filterApplyBtn.addEventListener('click', function () {
		applyFilter(this, homeLiderReportsTable);
	});

}

document.addEventListener('DOMContentLoaded', ready);
