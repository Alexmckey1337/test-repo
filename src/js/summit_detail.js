'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import 'inputmask/dist/inputmask/dependencyLibs/inputmask.dependencyLib.jquery.js';
import 'inputmask/dist/inputmask/inputmask.js';
import 'inputmask/dist/inputmask/jquery.inputmask.js';
import 'inputmask/dist/inputmask/inputmask.phone.extensions.js';
import 'inputmask/dist/inputmask/phone-codes/phone.js';
import URLS from './modules/Urls/index';
import getData, {deleteData, postData} from "./modules/Ajax/index";
import ajaxRequest from './modules/Ajax/ajaxRequest';
import {applyFilter, refreshFilter} from "./modules/Filter/index";
import updateSettings from './modules/UpdateSettings/index';
import exportTableData from './modules/Export/index';
import {showAlert, showConfirm} from "./modules/ShowNotifications/index";
import reverseDate from './modules/Date';
import {convertNum} from "./modules/ConvertNum/index";
import {
	createSummitUsersTable,
	updateSummitUsersTable,
	unsubscribeOfSummit,
	updateSummitParticipant,
	registerUser,
	makePotencialSammitUsersList,
	addUserToSummit,
} from "./modules/Summit/index";
import {closePopup} from "./modules/Popup/popup";
import {initAddNewUser, createNewUser} from "./modules/User/addUser";
import {makePastorListNew, makePastorListWithMasterTree} from "./modules/MakeList/index";
import errHandling from './modules/Error';
import validateEmail from './modules/validateEmail';

