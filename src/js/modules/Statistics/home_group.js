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
	getData(`${URLS.event.home_meeting.statistics()}`, config).then(data => {
		$('.preloader').css('display', 'none');
		makeStatsTable(data, config.last);
		initCharts(data, update, config.last);
	})
}

export function makeStatsTable(data, isGroup) {
	let formatedData = getTransformData(data, isGroup),
		tablePeoples = createTable(formatedData.headers, formatedData.dataPeoples, 'Люди'),
		tableAges = createTable(formatedData.headers, formatedData.dataAges, 'Возраст');
	$('#tableHomeStats').html('').append(tablePeoples);
	$('#tableHomeStatsAge').html('').append(tableAges);
}

function getTransformData(data, isGroup = '1m') {
	let dataPeoples = [
			{
				title: 'Всего людей',
			},
			{
				title: 'Мужчин/Женщин',
			},
			{
				title: 'Стабильные/Нестабильные прихожане',
			},
			{
				title: 'Стабильные/Нестабильные новообращенные',
			},
		],
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
			sex = elem.sex,
			congregation = elem.congregation,
			convert = elem.convert,
			age = elem.age;
		dataPeoples[0][item] = +sex.male + +sex.female;
		dataPeoples[1][item] = `${sex.male} / ${sex.female}`;
		dataPeoples[2][item] = `${congregation.stable} / ${congregation.unstable}`;
		dataPeoples[3][item] = `${convert.stable} / ${convert.unstable}`;
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
		dataPeoples
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
                                    				${headers.map(el => `<td>${beautifyNumber(item[el])}</td>`).join('')}
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