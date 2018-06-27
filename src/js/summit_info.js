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


	$('.create_pdf').on('click', function () {
		let authorID = $(this).data('author-id');
		ajaxRequest(URLS.generate_tickets_by_author(SUMMIT_ID, authorID), null, function (data) {
			console.log(data);
		}, 'GET', true, {
			'Content-Type': 'application/json'
		});
	});

});