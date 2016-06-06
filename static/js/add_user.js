$(document).ready(function(){

    $('.columns-wrap').on('scroll', function () {
      $("#partnerFrom").datepicker('hide')
      $("#partnerFrom").blur()
      $("#bornDate").datepicker('hide')
      $("#bornDate").blur()
      $("#firsVisit").datepicker('hide')
      $("#firsVisit").blur()
      $("#repentanceDate").datepicker('hide')
      $("#repentanceDate").blur()
    });

    $('[name="phone_number"]').click(function(){
        if ($(this).val().length === 0) {
            $(this).val('+')
        }
    })

    $('#impPopup').click(function(el){
        if (el.target != this) {return}
        $(this).hide();
        $('input[type=file]').val('');
        img.cropper("destroy")
    })

    $('#impPopup .top-text span').click(function(){
        $('#impPopup').hide();
        $('input[type=file]').val('');
        img.cropper("destroy");

    })

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
    })


    $('#impPopup button').click(function(){
      var iurl;
      iurl = img.cropper("getDataURL", "image/jpeg");
      $('#edit-photo').attr('data-source',document.querySelector("#impPopup img").src)
      $('.anketa-photo').html('<img src="'+iurl+'" />');
      $('#impPopup').hide();
      img.cropper("destroy");
    })

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

    $('#partner').click(function(){$('.hidden-partner').toggle()})
    

    getAll();

    var dep,
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

var img = $(".crArea img");

  document.querySelector('.pop-up-splash').addEventListener('click', function(el) {
    if(el.target !== this) {
      return;
    }
    this.style.display = 'none';
  });

  document.querySelector('.editprofile .top-text span').addEventListener('click', function() {
   document.querySelector('.pop-up-splash').style.display = 'none';
  });

  document.querySelector('button.close').addEventListener('click', function() {
    document.querySelector('.pop-up-splash').style.display = 'none';
  });

  document.getElementById('addFileButton').addEventListener('click', function() {
    document.getElementById('addFile').click();
  })

  document.getElementsByName('f')[0].addEventListener('change', selectFile, false);  


function getAll() {  
  getCountries();
  getDepartments();
  getStatuses();
  getDivisions();
  getManagers();
  getResponsibleStatuses();
}
  

function getCountries() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/countries/', null, function(data) {
      var html = '<option value=""> </option><option>Не выбрано</option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseCountry').innerHTML = html;
    });
}

function getDepartments() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/departments/', null, function(data) {
      var data = data.results;
      var html = '<option value=""> </option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseDepartment').innerHTML = html;      
      dep = $("#chooseDepartment").val();
    });

}

function getStatuses() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/hierarchy/', null, function(data) {
      var data = data.results;
      var html = '<option value=""> </option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseStatus').innerHTML = html;      
    });
}

function getResponsibleStatuses() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/hierarchy/', null, function(data) {
      var data = data.results;
      var html = '<option value=""> </option><option>Не выбрано</option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseResponsibleStatus').innerHTML = html;
      stat = $("#chooseResponsibleStatus").val();
    });
}

function getDivisions() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/divisions/', null, function(data) {
      var data = data.results;
      var html = '<option value=""> </option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseDivision').innerHTML = html;      
    });
}

function getUsers() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/hierarchy/', null, function(data) {
      var data = data.results;
      var html = '<option value=""> </option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseStatus').innerHTML = html;
    });
}

function getManagers() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/partnerships/?is_responsible=2', null, function(data) {
      var data = data.results;
      var html = '<option value=""> </option><option>Не выбрано</option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].fullname+'</option>';
      }
      document.getElementById('chooseManager').innerHTML = html;
    });
}

function getRegions() {
    var opt = {};
    opt['country'] = $("#chooseCountry").val();;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/regions/', opt, function(data) {
      if(data.length == 0) {
        document.getElementById('chooseRegion').innerHTML = '<option value=""> </option>';
        document.getElementById('chooseCity').removeAttribute('disabled')
      }
      var html = '<option value=""> </option><option>Не выбрано</option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseRegion').innerHTML = html;
      document.getElementById('chooseRegion').removeAttribute('disabled');      
    });
  }

