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
		configCongregationChart,
		optionCongregationChart,
		selectCongregationChart,
		configConvertChart,
		optionConvertChart,
		selectConvertChart,
		configGuestsChart,
		optionGuestsChart,
		selectGuestsChart,
		configFinChart,
		optionFinChart,
		selectFinChart,
	} = makeChartConfig(data, isGroup);
	if (update) {
		updateSexChart(optionSexChart);
		updateGuestsChart(optionCongregationChart);
		updateGuestsChart(optionConvertChart);
		updateGuestsChart(optionGuestsChart);
		updateAgeChart(optionAgeChart);
		updatePeopleChart(optionFinChart);
	} else {
		renderChart(selectSexChart, configSexChart);
		renderChart(selectCongregationChart, configCongregationChart);
		renderChart(selectConvertChart, configConvertChart);
		renderChart(selectGuestsChart, configGuestsChart);
		renderChart(selectAgeChart, configAgeChart);
		renderChart(selectFinChart, configFinChart);
	}
}

function makeChartConfig(data, isGroup = '1m') {
	let labels,
		male = [],
		female = [],
		guests = [],
		newPeople = [],
		repentance = [],
		stableCongr = [],
		unstableCongr = [],
		unknwCongr = [],
		stableConvert = [],
		unstableConvert = [],
		unkwnConvert = [],
		age1 = [],
		age2 = [],
		age3 = [],
		age4 = [],
		age5 = [],
		ageUnknown = [],
		uah = [],
		rur = [],
		usd = [],
		eur = [];

	(isGroup === '1m') ?
		labels = data.map(item => `${item.date.week} нед. ${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`)
		:
		labels = data.map(item => `${item.date.year}-${(item.date.month < 10) ? '0' + item.date.month : item.date.month}`);

	labels.map((item, index) => {
		let elem = data[index].result,
			sex = elem.sex,
			money = elem.money,
			congregation = elem.congregation,
			convert = elem.convert,
			age = elem.age;
		male.push(sex.male);
		female.push(sex.female);
		guests.push(elem.guest_count);
		newPeople.push(elem.new_count);
		repentance.push(elem.repentance_count);
		stableCongr.push(congregation.stable);
		unstableCongr.push(congregation.unstable);
		unknwCongr.push(congregation.unknown ? congregation.unknown : 0);
		stableConvert.push(convert.stable);
		unstableConvert.push(convert.unstable);
		unkwnConvert.push(convert.unknown ? convert.unknown : 0);
		age1.push(age['12-']);
		age2.push(age['13-25']);
		age3.push(age['26-40']);
		age4.push(age['41-60']);
		age5.push(age['60+']);
		ageUnknown.push(age['unknown']);
		uah.push(money.uah.total_sum);
		rur.push(money.rur.total_sum);
		usd.push(money.usd.total_sum);
		eur.push(money.eur.total_sum);
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
		datasetsCongregationChart = [{
			label: "Стабильные",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			stack: 'Stack 0',
			data: stableCongr,
		}, {
			label: "Нестабильные",
			borderColor: CHARTCOLORS.green,
			backgroundColor: CHARTCOLORS.green,
			stack: 'Stack 0',
			data: unstableCongr,
		}, {
			label: "Неизвестно",
			borderColor: CHARTCOLORS.blue,
			backgroundColor: CHARTCOLORS.blue,
			stack: 'Stack 0',
			data: unknwCongr,
		}],
		datasetsConvertChart = [{
			label: "Стабильные",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			stack: 'Stack 0',
			data: stableConvert,
		}, {
			label: "Нестабильные",
			borderColor: CHARTCOLORS.green,
			backgroundColor: CHARTCOLORS.green,
			stack: 'Stack 0',
			data: unkwnConvert,
		}, {
			label: "Неизвестно",
			borderColor: CHARTCOLORS.blue,
			backgroundColor: CHARTCOLORS.blue,
			stack: 'Stack 0',
			data: unkwnConvert,
		}],
		datasetsGuestsChart = [{
			label: "Гости",
			borderColor: CHARTCOLORS.green,
			backgroundColor: CHARTCOLORS.green,
			data: guests,
			lineTension: 0,
			fill: false,
		}, {
			label: "Новые",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			data: newPeople,
			lineTension: 0,
			fill: false,
		}, {
			label: "Покаяния",
			borderColor: CHARTCOLORS.orange,
			backgroundColor: CHARTCOLORS.orange,
			data: repentance,
			lineTension: 0,
			fill: false,
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
		datasetsFinChart = [{
			label: "грн",
			borderColor: CHARTCOLORS.red,
			backgroundColor: CHARTCOLORS.red,
			data: uah,
		},
			{
				label: "руб.",
				borderColor: CHARTCOLORS.orange,
				backgroundColor: CHARTCOLORS.orange,
				data: rur,
			},
			{
				label: "дол.",
				borderColor: CHARTCOLORS.blue,
				backgroundColor: CHARTCOLORS.blue,
				data: usd,
			},
			{
				label: "евро.",
				borderColor: CHARTCOLORS.green,
				backgroundColor: CHARTCOLORS.green,
				data: eur,
			}],
		xAxesBar = [{
			stacked: true,
		}],
		yAxesBar = [{
			stacked: true,
		}],
		xAxes = [{
			display: true,
			scaleLabel: {
				show: true,
				labelString: 'Day'
			}
		}],
		yAxes = [{
			display: true,
			scaleLabel: {
				show: true,
				labelString: 'Value'
			}
		}],
		titleSexChart = "Статистика по полу",
		titleCongregationChart = "Статистика по стабильным прихожанам",
		titleConvertChart = "Статистика по стабильным новообращенным",
		titleAgeChart = "Статистика по возрасту",
		titleGuestsChart = "Cтатистика по людям",
		titleFinChart = "Cтатистика по пожертвованиям",
		callbackSexChart = {
			footer: (tooltipItems, data) => {
				let female = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
					male = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
					total = +male + +female;
				return `Всего: ${beautifyNumber(total)}`;
			},
		},
		callbackStableChart = {
			footer: (tooltipItems, data) => {
				let
					stable = data.datasets[tooltipItems[0].datasetIndex].data[tooltipItems[0].index],
					unstable = data.datasets[tooltipItems[1].datasetIndex].data[tooltipItems[1].index],
					unknown = data.datasets[tooltipItems[2].datasetIndex].data[tooltipItems[2].index],
					total = +stable + +unstable + +unknown;
				return `Всего: ${beautifyNumber(total)}`;
			},
		},
		configSexChart = setConfig('bar', labels, datasetsSexChart, titleSexChart, xAxesBar, yAxesBar, callbackSexChart),
		configCongregationChart = setConfig('bar', labels, datasetsCongregationChart, titleCongregationChart, xAxesBar, yAxesBar, callbackStableChart),
		configConvertChart = setConfig('bar', labels, datasetsConvertChart, titleConvertChart, xAxesBar, yAxesBar, callbackStableChart),
		configGuestsChart = setConfig('line', labels, datasetsGuestsChart, titleGuestsChart, xAxes, yAxes),
		configAgeChart = setConfig('bar', labels, datasetsAgeChart, titleAgeChart),
		configFinChart = setConfig('bar', labels, datasetsFinChart, titleFinChart),
		optionSexChart = {
			chart: window.ChartSex,
			labels: labels,
			l1: female,
			l2: male,
		},
		optionCongregationChart = {
			chart: window.ChartCongr,
			labels: labels,
			l1: stableCongr,
			l2: unstableCongr,
			l3: unknwCongr,
		},
		optionConvertChart = {
			chart: window.ChartConvert,
			labels: labels,
			l1: stableConvert,
			l2: unknwCongr,
			l3: unkwnConvert,
		},
		optionGuestsChart = {
			chart: window.ChartGuests,
			labels: labels,
			l1: guests,
			l2: newPeople,
			l3: repentance,
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
		optionFinChart = {
			chart: window.ChartFin,
			labels: labels,
			l1: uah,
			l2: rur,
			l3: usd,
			l4: eur,
		},
		selectSexChart = 'chart_sex',
		selectCongregationChart = 'chart_congregation',
		selectConvertChart = 'chart_convert',
		selectGuestsChart = 'chart_guests',
		selectAgeChart = 'chart_age',
		selectFinChart = 'chart_finance';

	return {
		configSexChart,
		optionSexChart,
		selectSexChart,
		configAgeChart,
		optionAgeChart,
		selectAgeChart,
		configCongregationChart,
		optionCongregationChart,
		selectCongregationChart,
		configConvertChart,
		optionConvertChart,
		selectConvertChart,
		configGuestsChart,
		optionGuestsChart,
		selectGuestsChart,
		configFinChart,
		optionFinChart,
		selectFinChart
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

function updateGuestsChart({chart, labels, l1, l2, l3}) {
	chart.data.labels = labels;
	chart.data.datasets[0].data = l1;
	chart.data.datasets[1].data = l2;
	chart.data.datasets[2].data = l3;
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
	} else if (select === 'chart_guests') {
		window.ChartGuests = new Chart(ctx, config);
	} else if (select === 'chart_finance') {
		window.ChartFin = new Chart(ctx, config);
	} else if (select === 'chart_congregation') {
		window.ChartCongr = new Chart(ctx, config);
	} else if (select === 'chart_convert') {
		window.ChartConvert = new Chart(ctx, config);
	}
}