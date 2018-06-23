'use strict';
import URLS from '../Urls';
import {CONFIG} from '../config';
// import getSearch from '../Search';
import getData from '../Ajax';
import {getPastorsByDepartment} from '../../modules/GetList';
import {getFilterParam} from '../Filter'
import makeSortForm from '../Sort';
import makePagination from '../Pagination';
// import OrderTable from '../Ordering';
import updateHistoryUrl from '../History';
import {getOrderingData} from '../Ordering';
import {getCountFilter} from '../Filter';
import errHandling from '../Error';

const
	USER_ID = document.body.dataset.user,
	table = document.querySelector('#usersStableTable'),
	filterBtn = document.querySelector('#filter_button'),
	filterPopup = document.querySelector('#filterPopup'),
	preloader = document.querySelector('.preloader'),
	tableCount = document.querySelector('.table__count'),
	bg = document.querySelector('.bg'),
	tabs = document.querySelector('#tabs'),
	calendar = document.querySelector('#calendar_range'),
	departmentsFilter = document.querySelector('#department_filter'),
	treeFilter = document.querySelector('#master_tree_filter'),
	churchFilter = document.querySelector('#church_filter'),
	homeGroupFilter = document.querySelector('#hg_filter'),
	masterFilter = document.querySelector('#master_filter'),
	urlPastors = URLS.church.available_pastors(),
	urlChurches = URLS.church.for_select(),
	urlHG = URLS.home_group.for_select(),
	urlUserShort = URLS.user.short();

let init = false;

export function usersStableTable(config = {}) {
	Object.assign(config, getFilterParam(), getOrderingData(), getPreFilterParam());
	updateHistoryUrl(config);
	preloader.style.display = 'block';
	getData(URLS.event.home_meeting.stable_users(), config).then(data => {
		makeUsersStableTable(data, config);
	}).catch(err => {
		preloader.style.display = '';
		errHandling(err);
	});
}

function makeUsersStableTable(data, config = {}) {
	let
		tmpl = document.querySelector('#usersStableTmpl').innerHTML,
		rendered = _.template(tmpl)(data),
		count = data.count,
		pages = Math.ceil(count / CONFIG.pagination_count),
		page = config.page || 1,
		showCount = (count < CONFIG.pagination_count) ? count : data.results.length,
		text = `Показано ${showCount} из ${count}`,
		paginationConfig = {
			container: '.reports__pagination',
			currentPage: page,
			pages: pages,
			callback: usersStableTable
		};
	table.innerHTML = rendered;
	makePagination(paginationConfig);
	makeSortForm(data.table_columns);
	tableCount.textContent = text;
	// new OrderTable().sort(usersStableTable, '.table-wrap th');
	preloader.style.display = '';
}

function getPreFilterParam() {
	let
		week = document.querySelector('#calendar_range').dataset.week,
		type = document.querySelector('#tabs li.active button').dataset.id,
		data = {week};

	(type != 0) && (data.meeting_type = type);

	return data;
}

function initFilterAfterParse(set) {
	[...tabs.querySelectorAll('li')].forEach(tab => tab.classList.remove('active'));
	if (set.meeting_type) {
		tabs.querySelector(`button[data-id='${set.meeting_type}']`).parentNode.classList.add('active');
	} else {
		tabs.querySelector(`button[data-id='0']`).parentNode.classList.add('active');
	}

	if (set.week) {
		let week = set.week;
		calendar.dataset.week = week;

		calendar.value = `${week.slice(-2)} нед. ${week.slice(0,4)}`;
	}

	(set.is_stable) && $('#is_stable_filter').val(set.is_stable).trigger('change');
	(set.hierarchy) && $('#hierarchy_filter').val(set.hierarchy).trigger('change');

	usersStableTable();
	filterBtn.dataset.count = getCountFilter();
}

export function filterInit(set = null) {
	if (!init) {
		if (set != null) {
			initFilterAfterParse(set);
		} else {
			let config = {
				master_tree: USER_ID
			};
			getData(urlPastors, config).then(res => {
				const leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`).join(',');
				appendOptions(treeFilter, leaders);
			});
			getData(urlChurches).then(res => {
				const churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`).join(',');
				appendOptions(churchFilter, churches);
			});
			getData(urlHG).then(res => {
				const groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`).join(',');
				appendOptions(homeGroupFilter, groups);
			});
			getData(urlUserShort).then(data => {
				const users = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
				appendOptions(masterFilter, users);
			});
		}
		init = true;
	}
}

function appendOptions(node, options) {
	while (node.firstChild) {
		node.removeChild(node.firstChild);
	}
	node.insertAdjacentHTML('beforeEnd', '<option>ВСЕ</option>');
	node.insertAdjacentHTML('beforeEnd', options);
}

export function filterChange() {
	$('#department_filter').on('change', function () {
		let
			departamentID = this.value,
			config = {},
			config2 = {};
		if (!departamentID) {
			departamentID = null;
		} else {
			config.department = departamentID;
			config2.department_id = departamentID;
		}
		getPastorsByDepartment(config2).then(function (data) {
			const options = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
			appendOptions(treeFilter, options);
		});
		getData(urlChurches, config2).then(res => {
			let options = res.map(option => `<option value="${option.id}">${option.get_title}</option>`);
			appendOptions(churchFilter, options);
		});
		getData(urlHG, config2).then(res => {
			let options = res.map(option => `<option value="${option.id}">${option.get_title}</option>`);
			appendOptions(homeGroupFilter, options);
		});
		getData(urlUserShort, config).then(data => {
			const options = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
			appendOptions(masterFilter, options);
		});
	});

	$('#master_tree_filter').on('change', function () {
		let
			config = {},
			config2 = {},
			value = this.value,
			departamentID = departmentsFilter.value;
		if ((departamentID != "ВСЕ") && (departamentID != "") && (departamentID != null)) {
			config.department = departamentID;
			config2.department_id = departamentID;
		}
		if ((value != "ВСЕ") && (value != "") && (value != null)) {
			config.master_tree = this.value;
			config2.master_tree = this.value;
		}
		getData(urlChurches, config2).then(res => {
			const options = res.map(option => `<option value="${option.id}">${option.get_title}</option>`);
			appendOptions(churchFilter, options);
		});
		getData(urlHG, config2).then(res => {
			const options = res.map(option => `<option value="${option.id}">${option.get_title}</option>`);
			appendOptions(homeGroupFilter, options);
		});
		getData(urlUserShort, config).then(data => {
			const options = data.map(option => `<option value="${option.id}">${option.fullname}</option>`);
			appendOptions(masterFilter, options);
		});

	});

	$('#church_filter').on('change', function () {
		let config = {},
			value = this.value;
		if ((value != "ВСЕ") && (value != "") && (value != null)) {
			config.church = value;
		}
		getData(urlHG, config).then(res => {
			const options = res.map(option => `<option value="${option.id}">${option.get_title}</option>`);
			appendOptions(homeGroupFilter, options);
		});

	});

}