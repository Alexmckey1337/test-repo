'use strict';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import URLS from './modules/Urls';
import {postData} from './modules/Ajax';
import errorHandling from './modules/Error';
import {showPromt} from './modules/ShowNotifications';

$(document).ready(function () {
	const
		btnChangeStatus = document.querySelector('#proposalStatus'),
		btnReject = document.querySelector('#proposalReject'),
		btnAdd = document.querySelector('#add');

	btnChangeStatus && btnChangeStatus.addEventListener('click', function () {
		const
			DATASET = this.dataset,
			ID = DATASET.id,
			URL = (DATASET.type === 'receive') ? URLS.event_proposal.receive(ID) : URLS.event_proposal.reopen(ID);

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
			postData(URLS.event_proposal.reject(ID), {note})
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
	});

});
