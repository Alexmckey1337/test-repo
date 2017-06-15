(function ($) {
    $(document).ready(function () {
        "use strict";
        let userId = $('body').attr('data-user'),
            sortable;
        $('.preloader').css('display', 'block');

        function getHomeGroupStats() {
            let resData = {
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/events/home_meetings/dashboard_counts/`
            };
            return new Promise(function (resolve, reject) {
                let codes = {
                    200: function (data) {
                        resolve(data);
                    },
                    400: function (data) {
                        reject(data);
                    }
                };
                newAjaxRequest(resData, codes, reject);
            });
        }

        function getChurchData() {
            let resData = {
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.0/churches/dashboard_counts/`
            };
            return new Promise(function (resolve, reject) {
                let codes = {
                    200: function (data) {
                        resolve(data);
                    },
                    400: function (data) {
                        reject(data);
                    }
                };
                newAjaxRequest(resData, codes, reject);
            });
        }

        function getUsersData() {
            let resData = {
                url: `${CONFIG.DOCUMENT_ROOT}api/v1.1/users/dashboard_counts/`
            };
            return new Promise(function (resolve, reject) {
                let codes = {
                    200: function (data) {
                        resolve(data);
                    },
                    400: function (data) {
                        reject(data);
                    }
                };
                newAjaxRequest(resData, codes, reject);
            });
        }

        function initSort() {
            let order = localStorage.order ? JSON.parse(localStorage.order) : [];
            if (order.length > 0) {
                for (let i = 0; i < order.length; i++) {
                    let index = +order[i],
                        card = $('.dashboard').find(`.well[data-id='${index}']`)
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

        Promise.all([getHomeGroupStats(), getChurchData(), getUsersData()]).then(values => {
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

            $('.preloader').css('display', 'none');
        }).catch(function (err) {
            console.log(err);
        });

        $('#master-filter').select2();

        $('.dashboard').find('.edit-desk').on('click', function () {
            $(this).toggleClass('active');
            $('.dashboard').find('.drop').toggleClass('active');
            let state = sortable.option("disabled");
            sortable.option("disabled", !state);
            if ($(this).hasClass('active')) {
                $('.dashboard').find('.well.hide').show();
            } else {
                $('.dashboard').find('.well.hide').removeClass('hide').find('.vision').removeClass('active');
                initSort();
                hideCard();
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
        });

    });
})(jQuery);
