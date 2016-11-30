$(document).ready(function () {
    init();
    document.getElementsByName('f')[0].addEventListener('change', handleFileSelect, false);


    document.getElementById('file_upload').addEventListener('click', function () {
        document.getElementsByName('f')[0].click()
    }, false);

    $('#impPopup').click(function (el) {
        if (el.target != this) {
            return
        }
        $(this).fadeOut();
        $('input[type=file]').val('');
        img.cropper("destroy")
    })

    $('#impPopup .top-text span').click(function () {
        $('#impPopup').fadeOut();
        $('input[type=file]').val('');
        img.cropper("destroy");

    })

    $('#phone_number').click(function () {
        if ($(this).val().length === 0) {
            $(this).val('+')
        }
    })


    $('#edit-photo').click(function () {
        if ($(this).attr('data-source') !== 'null') {
            document.querySelector("#impPopup img").src = $(this).attr('data-source');
        } else {
            document.querySelector("#impPopup img").src = $('#edit-photo img').attr('src');
        }
        document.querySelector("#impPopup").style.display = 'block';
        img.cropper({
            aspectRatio: 1 / 1,
            built: function () {
                img.cropper("setCropBoxData", {width: "100", height: "50"});
            }
        });
    })


    //$('#impPopup span.go').click(function(){

    //})
    $('#impPopup button').click(function () {
        let iurl;
        iurl = img.cropper("getDataURL", "image/jpeg");
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src)
        $('.anketa-photo').html('<img src="' + iurl + '" />');
        $('#impPopup').fadeOut();
        img.cropper("destroy");
    })


    $("#partner_date").datepicker({
        dateFormat: "yy-mm-dd",
        // maxDate: new Date(),
        onSelect: function (date) {

        }
    }).datepicker("setDate", new Date()).mousedown(function () {
        $('#ui-datepicker-div').toggle();
    });


    document.getElementById('create_partner_info').addEventListener('click', function () {
        let el = document.getElementById('partner_wrap');
        let create_el = document.getElementById('create_partner');

        //this.checked ?  el.style.display = 'block' : el.style.display = 'none'
        if (this.checked) {
            el.style.display = 'block';
            create_el.style.display = 'none';
            $('#partner').attr('checked', true);
        } else {
            el.style.display = 'none';
            create_el.style.display = 'block';
            $('#partner').attr('checked', false);
        }


    });


    document.getElementById('revert_edit').addEventListener('click', function () {

        let id = parseInt(id || getLastId());
        if (!id) {
            return
        }
        window.location.href = '/account/' + id
    });


    document.getElementById('save').addEventListener('click', function () {
        sendData();
    });
    // document.getElementById('change_password').addEventListener('click', function () {
    //     sendPassword();
    // });
    // document.getElementById('revert_edit_password').addEventListener('click', function () {
    //     document.getElementById('old_password').value = "";
    //     document.getElementById('password1').value = "";
    //     document.getElementById('password2').value = "";
    // })


});


let data_for_drop = {};
let img = $(".crArea img");

