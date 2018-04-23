'use strict';
import 'chart.js/dist/Chart.bundle.min.js';
import {CHARTCOLORS, setConfig} from "./config";
import beautifyNumber from '../beautifyNumber';

export function initCharts(data, update, isGroup) {
	let {
		configSexChart,
		selectSexChart,
		optionSexChart,
		configAgeChart,
		optionAgeChart,
		selectAgeChart,
		configPeopleChart,
		optionPeopleChart,
		selectPeopleChart,
	} = makeChartConfig(data, isGroup);
	if (update) {
		updateSexChart(optionSexChart);
		updatePeopleChart(optionPeopleChart);
		updateAgeChart(optionAgeChart);
	} else {
		renderChart(selectSexChart, configSexChart);
		renderChart(selectPeopleChart, configPeopleChart);
		renderChart(selectAgeChart, configAgeChart);
	}
}

function makeChartConfig(data, isGroup = '1m') {
	let labels,
		male = [],
		female = [],
		stableCongr = [],
		unstableCongr = [],
		stableConvert = [],
		unstableConvert = [],
		age1 = [],
		age2 = [],
		age3 = [],
		age4 = [],
		age5 = [],
		ageUnknown = [];

	(isGroup === '1m') ?
		labels = data.map(item => `${item.date.week} нед. ${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`)
		:
		labels = data.map(item => `${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);

	labels.map((item, index) => {
		let elem = data[index].result,
			sex = elem.sex,
			congregation = elem.congregation,
			convert = elem.convert,
			age = elem.age;
		male.push(sex.male);
		female.push(sex.female);
		stableCongr.push(congregation.stable);
		unstableCongr.push(congregation.unstable);
		stableConvert.push(convert.stable);
		unstableConvert.push(convert.unstable);
		age1.push(age['12-']);
		age2.push(age['13-25']);
		age3.push(age['26-40']);
		age4.push(age['41-60']);
		age5.push(age['60+']);
		ageUnknown.push(age['unknown']);
	});

	let datasetsSexChart = [{
			label: "Женщин",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			data: female,
		}, {
			label: "Мужчин",
			borderColor: CHARTCOLORS.green,
			backgroundColor: CHARTCOLORS.green,
			data: male,
		}],
		datasetsPeopleChart = [{
			label: "Стабильные прихожане",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			stack: 'Stack 0',
			data: stableCongr,
		}, {
			label: "Нестабильные прихожане",
			borderColor: CHARTCOLORS.green,
			backgroundColor: CHARTCOLORS.green,
			stack: 'Stack 0',
			data: unstableCongr,
		},
			{
				label: "Стабильные новообращенные",
				borderColor: CHARTCOLORS.blue,
				backgroundColor: CHARTCOLORS.blue,
				stack: 'Stack 1',
				data: stableConvert,
			}, {
				label: "Нестабильные новообращенные",
				borderColor: CHARTCOLORS.orange,
				backgroundColor: CHARTCOLORS.orange,
				stack: 'Stack 1',
				data: unstableConvert,
			}],
		datasetsAgeChart = [{
			label: "12-",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			data: age1,
		},
			{
				label: "13-25",
				borderColor: CHARTCOLORS.orange,
				backgroundColor: CHARTCOLORS.orange,
				data: age2,
			},
			{
				label: "26-40",
				borderColor: CHARTCOLORS.yellow,
				backgroundColor: CHARTCOLORS.yellow,
				data: age3,
			},
			{
				label: "41-60",
				borderColor: CHARTCOLORS.green,
				backgroundColor: CHARTCOLORS.green,
				data: age4,
			},
			{
				label: "60+",
				borderColor: CHARTCOLORS.blue,
				backgroundColor: CHARTCOLORS.blue,
				data: age5,
			},
			{
				label: "Неизвестно",
				borderColor: CHARTCOLORS.salmon,
				backgroundColor: CHARTCOLORS.salmon,
				data: ageUnknown,
			},
		],
		xAxesBar = [{
			stacked: true,
		}],
		yAxesBar = [{
			stacked: true,
		}],
		titleSexChart = "Статистика по полу",
		titlePeopleChart = "Статистика по людям",
		titleAgeChart = "Статистика по возрасту",
		callbackSexChart = {
			footer: (tooltipItems, data) => {
				let female = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
					male = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
					total = +male + +female;
				return `Всего: ${beautifyNumber(total)}`;
			},
		},
		configSexChart = setConfig('bar', labels, datasetsSexChart, titleSexChart, xAxesBar, yAxesBar, callbackSexChart),
		configPeopleChart = setConfig('bar', labels, datasetsPeopleChart, titlePeopleChart),
		configAgeChart = setConfig('bar', labels, datasetsAgeChart, titleAgeChart),
		optionSexChart = {
			chart: window.ChartSex,
			labels: labels,
			l1: female,
			l2: male,
		},
		optionPeopleChart = {
			chart: window.ChartPeople,
			labels: labels,
			l1: stableCongr,
			l2: unstableCongr,
			l3: stableConvert,
			l4: unstableConvert,
		},
		optionAgeChart = {
			chart: window.ChartAge,
			labels: labels,
			l1: age1,
			l2: age2,
			l3: age3,
			l4: age4,
			l5: age5,
			l6: ageUnknown,
		},
		selectSexChart = 'chart_sex',
		selectPeopleChart = 'chart_people',
		selectAgeChart = 'chart_age';

	return {
		configSexChart,
		optionSexChart,
		selectSexChart,
		configAgeChart,
		optionAgeChart,
		selectAgeChart,
		configPeopleChart,
		optionPeopleChart,
		selectPeopleChart,
	}
}

function updateSexChart({chart, labels, l1, l2}) {
	chart.data.labels = labels;
	chart.data.datasets[0].data = l1;
	chart.data.datasets[1].data = l2;
	chart.update();
}

function updatePeopleChart({chart, labels, l1, l2, l3, l4}) {
	chart.data.labels = labels;
	chart.data.datasets[0].data = l1;
	chart.data.datasets[1].data = l2;
	chart.data.datasets[2].data = l3;
	chart.data.datasets[3].data = l4;
	chart.update();
}

function updateAgeChart({chart, labels, l1, l2, l3, l4, l5, l6}) {
	chart.data.labels = labels;
	chart.data.datasets[0].data = l1;
	chart.data.datasets[1].data = l2;
	chart.data.datasets[2].data = l3;
	chart.data.datasets[3].data = l4;
	chart.data.datasets[4].data = l5;
	chart.data.datasets[5].data = l6;
	chart.update();
}

function renderChart(select, config) {
	let ctx = document.getElementById(select).getContext("2d");
	if (select === 'chart_sex') {
		window.ChartSex = new Chart(ctx, config);
	} else if (select === 'chart_age') {
		window.ChartAge = new Chart(ctx, config);
	} else {
		window.ChartPeople = new Chart(ctx, config);
	}
}