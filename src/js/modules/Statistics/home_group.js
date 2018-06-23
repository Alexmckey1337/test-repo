'use strict';
import URLS from '../Urls/index';
import {getFilterParam} from "../Filter/index";
import getData from "../Ajax/index";
import updateHistoryUrl from '../History/index';
import beautifyNumber from '../beautifyNumber';
import {initCharts} from "../Chart/hg_stats";

export function homeStatistics(update = false) {
	$('.preloader').css('display', 'block');
	let config = Object.assign({}, getFilterParam(), getPreFilterParam());
	updateHistoryUrl(config);
	(config.last) && (config.group_by = 'month');
	getData(`${URLS.event.home_meeting.meeting_all_stats()}`, config).then(data => {
		$('.preloader').css('display', 'none');
		makeStatsTable(data, config.last);
		initCharts(data, update, config.last);
	})
}

export function makeStatsTable(data, isGroup) {
	let formatedData = getTransformData(data, isGroup),
		tablePeoples = createTable(formatedData.headers, formatedData.dataPeoples, 'Люди'),
		tableFinance = createTable(formatedData.headers, formatedData.dataFinance, 'Пожертвования'),
		tableAges = createTable(formatedData.headers, formatedData.dataAges, 'Возраст');
	$('#tableHomeStats').html('').append(tablePeoples);
	$('#tableHomeStatsFinance').html('').append(tableFinance);
	$('#tableHomeStatsAge').html('').append(tableAges);
}

function getTransformData(data, isGroup = '1m') {
	let dataPeoples = [
			{
				title: 'Всего людей',
			},
			{
				title: 'Гостей',
			},
			{
				title: 'Новых',
			},
			{
				title: 'Покаяний',
			},
			{
				title: 'Мужчин/Женщин',
			},
			{
				title: 'Прихожане: стабильные/нестабильные/неизвестно',
			},
			{
				title: 'Новообращенные: стабильные/нестабильные/неизвестно',
			},
		],
		dataFinance = [{
			title: 'Гривна',
		}, {
			title: 'Рубль',
		}, {
			title: 'Доллар',
		}, {
			title: 'Евро',
		}],
		dataAges = [
			{
				title: '12-',
			},
			{
				title: '13-25',
			},
			{
				title: '26-40',
			},
			{
				title: '41-60',
			},
			{
				title: '60+',
			},
			{
				title: 'Неизвестно',
			}
		],
		headers;

	if (isGroup === '1m') {
		headers = data.map(item => `${item.date.week} нед. ${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);
	} else {
		headers = data.map(item => `${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);
	}

	headers.map((item, index) => {
		let elem = data[index].result,
			money = elem.money,
			sex = elem.sex,
			congregation = elem.congregation,
			convert = elem.convert,
			age = elem.age;
		dataPeoples[0][item] = +sex.male + +sex.female + +sex.unknown;
		dataPeoples[1][item] = elem.guest_count;
		dataPeoples[2][item] = elem.new_count;
		dataPeoples[3][item] = elem.repentance_count;
		dataPeoples[4][item] = `${sex.male} / ${sex.female}`;
		if (isGroup === '1m') {
			dataPeoples[5][item] = {
				type: 'congregation',
				stable: congregation.stable,
				unstable: congregation.unstable,
				unknown: congregation.unknown ? congregation.unknown : 0
			};
			dataPeoples[6][item] = {
				type: 'convert',
				stable: convert.stable,
				unstable: convert.unstable,
				unknown: convert.unknown ? convert.unknown : 0
			};
		} else {
			dataPeoples[5][item] = `${congregation.stable} / ${congregation.unstable} / ${congregation.unknown ? congregation.unknown : 0}`;
			dataPeoples[6][item] = `${convert.stable} / ${convert.unstable} / ${convert.unknown ? convert.unknown : 0}`;
		}
		dataFinance[0][item] = money.uah.total_sum;
		dataFinance[1][item] = money.rur.total_sum;
		dataFinance[2][item] = money.usd.total_sum;
		dataFinance[3][item] = money.eur.total_sum;
		dataAges[0][item] = age['12-'];
		dataAges[1][item] = age['13-25'];
		dataAges[2][item] = age['26-40'];
		dataAges[3][item] = age['41-60'];
		dataAges[4][item] = age['60+'];
		dataAges[5][item] = age['unknown'];
	});
	return {
		headers,
		dataAges,
		dataPeoples,
		dataFinance
	}
}

function createTable(headers, body, title) {
	let table = `<table>
               	<thead>
                	<tr>
                  	<th>${title}</th>
                    	${headers.map(item => `<th>${item}</th>`).join('')}
                  </tr>
                </thead>
                <tbody>
                	${body.map(item => `<tr>
                                    		<td>${item.title}</td>
                                    				${headers.map(el => (typeof item[el] === 'object') ?
		`<td><span class="link" data-path="is_stable=True&week=${el.slice(8,-3)}${el.slice(0,2)}&hierarchy=${item[el].type}">${item[el].stable}</span> / <span class="link" data-path="is_stable=False&week=${el.slice(8,-3)}${el.slice(0,2)}&hierarchy=${item[el].type}">${item[el].unstable}</span> / ${item[el].unknown}</td>`
		:
		`<td>${beautifyNumber(item[el])}</td>`
	).join('')}
                                			</tr>`).join('')}
                </tbody>
              </table>`;

	return table;
}

function getPreFilterParam() {
	let rangeActive = $('.tab-home-stats').find('.range.active'),
		typeActive = $('#tabs').find('li.active').find('button'),
		type = typeActive.attr('data-id'),
		data = {};

	(type != 0) && (data.meeting_type = type);
	rangeActive.length ?
		(data.last = rangeActive.attr('data-range'))
		:
		(data.interval = $('#calendar_range').attr('data-interval'));

	return data;
}