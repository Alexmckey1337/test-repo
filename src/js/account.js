'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'select2';
import 'select2/dist/css/select2.css';
import 'cropper';
import 'cropper/dist/cropper.css';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import 'hint.css/hint.min.css';
import 'inputmask/dist/inputmask/dependencyLibs/inputmask.dependencyLib.jquery.js';
import 'inputmask/dist/inputmask/inputmask.js';
import 'inputmask/dist/inputmask/jquery.inputmask.js';
import 'inputmask/dist/inputmask/inputmask.phone.extensions.js';
import 'inputmask/dist/inputmask/phone-codes/phone.js';
import errorHandling from './modules/Error';
import moment from 'moment';
import 'moment/locale/ru';
import {updateOrCreatePartner, updateUser} from './modules/User/updateUser';
import {makeChurches, makeResponsibleList} from './modules/MakeList/index';
import makeSelect from './modules/MakeAjaxSelect';
import getLastId from './modules/GetLastId/index';
import {setCookie} from './modules/Cookie/cookie';
import {deleteData, postData} from "./modules/Ajax/index";
import ajaxRequest from './modules/Ajax/ajaxRequest';
import URLS from './modules/Urls/index';
import {CONFIG} from './modules/config';
import {showAlert, showConfirm} from './modules/ShowNotifications/index';
import {createPayment} from './modules/Payment/index';
import {
	changeLessonStatus,
	initLocationSelect,
	sendNote,
	dataIptelTable,
	dataIptelMonth
} from './modules/Account/index';
import {addUserToChurch, addUserToHomeGroup} from './modules/User/addUser';
import {dataURLtoBlob, handleFileSelect} from './modules/Avatar/index';
import {
	btnNeed,
	btnPartners,
	btnDeal,
	tabs,
	renderDealTable,
	renderPaymentTable,
} from "./modules/Partnerships/index";
import {chooseLocation} from "./modules/Location/index";

