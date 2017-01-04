(function($) {
    $(document).ready(function () {
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

    $('#impPopup').click(function (el) {
        if (el.target != this) {
            return
        }
        $(this).hide();
        $('input[type=file]').val('');
        img.cropper("destroy")
    });

    $('#impPopup .top-text span').click(function () {
        $('#impPopup').hide();
        $('input[type=file]').val('');
        img.cropper("destroy");
    });

    $('#edit-photo').click(function () {
        if ($(this).attr('data-source')) {
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
    });

    $('#impPopup button').click(function () {
        let imgUrl;
        imgUrl = img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
        $('.anketa-photo').html('<img src="' + imgUrl + '" />');
        $('#impPopup').hide();
        img.cropper("destroy");
    });

    $.datepicker.setDefaults($.datepicker.regional["ru"]);

    $("#partnerFrom").datepicker().mousedown(function () {
        $('#ui-datepicker-div').toggle();
    });

    $("#bornDate").datepicker({yearRange: '1920:+0'}).mousedown(function () {
        $('#ui-datepicker-div').toggle();
    });

    $("#firsVisit").datepicker().datepicker("setDate", new Date()).mousedown(function () {
        $('#ui-datepicker-div').toggle();
    });

    $("#repentanceDate").datepicker().mousedown(function () {
        $('#ui-datepicker-div').toggle();
    });

    $('#partner').click(function () {
        $('.hidden-partner').toggle()
    });
    getCountries();
    getDepartments();
    getStatuses();
    getDivisions();
    getManagers();
    getResponsibleStatuses();
    getCountryCodes();

    let dep,
        stat;

    $("#chooseCountry").select2({placeholder: " "}).on("change", getRegions);
    $("#chooseRegion").select2({placeholder: " "}).on("change", getCities);
    $("#chooseCity").select2({placeholder: " ", tags: true});
    $("#chooseDepartment").select2({placeholder: " "});
    $("#chooseStatus").select2({placeholder: " "});
    $("#chooseDivision").select2({placeholder: " "});
    $("#chooseStatus").select2({placeholder: " "});
    $("#chooseManager").select2({placeholder: " "});
    $("#chooseResponsible").select2({placeholder: " "});
    $("#chooseResponsibleStatus").select2({placeholder: " "});
    $("#chooseCountryCode").select2({placeholder: " "}).on("select2:select", function (el) {
        document.querySelector('[name="phone_numberCode"]').value = el.target.value;
    });


    $("#chooseDepartment").on("change", function () {
        window.dep = $(this).val();
        document.getElementById('chooseResponsible').removeAttribute('disabled');
        getResponsible(window.dep, window.stat);
    });

    $('input[name="first_name"]').keyup(function () {
        if ($(this).val() !== 0) {
            document.querySelector("input[name='first_name']").style.border = '';
        }
    });

    $('input[name="last_name"]').keyup(function () {
        if ($(this).val() !== 0) {
            document.querySelector("input[name='last_name']").style.border = '';
        }
    });

    $('input[name="phone_number"]').keyup(function () {
        if ($(this).val() !== 0) {
            document.querySelector("input[name='phone_number']").style.border = '';
        }
    });

    $('input[name="email"]').keyup(function () {
        if ($(this).val() !== 0) {
            document.querySelector("input[name='email']").style.border = '';
        }
    });

    $('#chooseStatus').on('change', function () {
        if ($(this).val() == 1) {
            document.getElementById('kabinet').setAttribute('disabled', true);
        } else {
            document.getElementById('kabinet').removeAttribute('disabled');
        }
    });

    $("#chooseResponsibleStatus").on("change", function () {
        window.stat = $(this).val();
        document.getElementById('chooseResponsible').removeAttribute('disabled');
        getResponsible(window.dep, window.stat);
    });

    $("#chooseDepartment").on("change", function () {
        document.querySelector("#chooseDepartment + span .select2-selection").style.border = '';
    });

    $("#chooseDepartment").on("change", function () {
        document.querySelector("#chooseStatus + span .select2-selection").style.border = '';
    });

    document.getElementById('saveNew').addEventListener('click', createNewAcc);
});

let img = $(".crArea img");

$('.pop-up-splash').on('click', function (el) {
    if (el.target !== this) {
        return;
    }
    this.style.display = 'none';
});

$('.editprofile .top-text span').on('click', function () {
    $('.pop-up-splash').css('display','none');
});

$('button.close').on('click', function () {
    $('.pop-up-splash').css('display', 'none');
});

$('#addFileButton').on('click', function () {
    $('#addFile').click();
});

$('#addFile').on('change', selectFile);


// function getAll() {
//     getCountries();
//     getDepartments();
//     getStatuses();
//     getDivisions();
//     getManagers();
//     getResponsibleStatuses();
//     getCountryCodes();
// }

function getCountryCodes() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/countries/', null, function (data) {
        let code = '<option value=""> </option>';
        for (let i = 0; i < data.length; i++) {
            if (data[i].phone_code == 38) {
                code += '<option selected value="' + data[i].phone_code + '">' + data[i].title + ' ' + data[i].phone_code + '</option>';
            } else {
                code += '<option value="' + data[i].phone_code + '">' + data[i].title + ' ' + data[i].phone_code + '</option>';
            }
        }
        document.getElementById('chooseCountryCode').innerHTML = code;
        document.querySelector('[name="phone_numberCode"]').value = $('#chooseCountryCode').val();
    })
}


