'use strict';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls';
import {postData} from './modules/Ajax';
import errorHandling from './modules/Error';
import {showPromt} from './modules/ShowNotifications';
import {initAddNewUser} from './modules/User/addUser';
import {showAlert} from './modules/ShowNotifications';
import {createNewUser} from './modules/User/addUser';

$(document).ready(function () {
	const
		btnChangeStatus = document.querySelector('#proposalStatus'),
		btnReject = document.querySelector('#proposalReject'),
		btnAdd = document.querySelector('#add'),
		btnSetUser = document.querySelector('#set_user');

	function insertLocality() {
		const elem = document.querySelector('#locInfo');
		if (elem.dataset.id) {
			const
				chooseCity = document.querySelector('#chooseCity'),
				chooseCountry = document.querySelector('#chooseCountry'),
				chooseRegion = document.querySelector('#chooseRegion'),
				chooseDistrict = document.querySelector('#chooseDistrict');
			chooseCity.setAttribute('data-id', elem.dataset.id);
			chooseCity.textContent = elem.dataset.city;
			chooseCountry.textContent = elem.dataset.country;
			chooseRegion.textContent = elem.dataset.area;
			chooseDistrict.textContent = elem.dataset.locality;
		}
	}

	btnChangeStatus && btnChangeStatus.addEventListener('click', function () {
		const
			DATASET = this.dataset,
			ID = DATASET.id,
			URL = (DATASET.type === 'receive') ? URLS.proposal.receive(ID) : URLS.proposal.reopen(ID);

		this.disabled = true;
		postData(URL)
			.then(() => location.reload())
			.catch(err => {
				this.disabled = false;
				errorHandling(err);
			});
	});

	btnReject && btnReject.addEventListener('click', function () {
		const ID = this.dataset.id;
		let self = this;
		self.disabled = true;
		showPromt('Отклонение заявки', 'Введите причину отклонения', '', function (evt, note) {
			if (!note) {
				errorHandling('Не указана причина удаления');
				self.disabled = false;
				return;
			}
			postData(URLS.proposal.reject(ID), {note})
				.then(() => location.reload())
				.catch(err => {
					self.disabled = false;
					errorHandling(err);
				});
		}, () => {
			self.disabled = false;
		});
	});

	btnAdd && btnAdd.addEventListener('click', function () {
		let
			form = document.querySelector('#proposalForm'),
			inputArr = form.querySelectorAll('input'),
			selectArr = form.querySelectorAll('select');
		document.body.classList.add('no_scroll');
		document.querySelector('#addNewUserPopup').classList.add('active');
		document.querySelector('.bg').classList.add('active');
		$(".editprofile-screen").animate({right: '0'}, 300, 'linear');
		initAddNewUser();
		[...inputArr].forEach(item => {
			let name = item.getAttribute('name');
			if (item.value.trim()) {
				if (name === 'phone') {
					let phone = $('#phone');
					phone.val(item.value).next().text(phone.inputmask("getmetadata")["name_ru"]);
				} else {
					document.querySelector(`#${name}`).value = item.value;
				}
			}
		});
		[...selectArr].forEach(item => {
			let name = item.getAttribute('name');
			(item.value.trim()) && $(`#${name}`).val(item.value).trigger('change');
		});
		insertLocality();
		$('#first_name').focusout();
	});

	btnSetUser && btnSetUser.addEventListener('click', function () {
		const
			USER_ID = this.dataset.userId,
			PROPOSAL_ID = this.dataset.proposalId;
		postData(URLS.proposal.process(PROPOSAL_ID), {user: USER_ID})
			.then(() => location.reload())
			.catch(err => errorHandling(err));
	});

	$.validate({
		lang: 'ru',
		form: '#createUser',
		onError: function (form) {
			showAlert(`Введены некорректные данные`);
			let top = $(form).find('div.has-error').first().offset().top;
			$(form).find('.body').animate({scrollTop: top}, 500);
		},
		onSuccess: function () {
			createNewUser((data) => {
				const PROPOSAL_ID = $('#add').attr('data-proposal');
				postData(URLS.proposal.process(PROPOSAL_ID), {user: data.id})
					.then(() => location.reload())
					.catch(err => errorHandling(err));
			}, false);

			return false;
		},
	});

});
