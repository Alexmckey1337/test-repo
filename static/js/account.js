$(document).ready(function(){
   init();
   getUserDeals()
   getUserSummitInfo();

   $('#deleteUser').click(function(){
        var id = $(this).attr('data-id');
        $('#yes').attr('data-id',id);
        $('.add-user-wrap').show();
   })

   $('#deletePopup').click(function(el){
    if (el.target != this) {
        return;
    }
        $(this).hide();
   })

   $('#no').click(function(){
     $('#deletePopup').hide();
   })

   $('#deletePopup .top-text span').click(function(){
     $('#deletePopup').hide();
   })

   $('#yes').click(function(){
     var id = $(this).attr('data-id');
     deleteUser(id)
     $('#deletePopup').hide();
   })



})


function init(id) {
    var id = parseInt(id || document.location.href.split('/')[document.location.href.split('/').length - 2]);


     
    if(!id){
        return 
    }
    ajaxRequest(config.DOCUMENT_ROOT + 'api/users/' + id, null, function(data) {

        if(data.image){
          document.querySelector(".anketa-photo img").src= data.image
        }
        if( !data.fields ){
            return
        }
        if(data.fields.coming_date.value) {
          document.getElementById('coming_date').innerHTML = data.fields.coming_date.value;
        }
        $('#deleteUser').attr('data-id',data.id)
        var fullname 
        var social = data.fields.social
        var repentance_date = data.fields.repentance_date;


        var status = repentance_date.value ? '<span class="green1">Покаялся: '+ repentance_date.value  +'</span>' : '<span class="reds">Не покаялся</span>'

        document.getElementById('repentance_status').innerHTML = status;


        for (var prop in data.fields) {
            if (!data.fields.hasOwnProperty(prop)) continue

            if(  prop == 'social' ){
               

                for(var soc in social){


                if( soc == 'skype'){
                document.getElementById('skype').innerHTML  =  social[soc]
                continue
               } 


                        if(document.querySelector("[data-soc = '"  +  soc   + "']")){
                            if(  social[soc]  ){
                                document.querySelector("[data-soc = '"  +  soc   + "']").setAttribute('data-href' , social[soc] )
                            }
                            
                        }
                }


                continue
            }    

            if( prop == 'fullname'){

                fullname = data.fields[prop]['value'].split(' ');

                if(document.getElementById(prop)){
                            document.getElementById(prop).innerHTML = fullname[0] + '<br>' +  fullname[1] + ' ' + fullname[2]
                }


                continue
            }
            if(  prop == 'divisions'  ){
              var   divisions = data.fields[prop]['value'].split(',').join(', ');
              document.getElementById(prop).innerHTML = divisions
                continue
            }

            if(document.getElementById(prop)){
                document.getElementById(prop).innerHTML = data.fields[prop]['value'] || ' '
            }





        } 

         Array.prototype.forEach.call(document.querySelectorAll(".a-socials"), function(el) {
            el.addEventListener('click', function() {
                var href= this.getAttribute('data-href');
                if(href){
                    window.location = href
                }

            });
        });


        document.getElementsByClassName('b-red')[0].addEventListener('click',function(){
            window.location.href = '/account_edit/' + id + '/'
        }) 

    })
}



