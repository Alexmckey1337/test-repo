(function ($) {
    $(document).ready(function () {
        "use strict";
        let userId = $('body').attr('data-user'),
            sortCard = document.getElementById('drop'),
            arrSortClass = localStorage.arrHideWell ? JSON.parse(localStorage.arrHideWell) : [];
        let sortable = new Sortable(sortCard, {
            sort: true,
            animation: 150,
            ghostClass: 'sortable-ghost',
            draggable: '.well',
            chosenClass: "sortable-chosen",
	        dragClass: "sortable-drag",
			group: "localStorage-example",
			store: {
				get: function (sortable) {
					let order = localStorage.getItem(sortable.options.group.name);
					return order ? order.split('|') : [];
				},
				set: function (sortable) {
					let order = sortable.toArray();
					localStorage.setItem(sortable.options.group.name, order.join('|'));
				}
			}
        });
        sortable.option("disabled", true);
        let $arrWell = $('.dashboard').find('.well');

        for (let i=0; i<arrSortClass.length; i++) {
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
               // order = sortable.toArray();
           sortable.option("disabled", !state);
           // localStorage.setItem(sortable.options.group.name, order.join('|'));

           let $arrWell = $('.dashboard').find('.well'),
               arrHideWell = [];
           $arrWell.each(function (index) {
               if ($(this).hasClass('hide')) {
                   arrHideWell.push(index);
               }
           });
           localStorage.arrHideWell = JSON.stringify(arrHideWell);

           $('.dashboard').find('.well.hide').hide();
        });
        $('.dashboard').find('.vision').on('click', function (e) {
            e.stopPropagation();
            $(this).toggleClass('active');
            $(this).closest('.well').toggleClass('hide');
        })
    });
})(jQuery);
