'use strict';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';
import 'cropper';
import 'cropper/dist/cropper.css';
import 'jquery-file-download/index.js';
import 'jquery-form-validator/form-validator/jquery.form-validator.min.js';
import 'jquery-form-validator/form-validator/lang/ru.js';
import {showAlert} from "./modules/ShowNotifications/index";
import {handleFileSelect} from "./modules/Avatar/index";
import {makeDuplicateCount, makeDuplicateUsers} from "./modules/User/findDuplicate";

$('document').ready(function () {
    let flagCroppImg = false,
        img = $(".crArea img");

    $('#file').on('change', handleFileSelect);
    $('#file_upload').on('click', function (e) {
        e.preventDefault();
        $('#file').click();
    });

    $('#impPopup').click(function (el) {
        if (el.target != this) {
            return
        }
        $('#impPopup').fadeOut(300, function () {
            img.cropper("destroy");
        });
        $('input[type=file]').val('');
    });

    $('#impPopup .close').on('click', function () {
        $('#impPopup').fadeOut(300, function () {
            img.cropper("destroy");
        });
        $('#file').val('');
    });

    $('#editCropImg').on('click', function () {
        let imgUrl;
        imgUrl = img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
        $('.anketa-photo').html('<img src="' + imgUrl + '" />');
        $('#impPopup').fadeOut(300, function () {
            img.cropper("destroy");
        });
        return flagCroppImg = false;

    });

    $("#bornDate").datepicker({
        minDate: new Date(new Date().setFullYear(new Date().getFullYear() - 120)),
        maxDate: new Date(),
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
    });

    $("#firsVisit").datepicker().datepicker({
        dateFormat: 'yyyy-mm-dd',
        maxDate: new Date(),
        setDate: new Date(),
        autoClose: true,
    });

    $("#repentanceDate").datepicker({
        dateFormat: 'yyyy-mm-dd',
        maxDate: new Date(),
        setDate: new Date(),
        position: 'top left',
        autoClose: true,
    });
    $('#partnerFrom').datepicker({
        dateFormat: 'yyyy-mm-dd',
        maxDate: new Date(),
        setDate: new Date(),
        autoClose: true,
    });
    $('#partner').on('change', function () {
        $('.hidden-partner').toggle();
    });

    $('.editprofile .top-text span').on('click', function () {
        $('.pop-up-splash').css('display', 'none');
    });

    $('button.close').on('click', function () {
        $('.pop-up-splash').css('display', 'none');
    });

    $('.btn-block').find('.closeForm').on('click', function (e) {
        e.preventDefault();
        $('#addNewUserPopup').css('display', 'none');
        $(this).closest('form').get(0).reset();
        $(this).closest('form').find('input[type=file]').val('');
        $(this).closest('form').find('#edit-photo img').attr('src', '/static/img/no-usr.jpg');
    });

    $('.btn-block').find('.nextForm').on('click', function (e) {
        e.preventDefault();
        let flag = false;
        $('.must').each(function () {
           $(this).validate(function (valid) {
               return flag = valid;
           });
           return flag;
        });
        if (!flag) {
               showAlert(`Обязательные поля не заполнены либо введены некорректные данные`);
           } else {
               $(this).closest('form').addClass('active');
               let user = `${$('#last_name').val()} ${$('#first_name').val()} ${$('#middle_name').val()}`;
               $('.second_step').find('.user').html(user);
        }
    });

    $('.btn-block').find('.prevForm').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').removeClass('active');
    });

    $("#createUser").find('input').each(function () {

        $(this).keypress(function(event) {
	        let keycode = (event.keyCode ? event.keyCode : event.which);
	        if (keycode == '13') {
	            event.preventDefault();
            }
	        event.stopPropagation();
        });
    });

    $('.popap').on('click', function () {
        $(this).css('display', 'none');
    });

    $('.editprofile-screen').on('click', function (e) {
       e.stopPropagation();
    });

    let inputs = $('#first_name, #last_name, #middle_name, #phoneNumber');
    inputs.on('focusout', function () {
        $('#createUser').find('._preloader').css('opacity', '1');
        makeDuplicateCount();
    });

     $('#duplicate_link').on('click', function () {
         $('.preloader').css('display', 'block');
         makeDuplicateUsers();
     });

    $('.pop-up__table').find('.close_pop').on('click', function () {
        $('.pop-up__table').hide();
    });

    $('#last_name, #first_name, #middle_name, #phoneNumber').keypress(function (event) {
        let keycode = (event.keyCode ? event.keyCode : event.which);
	        if (keycode == '13') {
	            event.preventDefault();
	            $('#createUser').find('._preloader').css('opacity', '1');
	            makeDuplicateCount();
            }
	        event.stopPropagation();
    });

        $("#createUser").find('input').each(function () {

        $(this).keypress(function(event) {
	        let keycode = (event.keyCode ? event.keyCode : event.which);
	        if (keycode == '13') {
	            event.preventDefault();
            }
	        event.stopPropagation();
        });
    });
});