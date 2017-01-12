$(document).ready(function(){

    $('.columns-wrap').on('scroll', function () {
        $("#partnerFrom").datepicker('hide');
        $("#partnerFrom").blur();
        $("#bornDate").datepicker('hide');
        $("#bornDate").blur();
        $("#firsVisit").datepicker('hide');
        $("#firsVisit").blur();
        $("#repentanceDate").datepicker('hide');
        $("#repentanceDate").blur();
    });

    $('#impPopup').click(function(el){
        if (el.target != this) {return}
        $(this).hide();
        $('input[type=file]').val('');
        img.cropper("destroy")
    });

    $('#impPopup .top-text span').click(function(){
        $('#impPopup').hide();
        $('input[type=file]').val('');
        img.cropper("destroy");

    });

    $('#edit-photo').click(function(){
        if($(this).attr('data-source')) {
            document.querySelector("#impPopup img").src = $(this).attr('data-source');
        } else {
            document.querySelector("#impPopup img").src = $('#edit-photo img').attr('src');
        }
        document.querySelector("#impPopup").style.display = 'block';
                img.cropper({
                    aspectRatio: 1 / 1,
                    built: function () {
                      img.cropper("setCropBoxData", { width: "100", height: "50" });
                    }
                });
    });


    $('#impPopup button').click(function(){
        let iurl;
      iurl = img.cropper("getDataURL", "image/jpeg");
      $('#edit-photo').attr('data-source',document.querySelector("#impPopup img").src);
      $('.anketa-photo').html('<img src="'+iurl+'" />');
      $('#impPopup').hide();
      img.cropper("destroy");
    });

    $.datepicker.setDefaults($.datepicker.regional["ru"]);

    $("#partnerFrom").datepicker().mousedown(function() {
        $('#ui-datepicker-div').toggle();
    });

    $("#bornDate").datepicker({yearRange: '1920:+0'}).mousedown(function() {
        $('#ui-datepicker-div').toggle();
    });

    $("#firsVisit").datepicker().datepicker("setDate", new Date()).mousedown(function() {
        $('#ui-datepicker-div').toggle();
    });

    $("#repentanceDate").datepicker().mousedown(function() {
        $('#ui-datepicker-div').toggle();
    });

    $('#partner').click(function () {
        $('.hidden-partner').toggle()
    });


    getAll();

    let dep,
        stat;

    $("#chooseCountry").select2({placeholder: " "}).on("change", getRegions);
    $("#chooseRegion").select2({placeholder: " "}).on("change", getCities);
    $("#chooseCity").select2({placeholder: " ",tags: true});
    $("#chooseDepartment").select2({placeholder: " "});
    $("#chooseStatus").select2({placeholder: " "});
    $("#chooseDivision").select2({placeholder: " "});
    $("#chooseStatus").select2({placeholder: " "});
    $("#chooseManager").select2({placeholder: " "});
    $("#chooseResponsible").select2({placeholder: " "});
    $("#chooseResponsibleStatus").select2({placeholder: " "});
    $("#chooseCountryCode").select2({placeholder: " "}).on("select2:select", function(el) {
      document.querySelector('[name="phone_numberCode"]').value = el.target.value;
    });


    $("#chooseDepartment").on("change", function(){
      window.dep = $(this).val();
      document.getElementById('chooseResponsible').removeAttribute('disabled');
      getResponsible(window.dep,window.stat);
    });

    $('input[name="first_name"]').keyup(function() {
      if ($(this).val() !== 0) {
        document.querySelector("input[name='first_name']").style.border = '';
      }
    });

    $('input[name="last_name"]').keyup(function() {
      if ($(this).val() !== 0) {
        document.querySelector("input[name='last_name']").style.border = '';
      }
    });

    $('input[name="phone_number"]').keyup(function() {
      if ($(this).val() !== 0) {
        document.querySelector("input[name='phone_number']").style.border = '';
      }
    });

    $('input[name="email"]').keyup(function() {
      if ($(this).val() !== 0) {
        document.querySelector("input[name='email']").style.border = '';
      }
    });

    $('#chooseStatus').on('change', function() {
      if ($(this).val() == 1) {
        document.getElementById('kabinet').setAttribute('disabled',true);
      } else {
        document.getElementById('kabinet').removeAttribute('disabled');
      }
    })

    $("#chooseResponsibleStatus").on("change", function(){
      window.stat = $(this).val();
      document.getElementById('chooseResponsible').removeAttribute('disabled');
      getResponsible(window.dep,window.stat);
    });

    $("#chooseDepartment").on("change", function(){
      document.querySelector("#chooseDepartment + span .select2-selection").style.border = '';
    });

    $("#chooseDepartment").on("change", function(){
      document.querySelector("#chooseStatus + span .select2-selection").style.border = '';
    });

    document.getElementById('saveNew').addEventListener('click', createNewAcc);
});