function init(id) {
    let id = parseInt(id || getLastId());
    if (!id) {
        return
    }


    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/users/' + id + '/', null, function (data) {
        if (data.image) {
            document.querySelector(".anketa-photo img").src = data.image;
            convertImgToDataURLviaCanvas($(".anketa-photo img").attr('src'), function (data64) {
                $(".anketa-photo img").attr('src', data64);
            })
        } else {
            document.querySelector(".anketa-photo img").src = '/static/img/no-usr.jpg';
            convertImgToDataURLviaCanvas($(".anketa-photo img").attr('src'), function (data64) {
                $(".anketa-photo img").attr('src', data64);
            })
        }
        if (document.getElementById('edit-photo')) {
            document.getElementById('edit-photo').setAttribute('data-source', data.image_source);
        }
        if (!data.fields) {
            return
        }
        let fullname
        let social = data.fields.social
        let repentance_date = data.fields.repentance_date;


        //let status = repentance_date.value ? '<span class="green1">Покаялся</span>' : '<span class="reds">Не покаялся</span>'

        //document.getElementById('repentance_status').innerHTML = status;


        $("#datepicker_born_date").datepicker({
            dateFormat: "yy-mm-dd",
            maxDate: new Date(),
            yearRange: '1920:+0',
            onSelect: function (date) {

            }
        }).datepicker("setDate", data.fields.born_date.value).mousedown(function () {
            $('#ui-datepicker-div').toggle();
        });

        $("#firsVisit").datepicker({
            dateFormat: "yy-mm-dd",
            maxDate: new Date(),
            yearRange: '1920:+0',
            onSelect: function (date) {

            }
        }).datepicker("setDate", data.fields.coming_date.value)
        $("#repentanceDate").datepicker({
            dateFormat: "yy-mm-dd",
            maxDate: new Date(),
            yearRange: '1920:+0',
            onSelect: function (date) {

            }
        }).datepicker("setDate", data.fields.repentance_date.value)

        for (let prop in data.fields) {
            if (!data.fields.hasOwnProperty(prop)) continue

            if (prop == 'social') {

                for (let soc in social) {

                    if (document.getElementById(soc)) {
                        document.getElementById(soc).value = social[soc]
                    }
                }


                continue
            }

            if (prop == 'fullname') {

                fullname = data.fields[prop]['value'].split(' ');

                document.getElementById('first_name').value = fullname[1]
                document.getElementById('last_name').value = fullname[0]
                document.getElementById('middle_name').value = fullname[2]

                continue
            }


            if (document.getElementById(prop)) {
                document.getElementById(prop).value = data.fields[prop]['value'] || ' '
            }


        }
        data_for_drop['country'] = data.fields['country']['value'];
        data_for_drop['region'] = data.fields['region']['value'];
        data_for_drop['city'] = data.fields['city']['value'];
        data_for_drop['hierarchy'] = data.fields['hierarchy']['value'];
        data_for_drop['department'] = data.fields['department']['value'];
        data_for_drop['master'] = data.fields['master']['value'];
        data.fields['master_hierarchy'] = data.fields['master_hierarchy']['value']

        initializeCountry('api/v1.0/countries/');

        document.getElementById('region_drop').innerHTML = '<option selected="selected" value="">' + data_for_drop["region"] + '</option>';
        document.getElementById('town_drop').innerHTML = '<option selected="selected" value="">' + data_for_drop["city"] + '</option>';
        //
        //console.log(document.getElementById('town_drop').innerHTML)
        initDropCustom('api/v1.0/departments/', 'department_drop', data.fields['department']['value'])

        initDropCustom('api/v1.0/hierarchy/', 'statuses_drop', data.fields['hierarchy']['value'],

            function () {

                initDropCustom('api/v1.0/hierarchy/', 'statuses_drop_parent', data.fields['master_hierarchy'],
                    function () {
                        getLeader(data_for_drop['master'])
                    })
            })


        getDivisions(data.fields['divisions']['value']);
        getPatrnershipInfo();


    })
}

function convertImgToDataURLviaCanvas(url, callback, outputFormat) {
    let img = new Image();
    img.crossOrigin = 'Anonymous';
    img.onload = function () {
        let canvas = document.createElement('CANVAS');
        let ctx = canvas.getContext('2d');
        let dataURL;
        canvas.height = this.height;
        canvas.width = this.width;
        ctx.drawImage(this, 0, 0);
        dataURL = canvas.toDataURL(outputFormat);
        callback(dataURL);
        canvas = null;
    };
    img.src = url;
}

function handleFileSelect(evt) {

    let files = evt.target.files; // FileList object

    // Loop through the FileList and render image files as thumbnails.
    for (let i = 0, f; f = files[i]; i++) {

        // Only process image files.
        if (!f.type.match('image.*')) {
            continue;
        }

        let reader = new FileReader();

        // Closure to capture the file information.
        reader.onload = (function (theFile) {
            return function (e) {

                //document.querySelector(".anketa-photo img").src = e.target.result;
                document.querySelector("#impPopup img").src = e.target.result;
                //console.log(e.target.result)
                //$('#impPopup').css({'marginLeft':- $('#impPopup').width()/2, 'marginTop':- $('#impPopup').height()/2});
                document.querySelector("#impPopup").style.display = 'block';
                img.cropper({
                    aspectRatio: 1 / 1,
                    built: function () {
                        img.cropper("setCropBoxData", {width: "100", height: "50"});
                    }
                });

            };
        })(f);

        // Read in the image file as a data URL.
        reader.readAsDataURL(f);
    }
}


