function changePass(data) {
    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT+'api/change_password/', json, function(JSONobj) {
        showPopup(JSONobj.message);
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
}


function clickButton(val) {
    var form = val.parentElement
    var old_pass = form.getElementsByTagName('INPUT')[0].value
    var new_pass = form.getElementsByTagName('INPUT')[1].value
    var confirm_pass = form.getElementsByTagName('INPUT')[2].value
    form.getElementsByTagName('INPUT')[1].style.border = '1px solid #E2E2E2'
    form.getElementsByTagName('INPUT')[2].style.border = '1px solid #E2E2E2'
    var data = {}
    if (new_pass == confirm_pass) {
        data = {
            "old_password": old_pass,
            "password1": new_pass,
            "password2": confirm_pass,
        }
        changePass(data);
    } else {
        form.getElementsByTagName('INPUT')[1].style.border = '1px solid #DC3030'
        form.getElementsByTagName('INPUT')[2].style.border = '1px solid #DC3030'
    }
}

function editUser() {

    var xhr = new XMLHttpRequest();
    var first_name = document.getElementById('name').value;
    var last_name = document.getElementById('surname').value;
    var middle_name = document.getElementById('pantronic').value;
    var email = document.getElementsByClassName('mail-input')[0].value;
    var phone_number = document.getElementById('tel-input').value;
    if (!first_name && !last_name && !middle_name && !email && !phone_number) {
        showPopup('Заполните все поля');
        return;
    }
    var data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "phone_number": phone_number
    }
    var id_current_user = document.getElementsByClassName('admin_name')[0].getAttribute('data-id');
    var json = JSON.stringify(data);
    xhr.open("PATCH", config.DOCUMENT_ROOT+'api/users/' + id_current_user + '/', true)
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.withCredentials = true;
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                [].forEach.call(document.querySelectorAll(".personal-data input"), function(el) {
                    //el.value = '';
                });
                //showPopup('');
            }
        }
    }
    xhr.send(json);
}

function logout() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open('GET', config.DOCUMENT_ROOT+'api/logout', true);
    xmlhttp.withCredentials = true;
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4) {
            if (xmlhttp.status == 200) {
                console.log(JSON.parse(xmlhttp.responseText));
            }
        }
    };
    xmlhttp.send(null);
}