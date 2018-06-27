'use strict';
import URLS from './modules/Urls';
import getData, {postData} from './modules/Ajax';
import errHandling from './modules/Error';
import {showAlert} from './modules/ShowNotifications';

$(document).ready(function () {

	let errMsg = 'При выполнении операции произошла ошибка. Попробуйте еще раз';

	$('table').on('click', '.create_pdf', function () {
		const
			authorID = $(this).data('author-id'),
			url = URLS.generate_tickets_by_author(SUMMIT_ID, authorID);

		getData(url).then(data => console.log(data)).catch(err => errHandling(err));
	});

	$('#toggle_one_entry').on('click', function () {
		$(this).attr('disabled', true);
		postData(toggle_entry_url)
			.then(data => {
				if (data.code == '0') {
					location.reload();
				} else {
					showAlert(errMsg);
				}
				$(this).attr('disabled', false);
			})
			.catch(err => {
				$(this).attr('disabled', false);
				errHandling(err);
			})
	});

	$('#reset_entries').on('click', function () {
		$(this).attr('disabled', true);
		postData('/api/summit_entries/reset/entries/')
			.then(data => {
				showAlert((data.code == '0') ? 'Входы успешно сброшены' : errMsg);
				$(this).attr('disabled', false);
			})
			.catch(err => {
				$(this).attr('disabled', false);
				errHandling(err);
			})
	});

	$('#load_codes').on('click', function () {
		$(this).attr('disabled', true);
		postData('/api/summit_entries/load/codes/')
			.then(data => {
				showAlert((data.code == '0') ? 'Коды успешно добавлены' : errMsg);
				$(this).attr('disabled', false);
			})
			.catch(err => {
				$(this).attr('disabled', false);
				errHandling(err);
			})
	});

	$('#reset_codes').on('click', function () {
		$(this).attr('disabled', true);
		postData('/api/summit_entries/reset/codes/')
			.then(data => {
				showAlert((data.code == '0') ? 'Коды успешно сброшены' : errMsg);
				$(this).attr('disabled', false);
			})
			.catch(err => {
				$(this).attr('disabled', false);
				errHandling(err);
			})
	});

});