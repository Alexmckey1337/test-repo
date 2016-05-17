function init(id) {
    var id = id || document.location.href.split('/')[document.location.href.split('/').length - 2];
    ajaxRequest(config.DOCUMENT_ROOT+'api/users/' + id, null, function(data) {
        var profile = '';
        var user_hierarchy = '';
        var user_status = '';
        for (var prop in data.fields) {
            if (!data.fields.hasOwnProperty(prop)) continue

            if (data.fields[prop]['type'] == 's') {
                profile += '<li><p>' + prop + '*</p><span>' + data.fields[prop]['value'] + '</span></li>';
            }

            if (data.fields[prop]['type'] == 'h') {
                user_hierarchy += '<li><p>' + prop + '*</p><span>' + data.fields[prop]['value'] + '</span></li>';

            }
            if (data.fields[prop]['type'] == 'b') {
                var is_checked = data.fields[prop]['value'] ? 'checked' : '';
                user_status += '<div class="field"><input type="checkbox" name="check1" id="check1" ' + is_checked + '><label>' + prop + '<span></span></label> </div>';
            }
            if (data.fields[prop]['type'] == 't') {
                profile += '<li><p>' + prop + '*</p><textarea rows = "3" disabled>' + data.fields[prop]['value'] + '</textarea>';
            }
        }
        document.getElementById('user-info').innerHTML = profile;
        document.getElementById('status').innerHTML = user_hierarchy;
        document.getElementsByClassName('user-status')[0].innerHTML = user_status;
    })
}

$(function() {

    init();
    $("#datepicker").datepicker({
        dateFormat: "yy-mm-dd"
    });

    //Отправить пароль
    document.getElementsByClassName('send_pass')[0].addEventListener('click', function() {
        var data = {
            "id": document.location.href.split('/')[document.location.href.split('/').length - 2]
        }
        var json = JSON.stringify(data);
        ajaxRequest(config.DOCUMENT_ROOT+'api/send_password/', json, function(data) {
            showPopup(data.message)
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
    });

    //Редактировать профиль
    document.getElementsByClassName('edit_user_id')[0].addEventListener('click', function(e) {
        e.preventDefault();
        var id = document.location.href.split('/')[document.location.href.split('/').length - 2];
        document.location.href = '/account_edit/' + id;
    })
})