//inialize DATABASE LOCATIONS
function initializeCountry(url) {


    ajaxRequest(config.DOCUMENT_ROOT + url, null, function (data) {

        let results = data;
        let html = '<option value=""></option><option>Не выбрано</option>';
        //console.log(data_for_drop["country"])
        if (data_for_drop["country"] != '') {
            html += '<option selected value=" ">' + data_for_drop["country"] + '</option>';
        }
        //console.log(html)

        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('country_drop').innerHTML = html;
        $('#country_drop').select2().on("change", initializeRegions);

    });


}

function initializeRegions() {
    //Country 
    //console.log(active)
    let opt = {};
    opt['country'] = $("#country_drop").val();
    //console.log(opt)

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/regions/', opt, function (data) {
        if (data.length == 0) {
            document.getElementById('region_drop').innerHTML = '<option value=""> </option>';
            //document.getElementById('town_drop').innerHTML = '<option value=""> </option>';
            $('#town_drop').select2({tags: true});
            document.getElementById('region_drop').removeAttribute('disabled');
            document.getElementById('town_drop').removeAttribute('disabled');
        }

        let results = data;
        let html = '<option value=""></option><option>Не выбрано</option>';

        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        //document.getElementById('town_drop').setAttribute('disabled',true);
        document.getElementById('region_drop').innerHTML = html;
        document.getElementById('region_drop').removeAttribute('disabled');
        $('#region_drop').select2({placeholder: " "}).on("change", initializeTown);

    });


}


function initializeTown() {
    let opt = {};
    opt['region'] = $("#region_drop").val();

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/cities/', opt, function (data) {

        let results = data;
        let html = '<option value=""></option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('town_drop').innerHTML = html;
        document.getElementById('town_drop').removeAttribute('disabled');
        $('#town_drop').select2({tags: true, placeholder: " "});
    });


}

//INITIALIZE STATUS USER


function initDropCustom(url, parent_id, active, callback) {
    //Country 
    //console.log(active)


    ajaxRequest(config.DOCUMENT_ROOT + url, null, function (data) {

        let results = data.results;

        //let html = '<select multiple id="e1" style="width:300px">'
        if (parent_id == 'department_drop' || parent_id == 'statuses_drop') {
            let html = '';
        } else {
            let html = '<option>Не выбрано</option>';
        }
        for (let i = 0; i < results.length; i++) {

            if (active == results[i].title) {
                html += '<option selected="selected" value="' + results[i].id + '">' + results[i].title + '</option>'
                active = false
            } else {
                html += '<option value="' + results[i].id + '">' + results[i].title + '</option>'
            }

        }

        if (active) {
            html += '<option selected="selected" >' + active + '</option>'
        }

        document.getElementById(parent_id).innerHTML = html;

        let $eventSelect = $('#' + parent_id);

        $eventSelect.select2({
            // tags: true

        });
        $eventSelect.on("change", function (e) {

            getLeader(data_for_drop['master']);
            /*
             let url_region = 'api/v1.0/regions/?country=' + $(this).val()
             initializeRegions(url_region,'region_drop', data_for_drop['region'] )

             */
        });

        //$("#country_drop").trigger('change')
        if (callback) {
            callback();
        }
    });


}


function getLeader(active) {
    let id_dep = parseInt($("#department_drop option:selected").val()) || null;
    let level = parseInt($("#statuses_drop_parent option:selected").val()) || null;

    if (id_dep && level) {
        //  console.log(id_dep);
        //  console.log(level);
    }

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/short_users/?department=' + id_dep + '&hierarchy=' + level, null, function (data) {
        //Потрібен парент айди 

        let html = '<option>Не выбрано</option>';
        let results = data;
        //onsole.log(results)
        for (let i = 0; i < results.length; i++) {

            if (active == results[i].title) {
                html += '<option selected value="' + results[i].id + '">' + results[i].fullname + '</option>';
                active = false
            } else {
                html += '<option value="' + results[i].id + '">' + results[i].fullname + '</option>'
            }

        }

        if (active) {
            html += '<option selected="selected" >' + active + '</option>'
        }

        document.getElementById('leader_drop').innerHTML = html;
        let $eventSelect = $('#leader_drop');

        $eventSelect.select2({
            // tags: true

        })

    })


}

