(function ($) {
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
        function makeChooseResponsible(data) {
            let html = '<option value=""> </option><option>Не выбрано</option>';
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].fullname + '</option>';
            }
            document.getElementById('chooseResponsible').innerHTML = html;
            document.getElementById('chooseResponsible').removeAttribute('disabled');
            $('#chooseResponsible').select2();
        }

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

        $("#bornDate").datepicker({
            minDate: new Date(new Date().setFullYear(new Date().getFullYear() - 120)),
            maxDate: new Date(),
            dateFormat: 'yyyy-mm-dd'
        });

        $("#firsVisit").datepicker().datepicker({
            dateFormat: 'yyyy-mm-dd',
            maxDate: new Date(),
            setDate: new Date()
        });

        $("#repentanceDate").datepicker({
            dateFormat: 'yyyy-mm-dd',
            maxDate: new Date(),
            setDate: new Date()
        });

        $('#partner').click(function () {
            $('.hidden-partner').toggle()
        });

        var makeChooseCountry = getCountries().then(function (data) {
            let html = '<option value=""> </option><option>Не выбрано</option>';
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
            return html;
        });

        makeChooseCountry.then(function (html) {
            document.getElementById('chooseCountry').innerHTML = html;
        });

        var makeChooseDepartment = getDepartments().then(function (data) {
            let results;
            results = data.results;
            let html = '<option value=""> </option>';
            for (let i = 0; i < results.length; i++) {
                html += '<option value="' + results[i].id + '">' + results[i].title + '</option>';
            }
            return html;
        });
        makeChooseDepartment.then(function (html) {
            document.getElementById('chooseDepartment').innerHTML = html;
        });

        makeChooseStatus.then(function (html) {
            document.getElementById('chooseStatus').innerHTML = html;
        });

        makeChooseDivision.then(function (html) {
            document.getElementById('chooseDivision').innerHTML = html;
        });

        var makeChooseManager = getManagers().then(function (data) {
            let html = '<option value=""> </option><option>Не выбрано</option>';
            data.forEach(function (partnership) {
                html += '<option value="' + partnership.id + '">' + partnership.fullname + '</option>';
            });
            return html;
        });
        makeChooseManager.then(function (html) {
            document.getElementById('chooseManager').innerHTML = html;
        });
        var makeChooseResponsibleStatus = getResponsibleStatuses().then(function (data) {
            data = data.results;
            let html = '<option value=""> </option><option>Не выбрано</option>';
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
            return html;
        });
        makeChooseResponsibleStatus.then(function (html) {
            if (document.getElementById('chooseResponsibleStatus')) {
                document.getElementById('chooseResponsibleStatus').innerHTML = html;
            }
        });
        var makeChooseCountryCode = getCountryCodes().then(function (data) {
            let codes = '<option value=""> </option>';
            for (let i = 0; i < data.length; i++) {
                if (data[i].phone_code == 38) {
                    codes += '<option selected value="' + data[i].phone_code + '">' + data[i].title + ' ' + data[i].phone_code + '</option>';
                } else {
                    codes += '<option value="' + data[i].phone_code + '">' + data[i].title + ' ' + data[i].phone_code + '</option>';
                }
            }
            return codes;
        });
        makeChooseCountryCode.then(function (codes) {
            document.getElementById('chooseCountryCode').innerHTML = codes;
            let code = $('#chooseCountryCode').val();
            $('input[name="phone_numberCode"]').val(code);

        });

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
            let department = $(this).val();
            let status = $('#chooseResponsibleStatus').val();
            if (status) {
                getResponsible(department, status).then(function (data) {
                    makeChooseResponsible(data);
                });
            }
        });

        $('#chooseDepartment').on('change', function () {
            let department = $('#chooseDepartment').val();
            let status = $('#chooseStatus option:selected').attr('data-level');

            if (!!$('#chooseStatus').val()) {
                $('#chooseResponsible').attr('disabled', true);
                getResponsible(department, status).then(function (data) {
                    makeChooseResponsible(data);
                });
            }
        });
        $('#chooseStatus').on('change', function () {
            let department = $('#chooseDepartment').val();
            let status = $('#chooseStatus option:selected').attr('data-level');
            $('#chooseResponsible').attr('disabled', true);
            if (!!$('#chooseStatus').val()) {
                $('#chooseResponsible').attr('disabled', true);
                getResponsible(department, status).then(function (data) {
                    makeChooseResponsible(data);
                });
            }
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
            let status = $(this).val();
            let department = $('#chooseDepartment').val();
            if (department) {
                getResponsible(department, status).then(function (data) {
                    makeChooseResponsible(data);
                });
            }
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
        $('.pop-up-splash').css('display', 'none');
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


    function getUsers() {
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/hierarchy/', null, function (data) {
            data = data.results;
            let html = '<option value=""> </option>';
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
            document.getElementById('chooseStatus').innerHTML = html;
        });
    }

    function getRegions() {
        let opt = {};
        opt['country'] = $("#chooseCountry").val();
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/regions/', opt, function (data) {
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

    function getCities() {
        let opt = {};
        opt['region'] = $("#chooseRegion").val();
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.0/cities/', opt, function (data) {
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
            "search_name": $('#search_name').val(),
            "born_date": $("input[name='born_date']").val() || null,
            "phone_number": parseInt($("input[name='phone_numberCode']").val() + '' + $("input[name='phone_number']").val()),
            "additional_phone": $("#additional_phone").val(),
            "vkontakte": $("input[name='vk']").val(),
            "facebook": $("input[name='fb']").val(),
            "odnoklassniki": $("input[name='ok']").val(),
            "address": $("input[name='address']").val(),
            "skype": $("input[name='skype']").val(),
            "district": $("input[name='district']").val(),
            "region": $('#chooseRegion option:selected').html() == 'Не выбрано' ? '' : $('#chooseRegion option:selected').html(),
            'divisions': $('#chooseDivision').val() || [],
            'hierarchy': parseInt($("#chooseStatus").val()),
            'department': parseInt($("#chooseDepartment").val()),
            'city': $('#chooseCity option:selected').html() == 'Не выбрано' ? '' : $('#chooseCity option:selected').html(),
            'country': $('#chooseCountry option:selected').html() == 'Не выбрано' ? '' : $('#chooseCountry option:selected').html()
        };

        if ($('#partner').prop('checked')) {
            if (!$('#summa_partner').val()) {
                $('#summa_partner').css('border', '1px solid #d46a6a');
                return
            }
            if (!$('#chooseManager').val()) {
                $('#chooseManager').css('border', '1px solid #d46a6a');
                return
            }
            if (!$('#partnerFrom').val()) {
                $('#partnerFrom').css('border', '1px solid #d46a6a');
                return
            }
            data.partner = {
                "value": ($('#summa_partner').val()) ? parseInt($('#summa_partner').val()) : 0,
                "responsible": ($('#chooseManager').val()) ? parseInt($('#chooseManager').val()) : null,
                "date": $('#partnerFrom').val()
            }
        }

        if ($("#chooseResponsible").val()) {
            data["master"] = parseInt($("#chooseResponsible").val());
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
        ajaxRequest(CONFIG.DOCUMENT_ROOT + 'api/v1.1/users/', json, function (data) {
            if (data) {
                let fd = new FormData();
                if (!$('input[type=file]')[0].files[0]) {
                    fd.append('id', data.id)
                } else {
                    fd.set('source', $('input[type=file]')[0].files[0], 'photo.jpg');
                    let blob = dataURLtoBlob($(".anketa-photo img").attr('src'));
                    let sr = $('#edit-photo').attr('data-source');
                    fd.append('file', blob);
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
                xhr.open('POST', CONFIG.DOCUMENT_ROOT + 'api/v1.0/create_user/', true);

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