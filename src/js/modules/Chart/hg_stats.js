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
		configGuestsChart,
		optionGuestsChart,
		selectGuestsChart,
		configFinChart,
		optionFinChart,
		selectFinChart,
	} = makeChartConfig(data, isGroup);
	if (update) {
		updateSexChart(optionSexChart);
		updatePeopleChart(optionPeopleChart);
		updateGuestsChart(optionGuestsChart);
		updateAgeChart(optionAgeChart);
		updatePeopleChart(optionFinChart);
	} else {
		renderChart(selectSexChart, configSexChart);
		renderChart(selectPeopleChart, configPeopleChart);
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
		stableCongr = [],
		unstableCongr = [],
		stableConvert = [],
		unstableConvert = [],
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
		datasetsGuestsChart = [{
			label: "Гости",
			borderColor: CHARTCOLORS.green,
			backgroundColor: CHARTCOLORS.green,
			data: guests,
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
		titlePeopleChart = "Статистика по людям",
		titleAgeChart = "Статистика по возрасту",
		titleGuestsChart = "Cтатистика по гостям",
		titleFinChart = "Cтатистика по пожертвованиям",
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
		configGuestsChart = setConfig('line', labels, datasetsGuestsChart, titleGuestsChart, xAxes, yAxes),
		configAgeChart = setConfig('bar', labels, datasetsAgeChart, titleAgeChart),
		configFinChart = setConfig('bar', labels, datasetsFinChart, titleFinChart),
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
		optionGuestsChart = {
			chart: window.ChartGuests,
			labels: labels,
			l1: guests,
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
		selectPeopleChart = 'chart_people',
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
		configPeopleChart,
		optionPeopleChart,
		selectPeopleChart,
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

function updateGuestsChart({chart, labels, l1}) {
	chart.data.labels = labels;
	chart.data.datasets[0].data = l1;
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
	} else {
		window.ChartPeople = new Chart(ctx, config);
	}
}