'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import moment from 'moment/min/moment.min.js';
import updateSettings from './modules/UpdateSettings';
import parseUrlQuery from './modules/ParseUrl';
import {applyFilter, refreshFilter} from './modules/Filter';
import {usersStableTable, filterInit, filterChange} from './modules/Reports/meetings_users';

function ready() {
	const
		YEAR = moment().format('YYYY'),
		WEEK = moment().isoWeek(),
		filterBtn = document.querySelector('#filter_button'),
		filterClearBtn = document.querySelector('.clear-filter'),
		filterApplyBtn = document.querySelector('.apply-filter'),
		filterPopup = document.querySelector('#filterPopup'),
		sortBtn = document.querySelector('#sort_save'),
		preloader = document.querySelector('.preloader'),
		bg = document.querySelector('.bg'),
		calendar = document.querySelector('#calendar_range'),
		PATH = window.location.href.split('?')[1];

	calendar.dataset.week = `${YEAR}${WEEK}`;
	calendar.value = `${WEEK} нед. ${YEAR}`;

	$('#calendar_range').datepicker({
		autoClose: true,
		maxDate: new Date(),
		onSelect: function (formattedDate, date) {
			if (date) {
				let
					year = moment(date).year(),
					week = moment(date).isoWeek();

				calendar.value = `${week} нед. ${year}`;
				calendar.dataset.week = `${year}${week}`;
			} else {
				calendar.dataset.week = `${YEAR}${WEEK}`;
				calendar.value = `${WEEK} нед. ${YEAR}`;
			}
			usersStableTable();
		}
	});

	//Parsing URL
	if (PATH === undefined) {
		usersStableTable();
		filterChange();
	} else {
		filterInit(parseUrlQuery());
	}

	$('.selectdb').select2();

	// Sort table
	sortBtn.addEventListener('click', () => {
		preloader.style.display = 'block';
		updateSettings(usersStableTable, 'unstable_user');
	});

	//Events
	$('.tab-home-stable').find('.type').on('click', function () {
		$(this).closest('#tabs').find('li').removeClass('active');
		$(this).parent().addClass('active');
		usersStableTable();
	});

	//Filter
	filterBtn.addEventListener('click', () => {
		filterInit();
		filterPopup.classList.add('active');
		bg.classList.add('active');
	});

	filterClearBtn.addEventListener('click', function () {
		refreshFilter(this);
	});

	filterApplyBtn.addEventListener('click', function () {
		applyFilter(this, usersStableTable);
	});

}

document.addEventListener('DOMContentLoaded', ready);
