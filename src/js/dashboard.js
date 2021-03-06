"use strict";
import Sortable from 'sortablejs/Sortable.min.js';
import URLS from './modules/Urls/index';
import makeSelect from './modules/MakeAjaxSelect/index';
import getData from './modules/Ajax/index';

$(document).ready(function () {
    let userId = $('body').attr('data-user'),
        userName = $('#master-filter').attr('data-userName'),
        sortable;
    $('.preloader').css('display', 'block');

    function init(id) {
        let config = {
                user_id: id
            },
            urlHG = URLS.event.home_meeting.dashboard_count(),
            urlCH = URLS.event.church_report.dashboard_count(),
            urlChurch = URLS.church.dashboard_count(),
            urlUser = URLS.user.dashboard_count();
        Promise.all([getData(urlHG, config), getData(urlChurch, config), getData(urlUser, config), getData(urlCH, config)]).then(values => {
            let data = {};
            for (let i = 0; i < values.length; i++) {
                Object.assign(data, values[i]);
            }
            let tmpl = document.getElementById('mainStatisticsTmp').innerHTML,
                rendered = _.template(tmpl)(data);
            $('#dashboard').append(rendered);

            initSort();
            initSortable();
            hideCard();
            addEventListenerToWell();

            $('.preloader').css('display', 'none');
        }).catch(function (err) {
            console.log(err);
        });
    }

    function addEventListenerToWell() {
        $('#drop').on('click', 'a', function (e) {
            e.preventDefault();
            let defaultUrl = $(this).attr('href'),
                tree = $('#master-filter').val();
            if (defaultUrl.indexOf('?') != -1) {
                window.location.href = `${defaultUrl}&master_tree=${tree}`;
            } else {
                window.location.href = `${defaultUrl}?master_tree=${tree}`;
            }
        });
    }

    function initSort() {
        let order = localStorage.order ? JSON.parse(localStorage.order) : [];
        if (order.length > 0) {
            for (let i = 0; i < order.length; i++) {
                let index = +order[i],
                    card = $('.dashboard').find(`.well[data-id='${index}']`);
                $('#drop').append(card);
            }
        }
    }

    function hideCard() {
        let arrSortClass = localStorage.arrHideCard ? JSON.parse(localStorage.arrHideCard) : [];
        if (arrSortClass.length > 0) {
            for (let i = 0; i < arrSortClass.length; i++) {
                let index = arrSortClass[i];
                $('.dashboard').find(`.well[data-id='${index}']`).addClass('hide').hide().find('.vision').addClass('active');
            }
        }
    }

    function initSortable() {
        let sortCard = document.getElementById('drop');
        sortable = new Sortable(sortCard, {
            sort: true,
            animation: 150,
            ghostClass: 'sortable-ghost',
            draggable: '.well',
            chosenClass: "sortable-chosen",
            dragClass: "sortable-drag",
            group: "localStorage-example",
            filter: ".vision",
            onFilter: function (evt) {
                let item = evt.item,
                    ctrl = evt.target;
                if (Sortable.utils.is(ctrl, ".vision")) {
                    $(item).find('.vision').toggleClass('active');
                    $(item).closest('.well').toggleClass('hide');
                }
            }
        });

        sortable.option("disabled", true);
    }

    function stopGoLink(event) {
        event.preventDefault();
    }

    init(userId);

    $('#master-filter').select2();

    $('.dashboard').find('.edit-desk').on('click', function () {
        $(this).toggleClass('active');
        $('.dashboard').find('.drop').toggleClass('active');
        let state = sortable.option("disabled");
        sortable.option("disabled", !state);
        if ($(this).hasClass('active')) {
            $('.dashboard').find('.well.hide').show();
            $('.dashboard').find('a.well').bind('click', stopGoLink);
        } else {
            $('.dashboard').find('.well.hide').removeClass('hide').find('.vision').removeClass('active');
            initSort();
            hideCard();
            $('.dashboard').find('a.well').unbind('click', stopGoLink);
        }
    });

    $('.dashboard').find('.save').on('click', function () {
        let state = sortable.option("disabled"),
            order = sortable.toArray(),
            $arrCard = $('.dashboard').find('.well'),
            arrHideCard = [];
        $('.dashboard').find('.edit-desk').removeClass('active');
        $('.dashboard').find('.drop').removeClass('active');
        sortable.option("disabled", !state);
        localStorage.order = JSON.stringify(order);
        $arrCard.each(function () {
            if ($(this).hasClass('hide')) {
                let indx = $(this).attr('data-id');
                arrHideCard.push(indx);
            }
        });
        localStorage.arrHideCard = JSON.stringify(arrHideCard);

        $('.dashboard').find('.well.hide').hide();
        $('.dashboard').find('a.well').unbind('click', stopGoLink);
    });

    $('#master-filter').on('change', function () {
        $('.preloader').css('display', 'block');
        let userId = $(this).val();
        $('#drop').remove();
        init(userId);

        //Fixed bugs for select2
        $('#container').unbind('scroll');
    });
    let config = {
        master_tree: userId,
        level_gte: 1
    };

    function parse(data, params) {
        params.page = params.page || 1;
        const results = [];
        data.results.forEach(function makeResults(element, index) {
            results.push({
                id: element.id,
                text: element.fullname,
            });
        });
        return {
            results: results,
            pagination: {
                more: (params.page * 50) < data.count
            }
        };
    }
    function formatRepo(data) {
        if (data.id === '') {
            return '-------';
        }
        return `<option value="${data.id}">${data.text}</option>`;
    }
    makeSelect($('#master-filter'), URLS.user.short_for_dashboard(), parse,formatRepo);
    const option = `<option value="${userId}">${userName}</option>`;
    $('#master-filter').append(option);

});