function getUserDeals(){
    var id = parseInt(id || document.location.href.split('/')[document.location.href.split('/').length - 2]);
    if(!id){
        return 
    }
     var url = config.DOCUMENT_ROOT + '/api/partnerships/?user=' + id 

      ajaxRequest(url, null, function(data) {
        //console.log(data)



     var data = data.results[0]

     if(!data){
        document.getElementsByClassName('tab-status')[0].innerHTML = 'На данном пользователе нету сделок';
         document.getElementsByClassName('a-sdelki')[0].style.display = 'none'
         document.getElementById('parntership_info').style.display = 'none'
        return ;
     }
    var fields = data.fields;
    var deal_fields = data.deal_fields;
    var id = data.id;
    var html = ''
    var responsible = data.responsible


    document.getElementById('incomplete-count').innerHTML = parseInt(data.undone_deals_count) || 0
    document.getElementById('overdue-count').innerHTML = parseInt(data.expired_deals_count) || 0
    document.getElementById('completed-count').innerHTML = parseInt(data.done_deals_count) || 0
    
    document.getElementById('responsible').innerHTML = responsible
    document.getElementById('partner_val').innerHTML = data.value;
    document.getElementById('coming_date_').innerHTML = data.date;
    
    document.getElementById('parntership_info').style.display = 'block'








    if (!deal_fields || deal_fields.length == 0) {
       // document.getElementById('partner_table').innerHTML = '' //'Нету deal_fields';
       document.getElementsByClassName('tab-status')[0].innerHTML = 'На данном пользователе нету сделок'
       document.getElementsByClassName('a-sdelki')[0].style.display = 'none'
       document.getElementById('parntership_info').style.display = 'none'
        return ''
    }

    document.getElementsByClassName('a-sdelki')[0].style.display = 'block'



     Array.prototype.forEach.call(document.querySelectorAll("#tabs1 li"), function(el) {
            el.addEventListener('click', function() {
                var id_tab = this.getAttribute('data-tab') ;
                 $('[data-tab-content]').hide();
                $('[data-tab-content="'+id_tab+'"]').show();

            });
        });

     

     var done_deals = ''
     var expired_deals= ''
     var undone_deals = ''
    for (var i = 0; i < deal_fields.length; i++) {
        //console.log(  deal_fields[i].status )
       
             switch(deal_fields[i].status.value){
                case   'done': 
                //console.log('done');
                done_deals += '<div class="rows"><div class="col">'+
                                        '<p><span>'+ deal_fields[i].fullname.value + '</span></p>'+
                                    '</div><div class="col">'+
                                        '<p>Последняя сделка:<span>' +  deal_fields[i].date.value +'</span></p>'+
                                        '<p>Сумма<span>'  +  deal_fields[i].value.value  + '₴</span></p></div></div>'
                break
                case  'expired' :
                expired_deals += '<div class="rows"><div class="col">'+
                                        '<p><span>'+ deal_fields[i].fullname.value + '</span></p>'+
                                    '</div><div class="col">'+
                                        '<p>Последняя сделка:<span>' +  deal_fields[i].date.value +'</span></p>'+
                                        '<p>Сумма<span>'  +  deal_fields[i].value.value  + '₴</span></p></div></div>'
                break;
                case 'undone': 
                undone_deals += '<div class="rows"><div class="col">'+
                                        '<p><span>'+ deal_fields[i].fullname.value + '</span></p>'+
                                    '</div><div class="col">'+
                                        '<p>Последняя сделка:<span>' +  deal_fields[i].date.value +'</span></p>'+
                                        '<p>Сумма<span>'  +  deal_fields[i].value.value  + '₴</span></p></div></div>'
                break;
                default : 
                break;
             }
        
        
    }

        document.querySelector('[data-tab-content="3"]').innerHTML = done_deals
         document.querySelector('[data-tab-content="2"]').innerHTML = expired_deals
          document.querySelector('[data-tab-content="1"]').innerHTML = undone_deals

       document.querySelector("#tabs1 li").click()

    
      })
}

function deleteUser(id) {
    var data = {
                "id": id
                }
    var json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT+'api/delete_user/', json, function(JSONobj) {
            if(JSONobj.status){
                showPopup('Пользователь успешно удален');
                window.location.href="/"
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
}


function getUserSummitInfo(){

 
 var id = parseInt(id || document.location.href.split('/')[document.location.href.split('/').length - 2]);
    if(!id){
        return 
    }
     var url = config.DOCUMENT_ROOT + '/api/summit_ankets/?user=' + id 

      ajaxRequest(url, null, function(data) {
         var results = data.results;
         if(!results.length){
            document.getElementsByClassName('a-sammits')[0].style.display = 'none'
            return
         }

         var tab_title = [];
         var menu_summit = ''
         var body_summit = ''


         for(var i =0 ; i<results.length ; i++){
            if(results[i].info){
            var info = results[i].info.money_info;
            if(  $.inArray( info.summit_type_id, tab_title ) == -1  ){
               menu_summit += '<li data-tab='+ info.summit_type_id  +'><a href="#" >' + info.summit_title + '</a></li>'
                tab_title.push(info.summit_type_id)
            }  
            body_summit += '<div class="rows" data-summit-id = "'+  info.summit_type_id +'" ><div class="col"><p>'+ info.summit_title  + '  '+info.start_date +'</p> </div><div class="col">';
            if (info.description != "") {
                body_summit += '<p>' + info.description+ '</p>';
            } else {
                body_summit += '<p>Комментарий не указан</p>';
            }
            
            body_summit += '<p>Сумма<span> '+ info.value + ' ₴</span></p>' +
                                    '</div></div>'


            }

         }


         document.getElementsByClassName('summit_wrapper')[0].innerHTML = body_summit
         document.getElementById('tabs2').innerHTML = menu_summit


          Array.prototype.forEach.call(document.querySelectorAll("#tabs2 li"), function(el) {
            el.addEventListener('click', function(e) {
                e.preventDefault();
                var id_tab = this.getAttribute('data-tab') ;
                 $('[data-summit-id]').hide();
                $('[data-summit-id="'+id_tab+'"]').show();

            });
        });

        if(  document.querySelector("#tabs2 li") ){
            document.getElementsByClassName('a-sammits')[0].style.display = 'block'
            document.querySelector("#tabs2 li").click()
        }else{
             document.getElementsByClassName('a-sammits')[0].style.display = 'none'
            return
        }

          


      })
       



}