$('document').ready(function () {
	const USER_ID = $('body').data('user'),
		PARTNER_ID = $('.tab_main').find('li.active').attr('data-partner'),
		ID = getLastId();
	let managerSelect = $('#manager_select'),
		userManagerSelect = $('#user_manager_select'),
		userIsPartner = $('.left-contentwrap').attr('data-partner');

	if (userIsPartner === 'True') {
		renderDealTable({done: 'False'});
		renderPaymentTable();
	}

	function parseFunc(data, params) {
		params.page = params.page || 1;
		const results = [];
		data.results.forEach(function makeResults(element) {
			results.push({
				id: element.id,
				text: element.title,
			});
		});
		return {
			results: results,
			pagination: {
				more: (params.page * 100) < data.count
			}
		};
	}

	// $('#set_manager').on('click', function () {
	//     const userId = $(this).data('user');
	//     let manager = $('#manager_select').val(),
	//         config = {'manager_id': manager};
	//     postData(`${URLS.user.detail(userId)}set_manager/`, config)
	//         .then(() => window.location.reload())
	//         .catch(err => errorHandling(err));
	// });
	$('.reset_device_id').on('click', function () {
		const profileId = $(this).data('id');
		postData(`/api/app/users/${profileId}/reset_device_id/`, null)
			.then(() => window.location.reload())
			.catch(err => errorHandling(err));
	});

	// const ID = getLastId();

	function AddColorMarkers() {
		let options = $('#markers-select').find('option:selected'),
			markers = [];
		options.each(function () {
			const marker = {
				'color': $(this).attr('data-color'),
				'title': $(this).attr('data-search'),
				'hint': $(this).attr('data-hint'),
			};
			markers.push(marker);
		});
		markers.forEach(function (item) {
			$('.select-wrapper').find('.selection').find(`li[title='${item.title}']`)
				.addClass('hint--top-left  hint--large')
				.attr('aria-label', item.hint).css({
				'background-color': item.color,
				'padding': '5px 10px',
			});
		});
	}

	$('.hard-login').on('click', function () {
		let user = $(this).data('user-id');
		setCookie('hard_user_id', user, {path: '/'});
		window.location.reload();
	});
	$('#create_light_auth').on('click', function () {
		let url = $(this).data('url');
		postData(url, null)
			.then(() => window.location.reload())
			.catch(err => errorHandling(err));
	});
	function send_confirm() {
		let url = $(this).data('url');
		postData(url, null)
			.then(() => window.location.reload())
			.catch(err => errorHandling(err));
	}
	$('#send_light_auth_confirm').on('click', send_confirm);
	$('#reset_light_auth_password').on('click', send_confirm);

	$("#tabs1 li").on('click', function () {
		let id_tab = $(this).attr('data-tab');
		$('[data-tab-content]').hide();
		$('[data-tab-content="' + id_tab + '"]').show();
		$(this).closest('.tab-status').find('li').removeClass('active');
		$(this).addClass('active');
	});

	$('#send_need').on('click', function () {
		let need_text = $('#id_need_text').val();
		let url = URLS.partner.update_need($(this).data('partner'));
		let need = JSON.stringify({'need_text': need_text});
		ajaxRequest(url, need, function () {
			showAlert('Нужда сохранена.');
		}, 'PUT', true, {
			'Content-Type': 'application/json'
		}, {
			400: function (data) {
				data = data.responseJSON;
				showAlert(data.detail);
			}
		});
		$(this).siblings('.editText').removeClass('active');
		$(this).parent().siblings('textarea').attr('readonly', true);
	});

	$('.send_email_with_code').on('click', function () {
		let url = $(this).data('url');
		ajaxRequest(url, null, function () {
			showAlert('Код отправлен на почту');
		}, 'GET', true, {
			'Content-Type': 'application/json'
		}, {
			400: function (data) {
				data = data.responseJSON;
				showAlert(data.detail);
			}
		});
	});
	$('#sendNote').on('click', function () {
		let _self = this;
		let id = $(_self).data('id');
		let resData = new FormData();
		resData.append('description', $('#id_note_text').val());
		updateUser(id, resData).then(() => showAlert('Ваше примечание добавлено.'));
		$(this).siblings('.editText').removeClass('active');
		$(this).parent().siblings('textarea').attr('readonly', true);
	});

	$('#sendMarker').on('click', function () {
		let id = $(this).data('id'),
			data = {};
		data.marker = $('#markers-select').val();
		postData(URLS.user.detail(id), data, {method: 'PATCH'}).then(() => {
			showAlert('Маркер изменен');
			AddColorMarkers();
		}).catch((err) => {
			let txt = err.responseText;
			showAlert(txt);
		});
		$(this).siblings('.editText').removeClass('active');
		$(this).closest('.note_wrapper').find('select').attr('readonly', true).attr('disabled', true);
	});

	$("#close-payment").on('click', function () {
		$('#popup-create_payment').css('display', 'none');
	});

	$("#popup-create_payment .top-text span").on('click', function () {
		$('#new_payment_sum').val('');
		$('#popup-create_payment textarea').val('');
		$('#popup-create_payment').css('display', '');
	});

	$('#payment-form').on("submit", function (event) {
		event.preventDefault();
		let data = $('#payment-form').serializeArray();
		let userID;
		let new_data = {};
		data.forEach(function (field) {
			if (field.name == 'sent_date') {
				new_data[field.name] = field.value.trim().split('.').reverse().join('-');
			} else if (field.name != 'id') {
				new_data[field.name] = field.value
			} else {
				userID = field.value;
			}
		});
		if (userID) {
			createPayment({
				data: new_data
			}, userID).then(function (data) {

			});
		}
		// create_payment(id, sum, description, rate, currency);

		$('#new_payment_sum').val('');
		$('#popup-create_payment textarea').val('');
		$('#popup-create_payment').css('display', 'none');
	});

	$("#create_new_payment").on('click', function () {
		$('#popup-create_payment').css('display', 'block');
	});
	$("#change-password").on('click', function () {
		$('#popup-change_password').css('display', 'block');
	});
	$("#close-password").on('click', function (e) {
		e.preventDefault();
		$('#popup-change_password').css('display', 'none');
	});
	$('#change-password-form').on('submit', function (event) {
		event.preventDefault();
		let data = $('#change-password-form').serializeArray();
		let new_data = {};
		data.forEach(function (field) {
			new_data[field.name] = field.value
		});
		$('.password-error').html('');
		ajaxRequest(`${CONFIG.DOCUMENT_ROOT}rest-auth/password/change/`, JSON.stringify(new_data), function (JSONobj) {
			window.location.href = `/entry/?next=${window.location.pathname}`;
		}, 'POST', true, {
			'Content-Type': 'application/json'
		}, {
			400: function (data) {
				data = data.responseJSON;
				for (let field in data) {
					if (!data.hasOwnProperty(field)) continue;
					$(`#error-${field}`).html(data[field]);
				}
			},
			403: function (data) {
				data = data.responseJSON;
				for (let field in data) {
					if (!data.hasOwnProperty(field)) continue;
					$(`#error-${field}`).html(data[field]);
				}
			}
		});
	});
	$("#popup-change_password .top-text span").on('click', function (el) {
		$('#popup-change_password').css('display', 'none');
	});

	$("#popup-create_deal .top-text span").on('click', function (el) {
		$('#new_deal_sum').val('');
		$('#popup-create_deal textarea').val('');
		$('#popup-create_deal').css('display', '');
	});
	$("#create_new_deal").on('click', function () {
		$('#send_new_deal').prop('disabled', false);
		$('#popup-create_deal').css('display', 'block');
	});

	$('.pop-up__table').find('.close_pop').on('click', function () {
		$('.pop-up_duplicate__table').css('display', 'none');
	});

	$("#tabs1 li").click();

	$("#id_deal_date").datepicker({
		dateFormat: "yy-mm-dd",
		maxDate: new Date(),
		yearRange: '2010:+0',
		autoClose: true,
		onSelect: function (date) {
		}
	}).mousedown(function () {
		$('#ui-datepicker-div').toggle();
	});
	$('#partnershipCheck').on('click', function () {
		let $input = $(this).closest('form').find('input:not([checkbox])');
		if ($(this).is(':checked')) {
			$input.each(function () {
				$(this).attr('readonly', false)
			});
		} else {
			$input.each(function () {
				$(this).attr('readonly', true)
			});
		}
	});
	$(".send_note").on('click', function (e) {
		e.preventDefault();
		let form = $(this).closest('form');
		let text_field = form.find('.js-add_note');
		let box = $(this).closest(".note-box");
		let text = text_field.val();
		let anket_id = form.data('anket-id');
		sendNote(anket_id, text, box);
		text_field.val('');
	});

	$(".js-lesson").on('click', function (e) {
		let lesson_id = $(this).data("lesson-id");
		let anket_id = $(this).data('anket-id');
		let checked = $(this).is(':checked');
		changeLessonStatus(lesson_id, anket_id, checked);
	});

	$("#tabs2 li").on('click', function (e) {
		e.preventDefault();
		let id_tab = this.getAttribute('data-tab');
		$('[data-summit-id]').hide();
		$('[data-summit-id="' + id_tab + '"]').show();
		$('.summits-block').hide();
		$(this).closest('.tab-status').find('li').removeClass('active');
		$(this).addClass('active');
	});
	$("#tabs3 li").on('click', function (e) {
		e.preventDefault();
		let id_tab = this.getAttribute('data-tab');
		$('.history-tabs-block[data-main_tab]').hide();
		$('.history-tabs-block[data-main_tab="' + id_tab + '"]').show();
		$(this).closest('.tab-status').find('li').removeClass('active');
		$(this).addClass('active');
	});
	$("#tabs4 li").on('click', function (e) {
		e.preventDefault();
		let id_tab = this.getAttribute('data-main');
		$('[data-history_tab]').hide();
		$('[data-history_tab="' + id_tab + '"]').show();
		$(this).closest('.tab-status').find('li').removeClass('active');
		$(this).addClass('active');
	});

	if ($("#tabs2 li")) {
		$('#Sammits').css('display', 'block');
	} else {
		$('#Sammits').css('display', 'block');
	}

	$('#deleteUser').click(function () {
		let id = $(this).attr('data-id');
		$('#yes').attr('data-id', ID);
		$('.add-user-wrap').show();
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

	$('#deletePopup span').click(function () {
		$('#deletePopup').hide();
	});

	function create_payment(partnerId, sum, description, rate, currency) {
		let data = {
			"sum": sum,
			"description": description,
			"rate": rate,
			"currency": currency
		};

		let json = JSON.stringify(data);

		ajaxRequest(URLS.partner.create_payment(partnerId), json, function (JSONobj) {
			showAlert('Оплата прошла успешно.');
		}, 'POST', true, {
			'Content-Type': 'application/json'
		}, {
			403: function (data) {
				data = data.responseJSON;
				showAlert(data.detail)
			}
		});
	}

	let $img = $(".crArea img");
	let flagCroppImg = false;

	let $selectDepartment = $('#departments');

	// makeHomeGroupsList($('#editHomeGroupForm').data('id')).then((results) => {
	//     if (!results) {
	//         return null
	//     }
	//     console.log(results);
	//     let $homeGroupsList = $('#home_groups_list');
	//     let homeGroupsID = $homeGroupsList.val();
	//     console.log(homeGroupsID);
	//     let options = [];
	//     let option = document.createElement('option');
	//     $(option).val('').text('Выберите домашнюю группу').attr('selected', true);
	//     options.push(option);
	//     results.forEach(function (item) {
	//         let option = document.createElement('option');
	//         $(option).val(item.id).text(item.get_title);
	//         if (homeGroupsID == item.id) {
	//             console.log(homeGroupsID == item.id);
	//             $(option).attr('selected', true);
	//             console.log(option);
	//         }
	//         options.push(option);
	//     });
	//     console.log(options);
	//     $homeGroupsList.html(options);
	// });

	$selectDepartment.on('change', function () {
		let option = document.createElement('option');
		$(option).val('').text('Выберите церковь').attr('selected', true);
		$(option).attr('value', 'null');
		makeChurches();
		$('#home_groups_list').html(option);
	});
	makeChurches();
	$('.selectdb').select2();
	$("#isStable").on('change', function () {
		console.log('checkbox');
		let stable,
			data;

		if ($('#isStable').is(':checked')) {
			stable = true;
		} else {
			stable = false;
		}
		data = {
			"is_stable": stable
		};
		postData(URLS.user.detail(currentUser), data, {method: "PATCH"});
	});
	$('.delete-manager').on('click', function () {
		let form = $(this).closest('form').attr('name'),
			link = $(this).parent('li').children('a').attr('href'),
			itemCount = $(`form[name='` + form + `']`).find('li').length,
			deleteItemCount = $(`form[name='` + form + `']`).find('.delete-item').length + 2,
			managerId = parseInt(link.replace(/\D+/g, ""));
		if ((itemCount - deleteItemCount) === 0) {
			$(this).closest(`form[name='` + form + `']`).find('.no-manager').css('display', 'block')
		}
		if (form === 'editUserManager') {
			let config = {'skin_id': managerId};
			postData(`${URLS.user.detail(currentUser)}delete_skin/`, config)
				.then(() => {
					$(this).parent('li').addClass('delete-item');
				})
				.catch((err) => showAlert(`Невозможно удалить. ${err.detail}`, 'Ошибка'));
		} else if (form === 'editManager') {
			let config = {'manager_id': managerId};
			postData(`${URLS.user.detail(currentUser)}delete_manager/`, config)
				.then(() => {
					$(this).parent('li').addClass('delete-item');
				})
				.catch((err) => showAlert(`Невозможно удалить. ${err.detail}`, 'Ошибка'));
		}
	});
	$('.set_user').on('click', function (e) {
		e.preventDefault();
		let managerText = $('#manager_select').parent('div').find('.select2-selection__rendered').text(),
			userManagerText = $('#user_manager_select').parent('div').find('.select2-selection__rendered').text(),
			userManager = $('#user_manager_select').val(),
			manager = $('#manager_select').val(),
			form = $(this).closest('form').attr('name'),
			list = $(this).closest('form').find('ul'),
			no_manager = $(this).closest('form').find('.no-manager'),
			noManager = $(this).closest('form').find('.noManager'),
			item = document.createElement('li'),
			config;

		$(no_manager).css('display', 'none');
		$(noManager).css('display', 'none');
		if (form === 'editUserManager') {
			config = {'skin_id': userManager};
			$(item).text(userManagerText);
			postData(`${URLS.user.detail(currentUser)}add_skin/`, config)
				.then(() => {
					list[0].prepend(item);
					$('#user_manager_select').val('').trigger('change');
				})
				.catch(err => errorHandling(err));
		} else if (form === 'editManager') {
			config = {'manager_id': manager};
			$(item).text(managerText);
			postData(`${URLS.user.detail(currentUser)}add_manager/`, config)
				.then(() => {
					list[0].prepend(item);
					$('#manager_select').val('').trigger('change');
				})
				.catch(err => errorHandling(err));
		}
	});
	$('.edit').on('click', function (e) {
		e.preventDefault();
		let $edit = $('.edit');
		let exists = $edit.closest('form').find('ul').hasClass('exists');
		let noEdit = false;
		let action = $(this).closest('form').data('action');
		let inputWrap = $(this).closest('form').find('.input-wrap');
		let deleteManager = $(this).closest('form').find('.delete-manager');
		$edit.each(function () {
			if ($(this).hasClass('active')) {
				noEdit = true;
			}
		});
		let $block = $('#' + $(this).data('edit-block'));
		let $input = $block.find('input:not(.select2-search__field), select');
		let $hiddenBlock = $(this).parent().find('.hidden');
		$hiddenBlock.each(function () {
			$(this).removeClass('hidden');
		});
		if ($(this).data('edit-block') == 'editContact' && $(this).hasClass('active')) {
			$(this).closest('form').get(0).reset();
		}
		if ($(this).hasClass('active')) {
			$('.search_city_link').css('visibility', 'hidden');
			$input.each(function (i, el) {
				if (!$(this).attr('disabled')) {
					$(this).attr('disabled', true);
				}
				$(this).attr('readonly', true);
				if ($(el).is('select')) {
					if ($(this).is(':not([multiple])')) {
						if (!$(this).is('.no_select')) {
							$(this).select2('destroy');
						}
					}
				}
			});
			if (action === 'update-manager') {
				$(inputWrap).css('display', 'none');
				$(deleteManager).css('display', 'none');
			}
			$(this).removeClass('active');
		} else {
			if (noEdit) {
				showAlert("Сначала сохраните или отмените изменения в другом блоке")
			} else {
				$('.search_city_link').css('visibility', '');
				$input.each(function () {
					if (!$(this).hasClass('no__edit')) {
						if ($(this).attr('disabled')) {
							$(this).attr('disabled', false);
						}
						$(this).attr('readonly', false);
						if ($(this).is('select') && $(this).is(':not(.no_select)')) {
							$(this).select2();
						}
					}
				});
				if (action === 'update-manager') {
					makeSelect(managerSelect, URLS.user.list_user(), parseFunc);
					makeSelect(userManagerSelect, URLS.user.list_user(), parseFunc);
					$(inputWrap).css('display', 'flex');
					$(deleteManager).css('display', 'flex');

				}
				$(this).addClass('active');
			}
		}
	});
	$('.save__info').on('click', function (e) {
		e.preventDefault();
		if (($(this).closest('form').attr('name') == 'editHierarchy') && ($('#selectResponsible').val() == null)) {
			showAlert('Выберите ответственного');

			return;
		}

		if (($(this).closest('form').attr('name') == 'editContact') && (!$('#phone_number').inputmask("isComplete"))) {
			showAlert('Введите коректный номер телефона');

			return;
		}

		$(this).closest('form').find('.edit').removeClass('active');
		let _self = this;
		let $block = $(this).closest('.right-info__block');
		let $input = $block.find('input:not(.select2-search__field), select');
		let thisForm = $(this).closest('form');
		let success = $(this).closest('form').closest('.right-info__block').find('.success__block');
		let formName = thisForm.attr('name');
		let action = thisForm.data('action');
		let partner = thisForm.data('partner');
		let form = document.forms[formName];
		let inputWrap = $(this).closest('form').find('.input-wrap');
		let deleteManager = $(this).closest('form').find('.delete-manager');
		let formData = new FormData(form);
		let hidden = $(this).hasClass('after__hidden');
		let messengers = [];
		if (action === 'update-user') {
			if ($input.is(':checkbox') && !$input.is('#is_dead')) {  // it is partner form
				let partnershipData = new FormData();
				partnershipData.append('is_active', !!$input.is(':checked'));
				let $newInput = $input.filter(":not(':checkbox')");
				$newInput.each(function () {
					let id = $(this).data('id');
					if ($(this).hasClass('sel__date')) {
						partnershipData.append(id, $(this).val().trim().split('.').reverse().join('-'));
					} else if ($(this).hasClass('par__group')) {
						if ($(this).val() != null) {
							partnershipData.append(id, $(this).val());
						}
					} else {
						partnershipData.append(id, $(this).val());
					}
				});
				console.log($(success));
				updateOrCreatePartner(partner, partnershipData, success)
					.then(function (data) {
						let partnerId = data.id;
						// let partnerForm = $('form#partnership');
						thisForm.attr('data-partner', partnerId);
					})
					.then(function (data) {
						if (hidden) {
							let editBtn = $(_self).closest('.hidden').data('edit');
							setTimeout(function () {
								$('#' + editBtn).trigger('click');
							}, 1500)
						}
					});
			} else {
				if (formName === 'editMessengers') {
					$input.each(function () {
						if ($(this).val().trim()) {
							messengers.push({"code": $(this).attr('name'), "value": $(this).val().trim()});
						}
					});
				}
				if (formName === 'editLocation') {
					let id = $('#chooseCity').attr('data-id');
					id && formData.append('locality', id);
				}
				$input.each(function () {
					let id = $(this).data('id');
					if (!$(this).attr('name')) {
						if ($(this).is('[type=file]')) {
							let send_image = $(this).prop("files").length || false;
							if (send_image) {
								try {
									let blob;
									blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
									formData.append('image', blob, 'logo.jpg');
									formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
									formData.append('id', id);

								} catch (err) {
									console.log(err);
								}
							}
							return;
						}
						let id = $(this).attr('id');
						let $val = $('#' + id);
						if ($val.val() instanceof Array) {
							formData.append(id, JSON.stringify($('#' + id).val()));
						} else {
							if ($val.val()) {
								if ($val.hasClass('sel__date')) {
									if ($val.val() == "Не покаялся") {
										formData.append(id, "");
									} else {
										formData.append(id, $('#' + id).val().trim().split('.').reverse().join('-'));
									}
								} else if ($val.hasClass('is_dead')) {
									if ($val.is(':checked')) {
										formData.append(id, "true");
									} else {
										formData.append(id, "false");
									}
								} else if ($val.hasClass('sex')) {
									$val.val() && formData.append(id, $val.val());
								} else if ($val.hasClass('language')) {
									$val.val() && formData.append(id, $val.val());
								}
								else {
									formData.append(id, JSON.stringify($('#' + id).val().trim().split(',').map((item) => item.trim())));
								}
							} else {
								if ($val.hasClass('sel__date')) {
									formData.append(id, '');
								} else {
									formData.append(id, JSON.stringify([]));
								}
							}
						}
					}
				});
				if (messengers.length > 0) {
					formData.append('messengers', JSON.stringify(messengers));
				}
				updateUser(ID, formData, success).then(function (data) {
					if (formName === 'editHierarchy') {
						$('.is-hidden__after-edit').html('');
					}
					if (hidden) {
						let editBtn = $(_self).closest('.hidden').data('edit');
						setTimeout(function () {
							$('#' + editBtn).trigger('click');
						}, 1500)
					}
					$('#fullName').text(data.fullname);
					$('#searchName').text(data.search_name);
				});
			}
		} else if (action === 'update-church') {
			let $existBlock = $('#editChurches').find('ul');
			let userId = $('body').attr('data-user');
			let url = URLS.user.detail(currentUser);
			let noExist = $existBlock.hasClass('exists');
			let church_id = $('#church_list').val();
			let home_groups_id = $('#home_groups_list').val();
			if (!!home_groups_id) {
				addUserToHomeGroup(ID, home_groups_id, url, noExist).then(function (data) {
					let success = $(_self).closest('.right-info__block').find('.success__block');
					$(success).text('Сохранено');
					setTimeout(function () {
						$(success).text('');
						$('.no_church_in').text('');
					}, 3000);
					$existBlock.addClass('exists');
				}).catch(function (data) {
					showAlert(JSON.parse(data.responseText));
				});
			} else if (!!church_id) {
				addUserToChurch(ID, church_id, url, noExist).then(function (data) {
					let success = $(_self).closest('.right-info__block').find('.success__block');
					$(success).text('Сохранено');
					setTimeout(function () {
						$(success).text('');
						$('.no_church_in').text('');
					}, 3000);
					$existBlock.addClass('exists');
				}).catch(function (data) {
					showAlert(JSON.parse(data.responseText));
				});
			}
		} else if (action === 'update-manager') {
			if (action === 'update-manager') {
				$(inputWrap).css('display', 'none');
				$(deleteManager).css('display', 'none');
			}
		}
		$input.each(function () {
			if (!$(this).attr('disabled')) {
				$(this).attr('disabled', true);
			}
			$(this).attr('readonly', true);
			if ($(this).is('select')) {
				if ($(this).is(':not([multiple])')) {
					if (!$(this).is('.no_select')) {
						$(this).select2('destroy');
					}
				}
			}
		});
		$('.search_city_link').css('visibility', 'hidden');
	});
	$.validate({
		lang: 'ru',
		form: '#editContactForm',
		modules: 'toggleDisabled',
	});

	initLocationSelect({
		country: 'selectCountry',
		region: 'selectRegion',
		city: 'selectCity'
	});
	$('.datepicker-here').datepicker({
		autoClose: true
	});
	$('#departments').on('change', function () {
		let status = $('#selectHierarchy').find('option:selected').data('level');
		let department = $(this).val();
		makeResponsibleList(department, status, false, true);
	});
	// after fix
	let depart = $('#departments').val(),
		stat = $('#selectHierarchy').find('option:selected').attr('data-level');
	makeResponsibleList(depart, stat, false, true);

	$('#selectHierarchy').on('change', function () {
		let department = $('#departments').val();
		let status = $(this).find('option:selected').data('level');
		makeResponsibleList(department, status, true, true);
	});
	$('.sel__date').each(function () {
		let $el = $(this);
		let date = ($el.val() && $el.val() != 'Не покаялся') ? new Date($el.val().split('.').reverse().join(', ')) : new Date();
		$el.datepicker({
			autoClose: true,
			startDate: date,
			dateFormat: 'dd.mm.yyyy'
		})
	});
	$('#editNameBtn').on('click', function () {
		if ($(this).hasClass('active')) {
			$('#editNameBlock').css({
				display: 'block',
			});
		} else {
			$('#editNameBlock').css({
				display: 'none',
			});
		}
	});

	$('#file').on('change', handleFileSelect);

	$('#editCropImg').on('click', function () {
		let imgUrl;
		imgUrl = $img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
		$('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
		$('.anketa-photo').html('<img src="' + imgUrl + '" />');
		$('#impPopup').fadeOut(300, function () {
			$img.cropper("destroy");
		});

		if (flagCroppImg && !$('#editNameBtn').hasClass('active')) {
			let form = document.forms['editName'];
			let formData = new FormData(form);
			let blob;
			blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
			formData.append('image', blob, 'logo.jpg');
			formData.set('image_source', $('input[type=file]')[0].files[0], 'photo.jpg');
			// formData.append('id', id);
			updateUser(ID, formData);
		}
		return flagCroppImg = false;
	});

	$('#impPopup').find('.close').on('click', function () {
		$('#impPopup').fadeOut(300, function () {
			$img.cropper("destroy");
		});
	});

	$('#divisions').select2();
	$('#departments').select2();

	$('#sent_date').datepicker({
		autoClose: true,
		dateFormat: 'dd.mm.yyyy'
	});

	$('.summits-title').on('click', function () {
		$(this).next('.summits-block').siblings('.summits-block').slideUp(300);
		$(this).next('.summits-block').slideToggle();
	});

	$('.summits-block .rows-tabs').on('click', 'p', function () {
		let tab = $(this).parent().data('tabs-id');
		$(this).closest('.rows-tabs').find('div').removeClass('active');
		$(this).parent().addClass('active');
		$(this).closest('.summits-block').find('.wrapp').hide();
		$(this).closest('.summits-block').find(`.wrapp-${tab}`).show();
	});

	AddColorMarkers();

	$('#phone_number').inputmask('phone', {
		onKeyValidation: function () {
			$(this).next().text($(this).inputmask("getmetadata")["name_ru"]);
		}
	});

	$('#access_select').select2();

	$('#sendAccess').on('click', function () {
		let hasAccess = $(this).attr('data-access'),
			id = $(this).attr('data-id'),
			level = $('#access_select').val(),
			accessTitle = $('#access_select').find("option:selected").text(),
			config = {
				level: +level,
			};

		if (level != null) {
			if (hasAccess == 'True') {
				postData(URLS.user.update_partner_role(id), config, {method: 'PATCH'}).then(() => {
					showAlert(`Права изменены на: ${accessTitle}`);
				}).catch((err) => showAlert(err.detail));
			} else {
				postData(URLS.user.set_partner_role(id), config).then(() => {
					showAlert(`Права (${accessTitle}) успешно установлены`);
				}).catch((err) => showAlert(err.detail));
			}
		}
		$(this).siblings('.editText').removeClass('active');
		$('#access_select').attr('readonly', true).attr('disabled', true);
		$('#delete_access').attr('disabled', true);
	});

	$('#delete_access').on('click', function () {
		let id = $(this).attr('data-id');
		showConfirm('Удаление', 'Вы действительно хотите удалить права пользователя?', function () {
			deleteData(URLS.user.delete_partner_role(id)).then(() => {
				showAlert(`Права успешно удалены`);
				$('#access_select').val(null).trigger("change");
			}).catch((err) => showAlert(`Невозможно удалить. ${err.detail}`, 'Ошибка'));
		}, () => {
		});
		$(this).closest('.access_wrapper').find('.editText').removeClass('active');
		$('#access_select').attr('readonly', true).attr('disabled', true);
		$('#delete_access').attr('disabled', true);
	});


	// $('label[for="master"]').on('click', function () {
	//     let id = $('#selectResponsible').find('option:selected').val();
	//     if(id) {
	//         window.location.href = `/account/${id}`;
	//     }
	// })

	dataIptelTable(URLS.phone.lastThree(currentUser));

	$('#monthInput').datepicker({
		autoClose: true,
		view: 'months',
		onSelect: function (formattedDate, date, inst) {
			$('.preloader').css('display', 'block');
			let dateMonth = moment(date).format("YYYY-MM"),
				url = URLS.phone.filterMonth(currentUser, dateMonth);
			// $('#popupMonth').find('.main-text').html('');

			dataIptelMonth(url);
		}
	});

	$('#monthBtn').on('click', function (e) {
		e.preventDefault;
		let idUser = $('body').attr('data-user'),
			todayDate = moment().locale('ru'),
			url = URLS.phone.filterMonth(currentUser, todayDate.format("YYYY-MM"));
		// $('#popupMonth').find('.main-text').html('');
		$('.preloader').css('display', 'block');
		$('#popupMonth').css('display', 'block');
		$('#monthInput').val(todayDate.format("MMMM YYYY"));
		dataIptelMonth(url);
	});

	$('.close_pop').on('click', function () {
		$('#popupMonth').css('display', 'none');
	});

	btnNeed();
	btnPartners();
	btnDeal();
	tabs();
	chooseLocation();

});