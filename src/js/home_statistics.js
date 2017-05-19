(function ($) {
    $('#filter_button').on('click', function () {
        $('#filterPopup').css('display', 'block');
    });

    getData('/api/v1.0/events/home_meetings/statistics/').then(data => {
        console.log(data);

        let tmpl = document.getElementById('statisticsTmp').innerHTML;
        let rendered = _.template(tmpl)(data);
        document.getElementById('statisticsContainer').innerHTML = rendered;
    })
})(jQuery);
