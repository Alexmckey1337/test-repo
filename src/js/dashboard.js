(function ($) {
    $(document).ready(function () {
        "use strict";
        let userId = $('body').attr('data-user');

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

        function initSortable() {
            let sortCard = document.getElementById('drop'),
                arrSortClass = localStorage.arrHideWell ? JSON.parse(localStorage.arrHideWell) : [];
            let sortable = new Sortable(sortCard, {
                sort: true,
                animation: 150,
                ghostClass: 'sortable-ghost',
                draggable: '.well',
                chosenClass: "sortable-chosen",
                dragClass: "sortable-drag",
                group: "localStorage-example",
                // store: {
                //     get: function (sortable) {
                //         let order = localStorage.getItem(sortable.options.group.name);
                //         return order ? order.split('|') : [];
                //     },
                //     set: function (sortable) {
                //         // let order = sortable.toArray();
                //         // localStorage.setItem(sortable.options.group.name, order.join('|'));
                //     }
                // },
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
            let $arrWell = $('.dashboard').find('.well');

            for (let i = 0; i < arrSortClass.length; i++) {
                let index = arrSortClass[i];
                $($arrWell[index]).addClass('hide').hide().find('.vision').addClass('active');
            }
            $('.dashboard').find('.edit-desk').on('click', function () {
                $(this).toggleClass('active');
                $('.dashboard').find('.drop').toggleClass('active');
                let state = sortable.option("disabled");
                sortable.option("disabled", !state);
                if ($(this).hasClass('active')) {
                    $('.dashboard').find('.well.hide').show();
                } else {
                    $('.dashboard').find('.well.hide').hide();
                }
            });

            $('.dashboard').find('.save').on('click', function () {
                $('.dashboard').find('.edit-desk').removeClass('active');
                $('.dashboard').find('.drop').removeClass('active');
                let state = sortable.option("disabled");
                // let order = sortable.toArray();
                sortable.option("disabled", !state);
                // localStorage.setItem(sortable.options.group.name, order.join('|'));

                //Save to localstore
                let rang = [];
                let $card = $('.dashboard').find('.well');
                $card.each(function (indx, elem) {
                    rang.push(1 + $card.index(elem) + " ");
                });
                localStorage.setItem('rang', JSON.stringify(rang));
                console.log(rang);
                let order = sortable.toArray();
                console.log(order);

                // let $arrWell = $('.dashboard').find('.well'),
                //     arrHideWell = [];
                // $arrWell.each(function (index) {
                //     if ($(this).hasClass('hide')) {
                //         arrHideWell.push(index);
                //     }
                // });
                // localStorage.arrHideWell = JSON.stringify(arrHideWell);

                $('.dashboard').find('.well.hide').hide();
            });
        }

        Promise.all([getHomeGroupStats(), getChurchData(), getUsersData()]).then(values => {
            let data = {};
            for (let i = 0; i < values.length; i++) {
                Object.assign(data, values[i]);
            }
            let tmpl = document.getElementById('mainStatisticsTmp').innerHTML;
            let rendered = _.template(tmpl)(data);
            $('#dashboard').append(rendered);
            initSortable();
        });

        $('#master-filter').select2();

    });
})(jQuery);
