(function ($) {
    getChurches().then(function (data) {
        console.log(data);
        let tmpl = $('#databaseUsers').html();
        let rendered = _.template(tmpl)(data);
        $('#tableChurches').html(rendered);
        $('.preloader').css('display', 'none');
    })
})(jQuery);