let img = $(".crArea img");



  document.querySelector('.pop-up-splash').addEventListener('click', function(el) {
    if(el.target !== this) {
      return;
    }
    this.style.display = 'none';
  });

  document.querySelector('.editprofile .top-text span').addEventListener('click', function() {
   document.querySelector('.pop-up-splash-add').style.display = 'none';
  });

  document.querySelector('button.close').addEventListener('click', function() {
    document.querySelector('.pop-up-splash-add').style.display = 'none';
  });

  document.querySelector('.pop-up-splash-add').addEventListener('click', function(el) {
    if(el.target !== this) {
      return;
    }
    this.style.display = 'none';
  });

  document.getElementById('addFileButton').addEventListener('click', function() {
    document.getElementById('addFile').click();
  });

  document.querySelector("#popupForNew h3 span").addEventListener('click', function() {
        document.querySelector('#popupForNew').style.display = 'none';
        document.querySelector('.pop-up-splash-add').style.display = 'block';
  });

    document.querySelector("#closeNew").addEventListener('click', function() {
        document.querySelector('#popupForNew').style.display = 'none';
        document.querySelector('.pop-up-splash-add').style.display = 'block';
    });

    document.getElementById('changeSumNew').addEventListener('click', function() {
        document.getElementById('summit-valueNew').removeAttribute('readonly');
        document.getElementById('summit-valueNew').focus();
    });

    document.getElementById('completeNew').addEventListener('click', function() {
        let id = this.getAttribute('data-id'),
            money = document.getElementById('summit-valueNew').value,
            description = document.querySelector('#popupForNew textarea').value;
        registerUserNew(id,summit_id,money,description);
        window.location.reload();
    });

  document.getElementsByName('f')[0].addEventListener('change', selectFile, false);


function getAll() {
    window.dep = $("#chooseDepartment").val();
    window.stat = $("#chooseResponsibleStatus").val();
    document.querySelector('[name="phone_numberCode"]').value = $('#chooseCountryCode').val();
}

function getDataForPopupNew(id, name, master) {
    document.getElementById('completeNew').setAttribute('data-id', id);
    document.getElementById('client-nameNew').innerHTML = name;
    document.getElementById('responsible-nameNew').innerHTML = master;
}

function registerUserNew(id,summit_id,money, description) {
    let data = {
                "user_id": id,
                "summit_id": summit_id,
                "value": money,
                "description": description
      };
        if (document.getElementById('check').checked) {
          data['retards'] = true;
          data['code'] = document.getElementById('code').value;
        }
        console.log(data);
    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/summit_ankets/post_anket/', json, function (JSONobj) {
            if(JSONobj.status){
                let data = {};
                data['summit'] = summit_id;
                getUsersList(data);
                getUnregisteredUsers();
            }
        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
}

function getRegions() {
    let opt = {};
    opt['country'] = $("#chooseCountry").val();;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/regions/', opt, function (data) {
      if(data.length == 0) {
        document.getElementById('chooseRegion').innerHTML = '<option value=""> </option>';
        document.getElementById('chooseCity').removeAttribute('disabled')
      }
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseRegion').innerHTML = html;
        document.getElementById('chooseRegion').removeAttribute('disabled');
    });
  }

function getResponsible(id, level) {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/short_users/?department=' + id + '&hierarchy=' + level, null, function (data) {
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].fullname+'</option>';
      }
        document.getElementById('chooseResponsible').innerHTML = html;
    });
  }

function getCities() {
    let opt = {};
    opt['region'] = $("#chooseRegion").val();;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/cities/', opt, function (data) {
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseCity').innerHTML = html;
      document.getElementById('chooseCity').removeAttribute('disabled')
    });
  }

function selectFile(evt) {

    let files = evt.target.files;
    for (let i = 0, f; f = files[i]; i++) {
          if (!f.type.match('image.*')) {
            continue;
          }
        let reader = new FileReader();
          reader.onload = (function(theFile) {
              return function (e) {
              document.querySelector("#impPopup img").src=e.target.result;
              document.querySelector("#impPopup").style.display = 'block';
                img.cropper({
                    aspectRatio: 1 / 1,
                    built: function () {
                      img.cropper("setCropBoxData", { width: "100", height: "50" });
                    }
                });
            };
          })(f);
          reader.readAsDataURL(f);
        }
   }

