(function ($) {
    $(document).ready(function () {
        "use strict";
        let userId = $('body').attr('data-user');
        let sortCard = document.getElementById('drop');
        function initSortable() {

        }
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
    });
})(jQuery);
