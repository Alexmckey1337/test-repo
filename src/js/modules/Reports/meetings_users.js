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
	liderFilter = document.querySelector('#leader_filter'),
	homeGroupFilter = document.querySelector('#hg_filter'),
	masterFilter = document.querySelector('#master_filter'),
	urlPastors = URLS.church.available_pastors(),
	urlChurches = URLS.church.for_select(),
	urlHGleaders = URLS.home_group.leaders(),
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

function appendOptions(node, options) {
	while (node.firstChild) {
		node.removeChild(node.firstChild);
	}
	node.insertAdjacentHTML('beforeEnd', '<option>ВСЕ</option>');
	node.insertAdjacentHTML('beforeEnd', options);
}

function createSelect(data, filterSelector, name = 'fullname') {
	const options = data.map(option => `<option value="${option.id}">${option[name]}</option>`).join(',');
	appendOptions(filterSelector, options);

	return options;
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
		calendar.value = `${week.slice(-2)} нед. ${week.slice(0, 4)}`;
	}

	(set.attended) && setSelectValue('attended_filter', set.attended);
	(set.convert) && setSelectValue('convert_filter', set.convert);
	(set.is_stable) && setSelectValue('is_stable_filter', set.is_stable);
	(set.sex) && setSelectValue('sex_filter', set.sex);
	(set.hierarchy) && setSelectValue('hierarchy_filter', set.hierarchy);
	(set.department) && setSelectValue('department_filter', set.department);

	(async () => {
		if (set.department) {
			let
				config = {
					department: set.department
				},
				config2 = {
					department_id: set.department
				};
			await getData(urlPastors, config2).then(data => createSelect(data, treeFilter));
			await getData(urlChurches, config2).then(data => createSelect(data, churchFilter, 'get_title'));
			await getData(urlHG, config2).then(data => createSelect(data, homeGroupFilter, 'get_title'));
			await getData(urlHGleaders, config).then(data => createSelect(data, liderFilter));
			await getData(urlUserShort, config).then(data => createSelect(data, masterFilter));
		} else {
			await getData(urlPastors, {master_tree: USER_ID}).then(data => createSelect(data, treeFilter));
			await getData(urlChurches).then(data => createSelect(data, churchFilter, 'get_title'));
			await getData(urlHG).then(data => createSelect(data, homeGroupFilter, 'get_title'));
			await getData(urlUserShort).then(data => createSelect(data, masterFilter));
			await getData(urlHGleaders).then(data => createSelect(data, liderFilter));
		}

		if (set.master_tree || set.leader_tree) {
			setSelectValue('master_tree_filter', set.master_tree || set.leader_tree);
			let config = {
				master_tree: set.master_tree || set.leader_tree
			};
			await getData(urlChurches, config).then(data => createSelect(data, churchFilter, 'get_title'));
			await getData(urlHG, config).then(data => createSelect(data, homeGroupFilter, 'get_title'));
			await getData(urlHGleaders, config).then(data => createSelect(data, liderFilter));
			await getData(urlUserShort, config).then(data => createSelect(data, masterFilter));
		}
		if (set.church) {
			setSelectValue('church_filter', set.church);
			let
				config = {
					church: set.church
				},
				config2 = {
					church_id: set.church
				};
			await getData(urlHG, config2).then(data => createSelect(data, homeGroupFilter, 'get_title'));
			await getData(urlHGleaders, config).then(data => createSelect(data, liderFilter));
			await getData(urlUserShort, config).then(data => createSelect(data, masterFilter));
		}
		if (set.leader) {
			setSelectValue('leader_filter', set.leader);
			let
				config = {
				leader_id: set.leader
			};
			await getData(urlHG, config).then(data => createSelect(data, homeGroupFilter, 'get_title'));
		}
		(set.hg) && setSelectValue('hg_filter', set.hg);
		(set.master) && setSelectValue('master_filter', set.master);
		usersStableTable();
		filterBtn.dataset.count = getCountFilter();
		filterChange();
	})();
}

function setSelectValue(selector, value) {
	$(`#${selector}`).val(value).trigger('change');
}

export function filterInit(set = null) {
	if (!init) {
		if (set != null) {
			preloader.style.display = 'block';
			initFilterAfterParse(set);
		} else {
			getData(urlPastors, {master_tree: USER_ID}).then(data => createSelect(data, treeFilter));
			getData(urlChurches).then(data => createSelect(data, churchFilter, 'get_title'));
			getData(urlHG).then(data => createSelect(data, homeGroupFilter, 'get_title'));
			getData(urlUserShort).then(data => createSelect(data, masterFilter));
			getData(urlHGleaders).then(data => createSelect(data, liderFilter));
			filterChange();
		}
		init = true;
	}
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
		getPastorsByDepartment(config2).then(data => createSelect(data, treeFilter));
		getData(urlChurches, config2).then(data => createSelect(data, churchFilter, 'get_title'));
		getData(urlHGleaders, config).then(data => createSelect(data, liderFilter));
		getData(urlHG, config2).then(data => createSelect(data, homeGroupFilter, 'get_title'));
		getData(urlUserShort, config).then(data => createSelect(data, masterFilter));
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
		getData(urlChurches, config2).then(data => createSelect(data, churchFilter, 'get_title'));
		getData(urlHGleaders, config).then(data => createSelect(data, liderFilter));
		getData(urlHG, config2).then(data => createSelect(data, homeGroupFilter, 'get_title'));
		getData(urlUserShort, config).then(data => createSelect(data, masterFilter));
	});

	$('#church_filter').on('change', function () {
		let
			config = {},
			config2 = {},
			value = this.value;
		if ((value != "ВСЕ") && (value != "") && (value != null)) {
			config.church = value;
			config2.church_id = value;
		}
		getData(urlHG, config2).then(data => createSelect(data, homeGroupFilter, 'get_title'));
		getData(urlHGleaders, config).then(data => createSelect(data, liderFilter));
	});

	$('#leader_filter').on('change', function () {
		let
			config = {},
			value = this.value;
		if ((value != "ВСЕ") && (value != "") && (value != null)) {
			config.leader_id = value;
		}
		getData(urlHG, config).then(data => createSelect(data, liderFilter, 'get_title'));
	});
}