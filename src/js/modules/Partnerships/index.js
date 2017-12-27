'use strict';
import URLS from '../Urls';
import {postData} from "../Ajax/index";
import {showAlert} from "../ShowNotifications/index";
import errorHandling from '../Error';

export function btnNeed() {
    $('.a-note, .a-sdelki').find('.editText').on('click', function () {
        $(this).toggleClass('active');
        let textArea = $(this).parent().siblings('textarea'),
            select = $(this).closest('.note_wrapper').find('select'),
            btn = $(this).closest('.access_wrapper').find('#delete_access');
        if ($(this).hasClass('active')) {
            textArea.attr('readonly', false);
            select.attr('readonly', false).attr('disabled', false);
            btn.attr('disabled', false);
        } else {
            textArea.attr('readonly', true);
            select.attr('readonly', true).attr('disabled', true);
            btn.attr('disabled', true);
        }
    });

    $('.a-note, .a-sdelki').find('.send_need').on('click', function () {
        let partnerID = $(this).attr('data-partner'),
            textArea = $(this).parent().siblings('textarea'),
            type = $(this).attr('data-type'),
            need_text = textArea.val(),
            url = (type === 'CH') ? URLS.partner.church_detail(partnerID) : URLS.partner.update_need(partnerID),
            data = {'need_text': need_text},
            config = {
                method: (type === 'CH') ? 'PATCH' : 'PUT',
            };
        postData(url, data, config).then(() => {
            showAlert('Нужда сохранена.');
        }).catch(err => {
            errorHandling(err);
        });
        $(this).siblings('.editText').removeClass('active');
        textArea.attr('readonly', true);
    });
}

export function btnPartners() {
    $('#addMorePartners').on('click', function () {
        $('#popup-create_partners').css('display', 'block');
    });

    $('#close_addPartners').on('click', function () {
        $('#popup-create_partners').css('display', 'none');
    });

    $('#send_addPartners').on('click', function () {
        let popup = $('#popup-create_partners'),
            checkBox = popup.find('.partnershipCheck'),
            partnershipData = {},
            type = $(this).attr('data-type'),
            url = (type === 'CH') ? URLS.partner.church_list() : URLS.partner.list();
        partnershipData.is_active = checkBox.is(':checked');
        let $input = popup.find('input:not(.select2-search__field), select').filter(":not(':checkbox')");
        $input.each(function () {
            let id = $(this).data('id');
            if ($(this).hasClass('sel__date')) {
                partnershipData[id] = $(this).val().trim().split('.').reverse().join('-');
            } else if ($(this).hasClass('par__group')) {
                if ($(this).val() != null) {
                    partnershipData[id] = $(this).val();
                }
            } else {
                partnershipData[id] = $(this).val();
            }
        });
        postData(url, partnershipData).then(() => {
            location.reload();
        }).catch(err => {
            errorHandling(err);
        })
    });
}

export function btnDeal() {
    $(".create_new_deal").on('click', function () {
        let partnerID = $(this).attr('data-partner'),
            currency = $(this).attr('data-currency'),
            popup = $('#popup-create_deal');
        $('#send_new_deal').prop('disabled', false);
        $('#send_new_deal').attr('data-partner', partnerID);
        popup.find('.currency').val(currency);
        popup.css('display', 'block');
    });

    $("#close-deal").on('click', function () {
        $('#popup-create_deal').css('display', 'none');
    });

    // $('#send_new_deal').on('click', function () {
    //     let description = $('#popup-create_deal textarea').val(),
    //         value = $('#new_deal_sum').val(),
    //         date = $('#new_deal_date').val(),
    //         type = $('#new_deal_type').val();
    //
    //     if (value && date) {
    //         let dateFormat = date.trim().split('.').reverse().join('-'),
    //             id = $(this).data('partner'),
    //             checkDeal = {
    //                 'date_created': dateFormat,
    //                 'value': value,
    //                 'partnership_id': id,
    //             },
    //             deal = {
    //                 'date_created': dateFormat,
    //                 'value': value,
    //                 'description': description,
    //                 'partnership': id,
    //                 'type': type,
    //             };
    //         $(this).prop('disabled', true);
    //         getData(URLS.deal.check_duplicates(), checkDeal).then(data => {
    //             if (data.results) {
    //                 $('.preloader').css('display', 'block');
    //                 $('#send_new_deal').prop('disabled', false);
    //                 makeDuplicateDeals(checkDeal);
    //                 $('#hard_create').attr('data-date_created', dateFormat)
    //                     .attr('data-value', value)
    //                     .attr('data-description', description)
    //                     .attr('data-partnership', id)
    //                     .attr('data-type', type);
    //             } else {
    //                 createDeal(deal);
    //             }
    //         }).catch(() => showAlert('При запросе к серверу произошла ошибка. Попробуйте снова', 'Ошибка'))
    //     } else {
    //         showAlert('Заполните все поля.');
    //     }
    // });
}