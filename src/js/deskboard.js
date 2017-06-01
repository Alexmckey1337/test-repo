(function ($) {
    "use strict";
    $(document).ready(function () {
        $('.deskboard').sortable({
            items: '.drop',
            axis: 'y',
            evert: true,
            scroll: false,
            placeholder: 'emptySpaceRow'
        });
        $('.drop').sortable({
            items: '.well',
            axis: 'x',
            revert: true,
            scroll: false,
            placeholder: 'emptySpace'
        });
    });
})(jQuery);