function getCountries() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/countries/', null, function (data) {
        let html = '<option value=""> </option><option>Не выбрано</option>';
        //let code = '<option value=""> </option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            /*if (data[i].code == 38) {
             code += '<option selected value="+'+data[i].code+'">'+data[i].title + ' +' + data[i].code +'</option>';
             } else {
             code += '<option value="+'+data[i].code+'">'+data[i].title + ' +' + data[i].code +'</option>';
             }*/
        }
        document.getElementById('chooseCountry').innerHTML = html;
        /*document.getElementById('chooseCountryCode').innerHTML = code;
         document.querySelector('[name="phone_numberCode"]').value = $('#chooseCountryCode').val();*/
    });
}

function getDepartments() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/departments/', null, function (data) {
        let results;
        results = data.results;
        let html = '<option value=""> </option>';
        for (let i = 0; i < results.length; i++) {
            html += '<option value="' + results[i].id + '">' + results[i].title + '</option>';
        }
        document.getElementById('chooseDepartment').innerHTML = html;
        console.log(results);
        GlobalParam.departments = results;
    });
}

function getStatuses() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/hierarchy/', null, function (data) {
        data = data.results;
        let html = '<option value=""> </option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('chooseStatus').innerHTML = html;
    });
}

function getResponsibleStatuses() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/hierarchy/', null, function (data) {
        data = data.results;
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('chooseResponsibleStatus').innerHTML = html;
        let stat = $("#chooseResponsibleStatus").val();
    });
}

function getDivisions() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/divisions/', null, function (data) {
        data = data.results;
        let html = '<option value=""> </option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('chooseDivision').innerHTML = html;
    });
}

function getUsers() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/hierarchy/', null, function (data) {
        data = data.results;
        let html = '<option value=""> </option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('chooseStatus').innerHTML = html;
    });
}

function getManagers() {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.1/partnerships/simple/', null, function (data) {
        let html = '<option value=""> </option><option>Не выбрано</option>';
        data.forEach(function (partnership) {
            html += '<option value="' + partnership.id + '">' + partnership.fullname + '</option>';
        });
        document.getElementById('chooseManager').innerHTML = html;
        GlobalParam.partnerships = data;
    });
}

function getRegions() {
    let opt = {};
    opt['country'] = $("#chooseCountry").val();
    ;
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/regions/', opt, function (data) {
        if (data.length == 0) {
            document.getElementById('chooseRegion').innerHTML = '<option value=""> </option>';
            document.getElementById('chooseCity').removeAttribute('disabled')
        }
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('chooseRegion').innerHTML = html;
        document.getElementById('chooseRegion').removeAttribute('disabled');
    });
}

function getResponsible(id, level) {
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/short_users/?department=' + id + '&hierarchy=' + level, null, function (data) {
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].fullname + '</option>';
        }
        document.getElementById('chooseResponsible').innerHTML = html;
    });
}

function getCities() {
    let opt = {};
    opt['region'] = $("#chooseRegion").val();
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/cities/', opt, function (data) {
        let html = '<option value=""> </option><option>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        document.getElementById('chooseCity').innerHTML = html;
        document.getElementById('chooseCity').removeAttribute('disabled')
    });
}