$(document).ready(function () {
	const $summitUsersList = $('#summitUsersList');
	const SUMMIT_ID = $summitUsersList.data('summit');

	function makeSummitInfo() {
		let width = 150,
			count = 1,
			position = 0,
			$carousel = $('#carousel'),
			$list = $carousel.find('ul'),
			$listElements;
		$listElements = $list.find('li');
		$carousel.find('.arrow-left').on('click', function () {
			position = Math.min(position + width * count, 0);

			$($list).css({
				marginLeft: position + 'px'
			});
		});

		$carousel.find('.arrow-right').on('click', function () {
			position = Math.max(position - width * count, -width * ($listElements.length - 3));
			$($list).css({
				marginLeft: position + 'px'
			});
		});
	}

	$('#export_table').on('click', function () {
		exportTableData(this);
	});

	createSummitUsersTable({summit: SUMMIT_ID});

	makeSummitInfo();
	$('body').on('click', '#carousel li span', function () {
		$('#carousel').find('li').removeClass('active');
		$(this).parent().addClass('active')
	});

	$("#close").on('click', function () {
		$('#popup').css('display', 'none');
		$('.choose-user-wrap').css('display', 'block');
	});

	$("#closeDelete").on('click', function () {
		$('#popupDelete').css('display', 'none');
	});

	$('#popup-create_payment').find('.pop_cont').on('click', function (e) {
		e.stopPropagation();
	});

	$(".add-user-wrap .top-text span").on('click', function () {
		$('.add-user-wrap').css('display', '');
	});

	$("#load-tickets").on('click', function () {
		let summit_id = $('#summitUsersList').data('summit');
		ajaxRequest(URLS.generate_summit_tickets(summit_id), null, function (data) {
			console.log(data);
		}, 'GET', true, {
			'Content-Type': 'application/json'
		});
	});

	$(".add-user-wrap").on('click', function (el) {
		if (el.target !== this) {
			return;
		}
		$('.add-user-wrap').css('display', '');
	});

	$("#popupDelete").on('click', function (el) {
		if (el.target !== this) {
			return;
		}
		$('#popupDelete').css('display', '');
	});

	$("#popupDelete .top-text span").on('click', function (el) {
		$('#popupDelete').css('display', '');
	});

	$(".choose-user-wrap").on('click', function (el) {
		if (el.target !== this) {
			return;
		}
		$('.choose-user-wrap').css('display', '');
		$('searchUsers').val('');
		$('.choose-user-wrap .splash-screen').removeClass('active');
	});

	$(".choose-user-wrap .top-text > span").on('click', function () {
		$('searchUsers').val('');
		$('.choose-user-wrap .splash-screen').removeClass('active');
		$('.choose-user-wrap').css('display', '');
	});

	$('.choose-user-wrap h3 span').on('click', function () {
		$('searchUsers').val('');
		$('.choose-user-wrap .splash-screen').removeClass('active');
		$('.choose-user-wrap').css('display', '');
		$('.add-user-wrap').css('display', 'block');
		$('#choose').on('click', function () {
			$('.choose-user-wrap').css('display', 'block');
			$('.add-user-wrap').css('display', '');
		});
	});

	$('#addNewUser').on('click', function () {
		$(this).closest('.popup').css('display', 'none');
		$('#addNewUserPopup').addClass('active');
		$('.bg').addClass('active');
	});

	$('#changeSum').on('click', function () {
		$('#summit-value').removeAttr('readonly');
		$('#summit-value').focus();
	});

	$('#changeSumDelete').on('click', function () {
		$('#summit-valueDelete').removeAttr('readonly');
		$('#summit-valueDelete').focus();
	});

	$('#preDeleteAnket').on('click', function () {
		let anketID = $(this).attr('data-anket'),
			fullName = $('#fullNameCard').text();
		getData(URLS.summit_profile.predelete(anketID)).then(function (data) {
			let keys = Object.keys(data),
				msg = `<h3>${fullName}</h3>
                            <ul class="info">
                                ${keys.map(item => `<li><strong>${item}:</strong> ${data[item].length}</li>`).join('')}
                            </ul>`;
			showConfirm('Подтверждение удаления', msg, function () {
				deleteData(URLS.summit_profile.detail(anketID)).then(() => {
					showAlert('Пользователь удален из саммита');
					$('.preloader').css('display', 'block');
					createSummitUsersTable({summit: SUMMIT_ID});
				}).catch(err => errHandling(err));
			}, _ => {
			});
		}).catch(err => errHandling(err));
		closePopup(this);
	});

	$('yes').on('click', function () {
		let summitAnketID = $(this).attr('data-anket');
		$('#deletePopup').css('display', '');
		unsubscribeOfSummit(summitAnketID);
	});

	$('#deletePopup').click(function (el) {
		if (el.target != this) {
			return;
		}
		$(this).hide();
	});

	$('#no').click(function () {
		$('#deletePopup').hide();
	});

	$('#deletePopup .top-text span').click(function () {
		$('#deletePopup').hide();
	});

	$('#applyChanges').on('click', function () {
		let profileID = $(this).data('id');
		let formData = $('#participantInfoForm').serializeArray();
		let data = {};

		formData.forEach(function (item) {
			data[item.name] = (item.value == 'on') ? true : item.value;
		});

		updateSummitParticipant(profileID, data);
		closePopup(this);
	});

	$('#complete').on('click', function () {
		let userID = $('#popup').attr('data-id');
		registerUser(userID, SUMMIT_ID);
	});

	$('#department_filter').select2().on('select2:open', function () {
		$('.select2-search__field').focus();
	});
	$('.selectdb').select2().on('select2:open', function () {
		$('.select2-search__field').focus();
	});

	//    Events
	$("#add").on('click', function () {
		initAddNewUser();
		$(".editprofile-screen").animate({right: '0'}, 300, 'linear');
		$('#searchedUsers').html('');
		$('#searchUsers').val('');
		$('.choose-user-wrap .splash-screen').removeClass('active');
		$('#searchedUsers').css('height', 'auto');
		$('#chooseUserINBases').css('display', 'block');
		document.querySelector('#searchUsers').focus();
	});

	//Filter
	$('.apply-filter').on('click', function () {
		applyFilter(this, createSummitUsersTable);
	});

	$('.clear-filter').on('click', function () {
		refreshFilter(this);
	});

	$('#department_filter').on('change', function () {
		$('#author_tree_filter').prop('disabled', true);
		let department_id = parseInt($(this).val()) || null;
		makePastorListNew(department_id, SUMMIT_ID, ['#author_tree_filter', '#author_filter']);
	});

	$('#author_tree_filter').on('change', function () {
		$('#author_filter').prop('disabled', true);
		let config = {};
		let author_tree = parseInt($(this).val());
		if (!isNaN(author_tree)) {
			config = {author_tree: author_tree}
		}
		makePastorListWithMasterTree(config, SUMMIT_ID, ['#author_filter'], null);
	});

	$('input[name="fullsearch"]').on('keyup', _.debounce(function (e) {
		$('.preloader').css('display', 'block');
		createSummitUsersTable({summit: SUMMIT_ID, page: 1});
	}, 500));

	$('#searchUsers').on('keyup', _.debounce(function () {
		makePotencialSammitUsersList();
	}, 500));

	$('#summitsTypes').find('li').on('click', function () {
		$('.preloader').css('display', 'block');
		let config = {};
		config.summit = $(this).data('id');
		config.page = 1;
		createSummitUsersTable(config);
	});

	$('#sort_save').on('click', function () {
		$('.preloader').css('display', 'block');
		updateSettings(createSummitUsersTable, 'summit');
	});

	$('#filter_button').on('click', function () {
		$('#filterPopup').addClass('active');
		$('.bg').addClass('active');
	});

	$.validate({
		lang: 'ru',
		form: '#createUser',
		onSuccess: function (form) {
			if ($(form).attr('name') == 'createUser') {
				$(form).find('#saveNew').attr('disabled', true);
				createNewUser();
			}
			return false; // Will stop the submission of the form
		}
	});

	$('#filterPopup').find('.pop_cont').on('click', function (e) {
		e.stopPropagation();
	});

	$('.select_date_filter').datepicker({
		dateFormat: 'yyyy-mm-dd',
		autoClose: true
	});

	$('#summitUsersList').on('click', '.ticket_status', _.debounce(function (e) {
		let option = {
			method: 'POST',
			credentials: "same-origin",
			headers: new Headers({
				'Content-Type': 'application/json',
			})
		};
		const profileId = $(this).data('user-id');
		fetch(URLS.summit_profile.set_ticket_status(profileId), option)
			.then(res => res.json())
			.then(data => {
				$(this).find('.text').text(data.text);
				if (data.new_status == 'given' || data.new_status == 'print') {
					$(this).find('div').show();
					(data.new_status == 'given') ? $(this).find('input').prop('checked', true) : $(this).find('input').prop('checked', false);
				} else {
					$(this).find('div').hide();
				}
			})

	}, 300));

	$('#send_codes').on('click', function () {
		$(this).attr('disabled', true);
		getData(URLS.summit.send_codes(SUMMIT_ID)).then(data => {
			$('#send_codes').attr('disabled', false);
			let msg = `<p class="text_row">Количество поставленых в очередь писем: <strong>${data.sent_count}</strong></p>
                       <p class="text_row">Количество пользователей без email: <strong>${data.users_without_emails_count}</strong></p>`;
			showAlert(msg);
		}).catch(err => {
			$('#send_codes').attr('disabled', false);
			showAlert('При запросе на сервер произошла ошибка. Попробуйте позже');
			console.log(err);
		});
	});

	$('#send_schedules').on('click', function () {
		$(this).attr('disabled', true);
		getData(URLS.summit.send_schedules(SUMMIT_ID)).then(data => {
			$('#send_schedules').attr('disabled', false);
			let msg = `<p class="text_row">Количество поставленых в очередь писем: <strong>${data.sent_count}</strong></p>
                       <p class="text_row">Количество пользователей без email: <strong>${data.users_without_emails_count}</strong></p>`;
			showAlert(msg);
		}).catch(err => {
			$('#send_schedules').attr('disabled', false);
			showAlert('При запросе на сервер произошла ошибка. Попробуйте позже');
			console.log(err);
		});
	});

	//Add user to summit
	$('#searchedUsers').on('click', '.add_participant', function () {
		const ID = $(this).attr('data-id');
		addUserToSummit(ID);
	});

	//Update user info
	$('#popup .popup_body').on('click', '.edit', function (e) {
		e.preventDefault();
		if ($(this).hasClass('active')) {
			$(this).removeClass('active');
			$(this).siblings('input').prop('readonly', true);
			$(this).parent().find('.save__info').removeClass('active');
			$(this).parent().find('.comment').text('');
		} else {
			$(this).siblings('input').prop('readonly', false);
			$(this).addClass('active');
			$(this).parent().find('.save__info').addClass('active');
		}
	});

	$('#client_phone').inputmask('phone', {
		onKeyValidation: function () {
			$(this).next().text($(this).inputmask("getmetadata")["name_ru"]);
		},
	});

	$('#popup .popup_body').on('click', '.save__info', function (e) {
		e.preventDefault();
		const USER_ID = $('#popup').attr('data-id');
		let config = {},
			input = $(this).siblings('input'),
			name = input.attr('name');

		if (name === 'phone_number') {
			if (input.inputmask("isComplete")) {
				config[name] = input.inputmask('unmaskedvalue');
			} else {
				showAlert('Номер телефона некорректный');
				return;
			}
		} else {
			if (validateEmail(input.val())) {
				config[name] = input.val();
			} else {
				showAlert('Email некорректный');
				return;
			}
		}
		postData(URLS.user.detail(USER_ID), config, {method: 'PATCH'}).then(_ => {
			showAlert('Изменения внесены');
			$(this).removeClass('active');
			$(this).siblings('input').prop('readonly', true);
			$(this).parent().find('.edit').removeClass('active');
			$(this).parent().find('.comment').text('');
		}).catch(err => errHandling(err));
	});

	//Payments
	function submitPayment() {
		let id = $('#complete-payment').attr('data-id'),
			data = {
				"rate": convertNum($('#new_payment_rate').val(), '.'),
				"operation": $('#operation').val(),
				"sum": convertNum($('#new_payment_sum').val(), '.'),
				"currency": $('#new_payment_currency').val(),
				"sent_date": reverseDate($('#sent_date').val(), '-'),
				"description": $('#popup-create_payment textarea').val(),
			},
			url = URLS.summit_profile.create_payment(id);

		postData(url, data).then(function () {
			updateSummitUsersTable();
			showAlert('Оплата прошла успешно.');
			$('#new_payment_sum').val('');
			$('#popup-create_payment textarea').val('');
			$('#complete-payment').prop('disabled', false);
			$('#popup-create_payment').css('display', 'none');
		}).catch(err => {
			errHandling(err);
			$('#complete-payment').prop('disabled', false);
		});
	}

	$.validate({
		lang: 'ru',
		form: '#payment-form',
		onError: function () {
			showAlert(`Введены некорректные данные либо заполнены не все поля`)
		},
		onSuccess: function () {
			submitPayment();
			$('#complete-payment').prop('disabled', true);

			return false;
		}
	});

	$("#close-payments").on('click', function () {
		$('#popup-payments').css('display', 'none');
		$('#popup-payments table').html('');
	});

	$("#close-payment").on('click', function (e) {
		e.preventDefault();
		$('#new_payment_rate').val(1);
		$('#in_user_currency').text('');
		$('#popup-create_payment').css('display', 'none');
	});

	$('#sent_date').datepicker({
		dateFormat: "dd.mm.yyyy",
		startDate: new Date(),
		maxDate: new Date(),
		autoClose: true
	});

	$('#payment-form').on("submit", function (e) {
		e.preventDefault();
	});

});