function getResponsible(id,level) {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/short_users/?department=' + id + '&hierarchy=' + level, null, function(data) {
      var html = '<option value=""> </option><option>Не выбрано</option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].fullname+'</option>';
      }
      document.getElementById('chooseResponsible').innerHTML = html;      
    });
  }

function getCities() {
    var opt = {};
    opt['region'] = $("#chooseRegion").val();;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/cities/', opt, function(data) {
      var html = '<option value=""> </option><option>Не выбрано</option>';
      for (var i = 0; i < data.length; i++) {
        html += '<option value="'+data[i].id+'">'+data[i].title+'</option>';
      }
      document.getElementById('chooseCity').innerHTML = html;
      document.getElementById('chooseCity').removeAttribute('disabled')
    });
  }

function selectFile(evt) {
  
        var files = evt.target.files;
        for (var i = 0, f; f = files[i]; i++) {
          if (!f.type.match('image.*')) {
            continue;
          }
          var reader = new FileReader();
          reader.onload = (function(theFile) {
            return function(e) {  
              document.querySelector("#impPopup img").src= e.target.result
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
  var data = {
    "email": document.querySelector("input[name='email']").value,
    "first_name": document.querySelector("input[name='first_name']").value,
    "last_name": document.querySelector("input[name='last_name']").value,
    "middle_name": document.querySelector("input[name='middle_name']").value,
    "born_date": document.querySelector("input[name='born_date']").value,
    "phone_number": document.querySelector("input[name='phone_number']").value,
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

  if (!data['first_name'] || !data['last_name'] || !data['phone_number']) {
    document.querySelector("input[name='first_name']").style.border = '1px solid #d46a6a';
    document.querySelector("input[name='last_name']").style.border = '1px solid #d46a6a';
    document.querySelector("input[name='phone_number']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='first_name']").style.border = '';
    document.querySelector("input[name='last_name']").style.border = '';
    document.querySelector("input[name='phone_number']").style.border = '';
  }

  if (!data['hierarchy'] || !data['department']) {
    document.querySelector("#chooseDepartment + span .select2-selection").style.border = '1px solid #d46a6a';
    document.querySelector("#chooseStatus + span .select2-selection").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("#chooseDepartment + span .select2-selection").style.border = '';
    document.querySelector("#chooseStatus + span .select2-selection").style.border = '';
  }

  var num_reg = /^\+[0-9]*$/ig;
  if (!num_reg.test(document.querySelector("input[name='phone_number']").value)) {
    document.querySelector("input[name='phone_number']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='phone_number']").style.border = '';
  }
  var val_reg = /^[0-9]*$/ig;
  if (!val_reg.test(document.querySelector("input[name='value']").value)) {
    document.querySelector("input[name='value']").style.border = '1px solid #d46a6a';
    return;
  } else {
    document.querySelector("input[name='value']").style.border = '';
  }
/*
  var url =config.DOCUMENT_ROOT + 'api/short_users/?search=' + data["first_name"] +'+' + data["last_name"];
      ajaxRequest( url, null, function(data,answer) {
      //  console.log(data);
        if (data.length) {
           var id  = data[0].id;
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
  var json = JSON.stringify(data);
  ajaxRequest(config.DOCUMENT_ROOT + 'api/create_user/', json, function(data) {
          if (data.redirect) {
            var fd = new FormData();
            if(!$('input[type=file]')[0].files[0]){
                  fd.append('id' , data.id)
                } else {
                  fd.set('source', $('input[type=file]')[0].files[0], 'photo.jpg');
                  var blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                  var sr = $('#edit-photo').attr('data-source');
                  fd.append( 'file', blob );
                  //fd.append('source', sr)
                  fd.append('id' , data.id)
                }
            function dataURLtoBlob(dataurl) {
                    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
                        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
                    while(n--){
                        u8arr[n] = bstr.charCodeAt(n);
                    }
                    return new Blob([u8arr], {type:mime});
                }
            var xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open('POST',config.DOCUMENT_ROOT + 'api/create_user/', true);

            xhr.onreadystatechange = function(){
              if (xhr.readyState == 4) {

                if(xhr.status == 200) {
                showPopup(data.message)
                  setTimeout(function() {
                    //window.location.href = '/account/' + data.id;
                  }, 1000);
                }
              }
            };


            xhr.send(fd);
          }
      }, 'POST', true, {
          'Content-Type': 'application/json'
      });
}