function createNewAcc() {
  if (!document.querySelector("input[name='phone_number']").value) {
    document.querySelector("input[name='phone_number']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='phone_number']").style.border = '';
  }
    let data = {
    "email": document.querySelector("input[name='email']").value,
    "first_name": document.querySelector("input[name='first_name']").value,
    "last_name": document.querySelector("input[name='last_name']").value,
    "middle_name": document.querySelector("input[name='middle_name']").value,
    "born_date": document.querySelector("input[name='born_date']").value,
    "phone_number": document.querySelector("input[name='phone_numberCode']").value + '' + document.querySelector("input[name='phone_number']").value,
    "vkontakte": document.querySelector("input[name='vk']").value,
    "facebook": document.querySelector("input[name='fb']").value,
    "odnoklassniki": document.querySelector("input[name='ok']").value,
    "address": document.querySelector("input[name='address']").value,
    "skype": document.querySelector("input[name='skype']").value,
    "district": document.querySelector("input[name='district']").value,
    "region": $('#chooseRegion option:selected').html() == 'Не выбрано'?'':$('#chooseRegion option:selected').html(),
    'responsible':$("#chooseManager").val(),
    'value': document.querySelector("input[name='value']").value,
    'date': document.querySelector("input[name='partnership_date']").value,
    'divisions': $('#chooseDivision').val() || '',
    'hierarchy': $("#chooseStatus").val(),
    'department': $("#chooseDepartment").val(),
    'repentance_date': document.querySelector("input[name='repentance_date']").value,
    'coming_date': document.querySelector("input[name='first_visit']").value,
    'city': $('#chooseCity option:selected').html() == 'Не выбрано'?'':$('#chooseCity option:selected').html(),
    'country': $('#chooseCountry option:selected').html() == 'Не выбрано'?'':$('#chooseCountry option:selected').html()
  }
  if (document.getElementById('kabinet').checked) {
    data['send_password'] = true;
    if (!data['email']) {
      document.querySelector("input[name='email']").style.border = '1px solid #d46a6a';
      return;
    }
  } else {
    data['send_password'] = false;
  }

  if ($("#chooseResponsible").val()) {
    data["master"] = $("#chooseResponsible").val();
  }

  if (!data['first_name']) {
    document.querySelector("input[name='first_name']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='first_name']").style.border = '';
  }

  if (!data['last_name']) {
    document.querySelector("input[name='last_name']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='last_name']").style.border = '';
  }

  if ($("#chooseCountry").val() == '206' || $("#chooseCountry").val() == '162') {
    if (!data['middle_name']) {
      document.querySelector("input[name='middle_name']").style.border = '1px solid #d46a6a';
      return;
    } else {
      document.querySelector("input[name='middle_name']").style.border = '';
    }
  } else {
      document.querySelector("input[name='middle_name']").style.border = '';
    }

  if (!data['email']) {
    document.querySelector("input[name='email']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='email']").style.border = '';
  }

  if (!data['hierarchy'] || !data['department']) {
    document.querySelector("#chooseDepartment + span .select2-selection").style.border = '1px solid #d46a6a';
    document.querySelector("#chooseStatus + span .select2-selection").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("#chooseDepartment + span .select2-selection").style.border = '';
    document.querySelector("#chooseStatus + span .select2-selection").style.border = '';
  }

    let num_reg = /^[0-9]*$/ig;
  if (!num_reg.test(document.querySelector("input[name='phone_number']").value)) {
    document.querySelector("input[name='phone_number']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='phone_number']").style.border = '';
  }
    let val_reg = /^[0-9]*$/ig;
  if (!val_reg.test(document.querySelector("input[name='value']").value)) {
    document.querySelector("input[name='value']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='value']").style.border = '';
  }
/*
 let url =config.DOCUMENT_ROOT + 'api/v1.0/short_users/?search=' + data["first_name"] +'+' + data["last_name"];
      ajaxRequest( url, null, function(data,answer) {
      //  console.log(data);
        if (data.length) {
 let id  = data[0].id;
          // debugger
          // showPopup(data.message)
           //showPopup('Такой пользователей есть уже в БД');
           return;
           setTimeout(function() {
            window.location.href = '/account/' + id ;
            }, 1500);
        }

      })
*/
    let name = data['first_name'] + " " + data['last_name'],
    master = $('#chooseResponsible option:selected').html();
    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/create_user/', json, function (data) {
          if (data.redirect) {
              let fd = new FormData();
            if(!$('input[type=file]')[0].files[0]){
              console.log(data.id)
                  fd.append('id' , data.id)
                } else {
                let blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                let sr = $('#edit-photo').attr('data-source');
                  fd.append( 'file', blob );
                  fd.set('source', $('input[type=file]')[0].files[0], 'photo.jpg');
                  fd.append('id' , data.id)
                }
            function dataURLtoBlob(dataurl) {
                let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
                        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
                    while(n--){
                        u8arr[n] = bstr.charCodeAt(n);
                    }
                    return new Blob([u8arr], {type:mime});
                }
            /*fd.append( 'file', $('input[type=file]')[0].files[0] );
            fd.append('id' , data.id)*/
              let xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
              xhr.open('POST', config.DOCUMENT_ROOT + 'api/v1.0/create_user/', true);

            xhr.onreadystatechange = function(){
              if (xhr.readyState == 4) {

                if(xhr.status == 200) {
                         //    debugger
                //showPopup(data.message)
                    getDataForPopupNew(data.id, name, master);
                    document.querySelector('.pop-up-splash-add').style.display = 'none';
                    document.querySelector('.pop-up-splash').style.display = 'none';
                    document.getElementById('popupForNew').style.display = 'block';
                    //registerUser(data.id+'',summit_id+'','0', '')

                }
              }
            };


            xhr.send(fd);
          }
      }, 'POST', true, {
          'Content-Type': 'application/json'
      });
}