function getDivisions(str) {

    // console.log(str)
    let arr = str.split(',');
    //console.log(arr);


    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/divisions/', null, function (data) {


        let html = '';
        let results = data.results
        //console.log(results)

        for (let i = 0; i < results.length; i++) {

            if ($.inArray(results[i].title, arr) != -1) {
                html += '<option value="' + results[i].id + '" selected>' + results[i].title + '</option>'
            } else {
                html += '<option value="' + results[i].id + '">' + results[i].title + '</option>'
            }


        }


        document.getElementById('division_drop').innerHTML = html
        let $eventSelect = $('#division_drop');

        $eventSelect.select2({
            // tags: true

        })


    })
}


function getPatrnershipInfo() {

    let id = parseInt(getLastId());


    if (!id) {
        return
    }
    let url = config.DOCUMENT_ROOT + 'api/v1.1/partnerships/for_edit/?user=' + id;

    ajaxRequest(url, null, function (data) {

        document.getElementById('create_partner').style.display = 'none';
        document.getElementById('partner_wrap').style.display = 'block';

        data_for_drop['responsible_id'] = data.responsible_id;

        let date = data.date.split('.');
        date = date[2] + '-' + date[1] + '-' +date[0];
        let val = data.value || 0;
        $('#partner').attr('checked', true);
        $('#partner').parent('li').hide();
        $('#partner').closest('#partner_wrap').find('.left-info').find('li:first-child').hide();
        if (date) {
            $("#partner_date").datepicker('setDate', date).mousedown(function () {
                $('#ui-datepicker-div').toggle();
            })
        }
        document.getElementById('val_partnerships').value = val;
        //  document.getElementById('partner_name').innerHTML = data.responsible


        getManagerList(data_for_drop['responsible_id'])
    }, 'GET', true, null, {
        404: function () {
            document.getElementById('create_partner').style.display = 'block'
            getManagerList(data_for_drop['responsible_id'])
        }
    })
}


function getManagerList(active) {


    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.1/partnerships/simple/', null, function (data) {
        let html = '<option>Не выбрано</option>';

        data.forEach(function (partnership) {
            if (active == partnership.id) {
                html += '<option selected="selected" value="' + partnership.id + '">' + partnership.fullname + '</option>';
                active = false
            } else {
                html += '<option value="' + partnership.id + '">' + partnership.fullname + '</option>'
            }
        });
        document.getElementById('partner_drop').innerHTML = html;
        let $eventSelect = $('#partner_drop');

        $eventSelect.select2({
            // tags: true

        })

    });


}
function sendPassword() {

    let data = {};

    /*Блок проверки паролей */

    data['old_password'] = document.getElementById('old_password').value.trim();
    data['new_password1'] = document.getElementById('password1').value.trim();
    data['new_password2'] = document.getElementById('password2').value.trim();

    let json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'rest-auth/password/change/', json, function (data) {
        showPopup(data.success, 'SUCCESS');
        document.getElementById('old_password').value = "";
        document.getElementById('password1').value = "";
        document.getElementById('password2').value = "";
    }, 'POST', true, {
        'Content-Type': 'application/json'
    }, {
        400: function (data) {
            showPopup(data, 'ERROR');
        }
    });
}


