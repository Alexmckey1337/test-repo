function changePass() {
   
var hash =   document.location.href.split('/')[document.location.href.split('/').length - 2] ;

if(!hash){
     showPopup('неверный ключ активации');
}

    var data = {
        "password1": document.getElementsByTagName('input')[0].value,
        "password2": document.getElementsByTagName('input')[1].value,
        "activation_key": hash
    }


        var json = JSON.stringify(data);
        ajaxRequest(config.DOCUMENT_ROOT+'api/password_view/', json, function(JSONobj) {
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
})
