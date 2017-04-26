/**
 * Created by pluton on 25.04.17.
 */
(function ($) {
    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        let regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    $('.ticket_title').click(function () {
        let self = $(this);
        let ticket_id = $(this).data('id');
        let url = `/api/v1.0/summit_tickets/${ticket_id}/users/`;
        let code = getParameterByName('code');
        if (code) {
            url += `?code=${code}`
        }
        fetch(url, {'credentials': 'include'})
            .then(function (response) {
                return response.json();
            })
            .then(function (ankets) {
                $('.tickets_table tr').removeClass('active_ticket');
                self.closest("tr").addClass('active_ticket');
                let tmpl = $('#users_tml').html();
                let rendered = _.template(tmpl)({"ankets": ankets});

                $('#ticket_users').html(rendered);
            });
    });
    $('#find_by_code_btn').on('click', function () {
        let code = $('#find_by_code').val();
        window.location.href = `/summits/tickets/?code=${code}`;
    })

})(jQuery);