function sendData() {

    let id = parseInt(getLastId());


    if (!id) {
        return
    }

    //let master = parseInt($("#leader_drop").val());


    let data = {


        "first_name": document.getElementById("first_name").value,
        "last_name": document.getElementById("last_name").value,
        "middle_name": document.getElementById("middle_name").value,

        "skype": document.getElementById("skype").value,
        "email": document.getElementById("email").value,
        "phone_number": document.getElementById("phone_number").value,
        "additional_phone": document.getElementById("additional_phone").value,
        "born_date": document.getElementById("datepicker_born_date").value || '',
        "coming_date": document.querySelector("input[name='first_visit']").value || '',
        "repentance_date": document.querySelector("input[name='repentance_date']").value || '',

        'country': $('#country_drop option:selected').html() == "Не выбрано" ? '' : $('#country_drop option:selected').html(),
        'region': $('#region_drop option:selected').html() == "Не выбрано" ? '' : $('#region_drop option:selected').html(),
        'city': $('#town_drop option:selected').html() == "Не выбрано" ? '' : $('#town_drop option:selected').html(),

        "vkontakte": document.getElementById('vkontakte').value || '',
        "facebook": document.getElementById('facebook').value || '',

        "odnoklassniki": document.getElementById('odnoklassniki').value || '',

        "address": document.getElementById('address').value || '',


        'department': parseInt(document.getElementById('department_drop').value),
        'divisions': $("#division_drop").val() || [],
        'hierarchy': parseInt(document.getElementById('statuses_drop').value),

        // "odnoklassniki": document.querySelector("input[name='ok']").value,

    };

    data['id'] = id


    let master = $('#leader_drop option:selected');


    if (master.html() == "Не выбрано") {
        data['master'] = 0;
    } else {
        if (master.attr('value') != undefined) {
            data['master'] = master.attr('value');
        }

    }

    //if (master) {

    //}

    /*Блок проверки паролей */

    // data['old_password'] = document.getElementById('old_password').value.trim();
    // data['password1'] = document.getElementById('password1').value.trim();
    // data['password2'] = document.getElementById('password2').value.trim();

    /*

     if(  !data['password1'].length   ||  !data['old_password'].length || data['password1'] != data['password2'] ){
     showPopup('Не совпадение паролей');
     document.getElementById('old_password').value = ''
     document.getElementById('password1').value = ''
     document.getElementById('password2').value = ''
     //document.getElementById('old_password').focus();


     Array.prototype.forEach.call(document.querySelectorAll(" .pass"), function(el) {
     // el.classList.add('error_valid')
     })
     }else{


     }

     */
    //Партнерка

    if (document.getElementById('partner') && document.getElementById('partner').checked) {

        // "responsible":"","value":"","date":"",
        data['value'] = parseInt(document.getElementById('val_partnerships').value) || 0;
        data['date'] = document.getElementById('partner_date').value || '';
        let id_partner = parseInt($("#partner_drop option:selected").val());

        //   debugger

        if (id_partner) {
            data['responsible'] = id_partner
        }

    } else {
        data['remove_partnership'] = 'true'; //gavnocod vlada
    }

    /*
     let url =config.DOCUMENT_ROOT + 'api/v1.0/short_users/?search=' + data["first_name"] +'+' + data["last_name"];
     ajaxRequest( url, null, function(answer) {

     if (answer.length) {
     let id  = answer[0].id;
     showPopup('Такой пользователей есть уже в БД');

     setTimeout(function() {
     window.location.href = '/account/' + id ;
     }, 1500);

     return;
     }else{
     */

    let json = JSON.stringify(data);

    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/create_user/', json, function (data) {


        if (!data.redirect) {
            showPopup(data.message)
        }

        let send_image = true;

        if (data.redirect && send_image) {

            //console.log(data.id)
            try {
                let fd = new FormData();

                let blob;
                let sr;
                if (!$('input[type=file]')[0].files[0]) {
                    blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                    fd.append('file', blob);
                    /*fd.append('source', sr)*/
                    fd.append('id', data.id)
                } else {
                    blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                    sr = $('input[type=file]')[0].files[0];
                    fd.append('file', blob);
                    fd.set('source', $('input[type=file]')[0].files[0], 'photo.jpg');
                    fd.append('id', data.id)
                }

                function dataURLtoBlob(dataurl) {
                    let arr = dataurl.split(',');
                    let mime = arr[0].match(/:(.*?);/)[1],
                        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
                    while (n--) {
                        u8arr[n] = bstr.charCodeAt(n);
                    }
                    return new Blob([u8arr], {type: mime});
                }

                let xhr = new XMLHttpRequest();
                xhr.withCredentials = true;
                xhr.open('POST', config.DOCUMENT_ROOT + 'api/v1.0/create_user/', true);
                //  xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.onreadystatechange = function () {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            /*setTimeout(function() {*/
                            window.location.href = '/account/' + data.id;
                            /*}, 1000);*/
                        }
                    }
                };
                xhr.send(fd);
            } catch (err) {
                console.log(err);
                window.location.href = '/account/' + data.id;
            }


        }
        // window.location.href = '/account/' + data.id;


    }, 'POST', true, {
        'Content-Type': 'application/json'
    });
    /*
     }

     })


     */


}
