function authUser() {
    var username = document.getElementById('login').value;
    var password = document.getElementById('psw').value;
    var remember_me = document.getElementById('save-profile').checked;
    //var remember = false
        //	if (remember_me.className == 'checkbox active'){
        //		remember = true
        //	}
    
    var data = {
        "username": username,
        "email": username,
        "password": password
        //'remember_me': remember
    }
    if (remember_me) {
        data['remember_me'] = false;
    } else {
        data['remember_me'] = true;
    }
    console.log(data)
    if (checkEmptyFields(username, password) == false) {

        var json = JSON.stringify(data);
        ajaxRequest(config.DOCUMENT_ROOT+'api/login/', json, function(JSONobj) {
            //showPopup(JSONobj.message);
            if (JSONobj.status == true) {
                //showPopup(JSONobj.message);
              window.location.href = '/events';
            } else {
                //loginError(JSONobj.message);
                //alert(JSONobj.message)
                clearFields()
                document.querySelector(".account .invalid").style.display = 'block'
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });

    }else{
        document.querySelector(".account .invalid").style.display = 'block';
        clearFields()
    }
}

function clearFields(){
   // document.getElementById('login').value = '';
    document.getElementById('psw').value = '';
}
/*
function loginError(text) {
    document.getElementById('error_alert').innerHTML = '* ' + text;
    document.getElementById('error_alert').style.display = 'block';
    document.getElementById('login').style.border = '1px solid #DC3030'
    document.getElementById('psw').style.border = '1px solid #DC3030'
}

function clearStyle() {
    document.getElementById('error_alert').style.display = 'none'
    document.getElementById('login_alert').style.display = 'none'
    document.getElementById('pass_alert').style.display = 'none'
    document.getElementById('login').style.border = '1px solid #fff'
    document.getElementById('psw').style.border = '1px solid #fff'
}

function addErrorStyle(errorId, fieldId) {
    document.getElementById(errorId).style.display = 'block'
    document.getElementById(fieldId).style.border = '1px solid #DC3030'
}
*/
function checkEmptyFields(username, password) {
    var empty = false
    if (username.length == 0) {
      //  addErrorStyle('login_alert', 'login');
        empty = true;
    }

    if (password.length == 0) {
      //  addErrorStyle('pass_alert', 'psw');
        empty = true;
    }
    return empty;
}

function logIn() {
   // clearStyle()
    authUser();
}


function sendPassToEmail(){

        var data = {
            'email' : document.getElementById('send_letter').value
        }

            var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT+'/api/password_forgot', json, function(JSONobj) {
            showPopup(JSONobj.message);
            if (JSONobj.status == true) {
                //showPopup(JSONobj.message);
                setTimeout(function() {
                   // window.location.href = '/events';
                }, 1500);
            } 
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
}

$(document).ready(function(){
    document.getElementById('entry').addEventListener('click',function(){
        logIn();
    })


    document.getElementById('prev_page').addEventListener('click',function(){
        document.getElementsByClassName('getpassword')[0].style.display = 'none';
        document.getElementById('login_popup').style.display = 'block'
    })



    document.getElementsByClassName('restore')[0].addEventListener('click',function(){
        document.getElementsByClassName('getpassword')[0].style.display = 'block';
        document.getElementById('login_popup').style.display = 'none'
    });


    document.getElementById('getpass').addEventListener('click',function(){
        sendPassToEmail();
    })

    $('.entry-input2').keypress(function(e) {
        if (e.which == 13) {
            logIn();
        }
    });

    $('.entry-input1').keypress(function(e) {
        if (e.which == 13) {
            logIn();
        }
    });
})