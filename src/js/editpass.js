function changePass() {

    let hash = getLastId();

if(!hash){
     showPopup('неверный ключ активации');
}

    let data = {
        "password1": document.getElementsByTagName('input')[0].value,
        "password2": document.getElementsByTagName('input')[1].value,
        "activation_key": hash
    };


    let json = JSON.stringify(data);
    ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/password_view/', json, function (JSONobj) {
          // debugger

            if (JSONobj.status == true) {
                showPopup(JSONobj.message);
                setTimeout(function() {
                    window.location.href = '/events';
                }, 1500);
            } else{
                 showPopup(JSONobj.message);
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });

    

}


$("document").ready(function(){
    document.getElementById('create').addEventListener('click',function(){
        changePass()
    })
});