function selectFile(evt) {
    evt.preventDefault();
    let files = evt.target.files;
    for (let i = 0, f; f = files[i]; i++) {
        if (!f.type.match('image.*')) {
            continue;
        }
        let reader = new FileReader();
        reader.onload = (function (theFile) {
            return function (e) {
                document.querySelector("#impPopup img").src = e.target.result;
                document.querySelector("#impPopup").style.display = 'block';
                img.cropper({
                    aspectRatio: 1 / 1,
                    built: function () {
                        img.cropper("setCropBoxData", {width: "100", height: "50"});
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
        "email": $("input[name='email']").val(),
        "first_name": $("input[name='first_name']").val(),
        "last_name": $("input[name='last_name']").val(),
        "middle_name": $("input[name='middle_name']").val(),
        "born_date": $("input[name='born_date']").val(),
        "phone_number": $("input[name='phone_numberCode']").val() + '' + $("input[name='phone_number']").val(),
        "additional_phone": $("#additional_phone").val(),
        "vkontakte": $("input[name='vk']").val(),
        "facebook": $("input[name='fb']").val(),
        "odnoklassniki": $("input[name='ok']").val(),
        "address": $("input[name='address']").val(),
        "skype": $("input[name='skype']").val(),
        "district": $("input[name='district']").val(),
        "region": $('#chooseRegion option:selected').html() == 'Не выбрано' ? '' : $('#chooseRegion option:selected').html(),
        'responsible': $("#chooseManager").val(),
        'value': $("input[name='value']").val(),
        'date': $("input[name='partnership_date']").val(),
        'divisions': $('#chooseDivision').val() || '',
        'hierarchy': $("#chooseStatus").val(),
        'department': $("#chooseDepartment").val(),
        'repentance_date': $("input[name='repentance_date']").val(),
        'coming_date': $("input[name='first_visit']").val(),
        'city': $('#chooseCity option:selected').html() == 'Не выбрано' ? '' : $('#chooseCity option:selected').html(),
        'country': $('#chooseCountry option:selected').html() == 'Не выбрано' ? '' : $('#chooseCountry option:selected').html()
    };

    data['send_password'] = $('#kabinet').prop("checked");

    if ($("#chooseResponsible").val()) {
        data["master"] = $("#chooseResponsible").val();
    }

    if (!data['first_name']) {
        $("input[name='first_name']").css('border', '1px solid #d46a6a');
        return;
    } else {
        $("input[name='first_name']").css('border', '');
    }

    if (!data['last_name']) {
        $("input[name='last_name']").css('border', '1px solid #d46a6a');
        return;
    } else {
        $("input[name='last_name']").css('border', '');
    }

    if ($("#chooseCountry").val() == '206' || $("#chooseCountry").val() == '162') {
        if (!data['middle_name']) {
            $("input[name='middle_name']").css('border', '1px solid #d46a6a');
            return;
        } else {
            $("input[name='middle_name']").css('border', '');
        }
    } else {
        $("input[name='middle_name']").css('border', '');
    }

    if (!data['email']) {
        $("input[name='email']").css('border', '1px solid #d46a6a');
        return;
    } else {
        $("input[name='email']").css('border', '');
    }


    if (!data['hierarchy'] || !data['department']) {
        $("#chooseDepartment + span .select2-selection").css('border', '1px solid #d46a6a');
        $("#chooseStatus + span .select2-selection").css('border', '1px solid #d46a6a');
        return;
    } else {
        $("#chooseDepartment + span .select2-selection").css('border', '');
        $("#chooseStatus + span .select2-selection").css('border', '');
    }

    let num_reg = /^[0-9]*$/ig;
    if (!num_reg.test($("input[name='phone_number']").val())) {
        $("input[name='phone_number']").css('border', '1px solid #d46a6a');
        return;
    } else {
        $("input[name='phone_number']").css('border', '');
    }
    let val_reg = /^[0-9]*$/ig;
    if (!val_reg.test($("input[name='value']").val())) {
        $("input[name='value']").css('border', '1px solid #d46a6a');
        return;
    } else {
        $("input[name='value']").css('border', '');
    }
    let json = JSON.stringify(data);
    ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/create_user/', json, function (data) {
        if (data.redirect) {
            let fd = new FormData();
            if (!$('input[type=file]')[0].files[0]) {
                fd.append('id', data.id)
            } else {
                fd.set('source', $('input[type=file]')[0].files[0], 'photo.jpg');
                let blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                let sr = $('#edit-photo').attr('data-source');
                fd.append('file', blob);
                //fd.append('source', sr)
                fd.append('id', data.id)
            }
            function dataURLtoBlob(dataurl) {
                let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
                    bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
                while (n--) {
                    u8arr[n] = bstr.charCodeAt(n);
                }
                return new Blob([u8arr], {type: mime});
            }

            let xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open('POST', config.DOCUMENT_ROOT + 'api/v1.0/create_user/', true);

            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4) {

                    if (xhr.status == 200) {
                        showPopup(data.message);
                        setTimeout(function () {
                            window.location.href = '/account/' + data.id;
                        }, 1000);
                    }
                }
            };

            xhr.send(fd);
        } else if (data.message) {
            showPopup(data.message)
        }
    }, 'POST', true, {
        'Content-Type': 'application/json'
    });

}
})(jQuery);