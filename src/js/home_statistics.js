'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import * as moment from 'moment';
import 'moment/locale/ru';
import URLS from './modules/Urls';
import getData from './modules/Ajax';
import {getPastorsByDepartment, getHGLeaders} from "./modules/GetList";
import {applyFilter, refreshFilter} from "./modules/Filter";
import {homeStatistics} from "./modules/Statistics/home_group";
import parseUrlQuery from './modules/ParseUrl';
import {regLegendPlagin} from './modules/Chart/config';

$('document').ready(function () {
	const USER_ID = $('body').data('user'),
		$departmentsFilter = $('#department_filter'),
		$treeFilter = $('#leader_tree_filter'),
		$churchFilter = $('#church_filter'),
		$liderFilter = $('#leader_filter'),
		$homeGroupFilter = $('#hg_filter'),
		urlPastors = URLS.church.available_pastors(),
		urlChurches = URLS.church.for_select(),
		urlHGleaders = URLS.home_group.leaders(),
		urlHG = URLS.home_group.for_select(),
		today = moment().format('MMM YYYY');

	let init = false,
		path = window.location.href.split('?')[1],
		year = moment().year(),
		month = ("0" + (moment().month() + 1)).slice(-2),
		dateInterval = `m:${year}${month}-${year}${month}`;

	moment.locale('ru');

	$('#calendar_range').datepicker({
		autoClose: true,
		view: 'months',
		minView: 'months',
		dateFormat: 'M yyyy',
		maxDate: new Date(),
		onSelect: function (formattedDate, date) {
			if (!date) return;
			let year = moment(date).year(),
				month = ("0" + (moment(date).month() + 1)).slice(-2),
				dateInterval = `m:${year}${month}-${year}${month}`;
			$('#calendar_range').attr('data-interval', dateInterval);
			$('.tab-status ').find('.range').removeClass('active');
			homeStatistics(true);
		}
	}).val(today).attr('data-interval', dateInterval);

	$('.tab-home-stats').find('.range').on('click', function () {
		$(this).closest('.tab-home-stats').find('.range').removeClass('active');
		$(this).addClass('active');
		$('#calendar_range').val('');
		homeStatistics(true);
	});

	$('.tab-home-stats').find('.type').on('click', function () {
		$(this).closest('#tabs').find('li').removeClass('active');
		$(this).parent().addClass('active');
		homeStatistics(true);
	});

	function initFilterAfterParse(set) {
		if (set.meeting_type) {
			$('#tabs').find('li').removeClass('active');
			$('#tabs').find(`button[data-id='${set.meeting_type}']`).parent().addClass('active');
		} else {
			$('#tabs').find('li').removeClass('active');
			$('#tabs').find(`button[data-id='0']`).parent().addClass('active');
		}
		if (set.last) {
			$('.tab-home-stats').find('.range').removeClass('active');
			$('.tab-home-stats').find(`.range[data-range='${set.last}']`).addClass('active');
		}
		if (set.interval) {
			let year = set.interval.split('-')[1].slice(0, 4),
				month = set.interval.split('-')[1].slice(4),
				date = moment(`${+month}-${+year}`, "MM-YYYY").format('MMM YYYY');

			$('#calendar_range').attr('data-interval', set.interval).val(date);
		}

		$departmentsFilter.val(set.department).trigger('change');
		(async () => {
			if (set.department) {
				let config = {
						department: set.department
					},
					config2 = {
						department_id: set.department
					};
				await getData(urlPastors, config2).then(function (res) {
					const pastors = res.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
					$treeFilter.html('<option>ВСЕ</option>').append(pastors);
					return res;
				});
				await getData(urlChurches, config2).then(res => {
					let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
					$churchFilter.html('<option>ВСЕ</option>').append(churches);
					return res;
				});
				await getData(urlHG, config2).then(res => {
					let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
					$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
					return res;
				});
				await getData(urlHGleaders, config).then(res => {
					let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
					$liderFilter.html('<option>ВСЕ</option>').append(liders);
					return res;
				});
			} else {
				let config = {
					master_tree: USER_ID
				};
				await getData(urlPastors, config).then(res => {
					let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
					$treeFilter.html('<option>ВСЕ</option>').append(leaders);
					return res;
				});
				await getData(urlChurches).then(res => {
					let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
					$churchFilter.html('<option>ВСЕ</option>').append(churches);
					return res;
				});
				await getData(urlHG).then(res => {
					let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
					$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
					return res;
				});
				await getData(urlHGleaders).then(res => {
					let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
					$liderFilter.html('<option>ВСЕ</option>').append(liders);
					return res;
				});
			}
			if (set.leader_tree) {
				$treeFilter.val(set.leader_tree).trigger('change');
				let config = {
					master_tree: set.leader_tree
				};
				await getData(urlChurches, config).then(res => {
					let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
					$churchFilter.html('<option>ВСЕ</option>').append(churches);
					return res;
				});
				await getData(urlHG, config).then(res => {
					let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
					$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
					return res;
				});
				await getData(urlHGleaders, config).then(res => {
					let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
					$liderFilter.html('<option>ВСЕ</option>').append(liders);
					return res;
				});
			}
			if (set.church) {
				$churchFilter.val(set.church).trigger('change');
				let config = {
						church: set.church
					},
					config2 = {
						church_id: set.church
					};
				await getData(urlHG, config2).then(res => {
					let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
					$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
					return res;
				});
				await getData(urlHGleaders, config).then(res => {
					let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
					$liderFilter.html('<option>ВСЕ</option>').append(liders);
					return res;
				});
			}
			if (set.leader) {
				$liderFilter.val(set.leader).trigger('change');
				let config = {
					leader_id: set.leader
				};
				await getData(urlHG, config).then(res => {
					let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
					$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
					return res;
				});
			}
			(set.hg) && $homeGroupFilter.val(set.hg).trigger('change');
			// $('.apply-filter').trigger('click');
			homeStatistics();
			filterChange();
		})();
	}

	function filterInit(set = null) {
		if (!init) {
			if (set != null) {
				initFilterAfterParse(set);
			} else {
				let config = {
					master_tree: USER_ID
				};
				getData(urlPastors, config).then(res => {
					let leaders = res.map(leader => `<option value="${leader.id}">${leader.fullname}</option>`);
					$treeFilter.html('<option>ВСЕ</option>').append(leaders);
				});
				getData(urlChurches).then(res => {
					let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
					$churchFilter.html('<option>ВСЕ</option>').append(churches);
				});
				getData(urlHG).then(res => {
					let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
					$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
				});
				getData(urlHGleaders).then(res => {
					let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
					$liderFilter.html('<option>ВСЕ</option>').append(liders);
				});
			}
			init = true;
		}
	}

	$('.selectdb').select2();

	//Filter
	$('#filter_button').on('click', function () {
		filterInit();
		$('#filterPopup').addClass('active');
		$('.bg').addClass('active');
	});

	$('.clear-filter').on('click', function () {
		refreshFilter(this);
	});

	$('.apply-filter').on('click', function () {
		applyFilter(this, homeStatistics);
	});

	function filterChange() {
		$departmentsFilter.on('change', function () {
			let departamentID = $(this).val();
			let config = {},
				config2 = {};
			if (!departamentID) {
				departamentID = null;
			} else {
				config.department = departamentID;
				config2.department_id = departamentID;
			}
			getPastorsByDepartment(config2).then(function (data) {
				const pastors = data.map(pastor => `<option value="${pastor.id}">${pastor.fullname}</option>`);
				$treeFilter.html('<option>ВСЕ</option>').append(pastors);
			});
			getData(urlChurches, config2).then(res => {
				let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
				$churchFilter.html('<option>ВСЕ</option>').append(churches);
			});
			getData(urlHG, config2).then(res => {
				let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
				$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
			});
			getHGLeaders(config).then(res => {
				let leaders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
				$liderFilter.html('<option>ВСЕ</option>').append(leaders);
			});
		});

		$treeFilter.on('change', function () {
			let config = {},
				config2 = {},
				departamentID = $departmentsFilter.val();
			if ((departamentID != "ВСЕ") && (departamentID != "") && (departamentID != null)) {
				config.department = departamentID;
				config2.department_id = departamentID;
			}
			if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
				config.master_tree = $(this).val();
				config2.master_tree = $(this).val();
			}
			getData(urlChurches, config2).then(res => {
				let churches = res.map(church => `<option value="${church.id}">${church.get_title}</option>`);
				$churchFilter.html('<option>ВСЕ</option>').append(churches);
			});
			getData(urlHG, config2).then(res => {
				let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
				$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
			});
			getHGLeaders(config).then(res => {
				let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
				$liderFilter.html('<option>ВСЕ</option>').append(liders);
			});
		});

		$churchFilter.on('change', function () {
			let config = {},
				config2 = {};
			if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
				config.church = $(this).val();
				config2.church_id = $(this).val();
			}
			getData(urlHG, config2).then(res => {
				let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
				$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
			});
			getHGLeaders(config).then(res => {
				let liders = res.map(lider => `<option value="${lider.id}">${lider.fullname}</option>`);
				$liderFilter.html('<option>ВСЕ</option>').append(liders);
			});
		});

		$liderFilter.on('change', function () {
			let config = {};
			if (($(this).val() != "ВСЕ") && ($(this).val() != "") && ($(this).val() != null)) {
				config.leader_id = $(this).val();
			}
			getData(urlHG, config).then(res => {
				let groups = res.map(group => `<option value="${group.id}">${group.get_title}</option>`);
				$homeGroupFilter.html('<option>ВСЕ</option>').append(groups);
			});
		});
	}

	//Parsing URL
	if (path === undefined) {
		homeStatistics();
		filterChange();
	} else {
		let filterParam = parseUrlQuery();
		console.log(filterParam);
		filterInit(filterParam);
	}

	regLegendPlagin();

});
