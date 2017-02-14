(function ($) {
    let img = $(".crArea img");

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
        let html = '<option value="" selected>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].fullname + '</option>';
        }
        document.getElementById('chooseResponsible').innerHTML = html;
        document.getElementById('chooseResponsible').removeAttribute('disabled');
        $('#chooseResponsible').select2();
    }

    function handleFileSelect(e) {
        e.preventDefault();
        let files = e.target.files; // FileList object

        // Loop through the FileList and render image files as thumbnails.
        for (let i = 0, file; file = files[i]; i++) {

            // Only process image files.
            if (!file.type.match('image.*')) {
                continue;
            }

            let reader = new FileReader();

            // Closure to capture the file information.
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
            })(file);

            // Read in the image file as a data URL.
            reader.readAsDataURL(file);
        }
    }


    $('#file').on('change', handleFileSelect);
    $('#file_upload').on('click', function (e) {
        e.preventDefault();
        $('#file').click();
    });

    $('#impPopup').click(function (el) {
        if (el.target != this) {
            return
        }
        $(this).fadeOut();
        $('input[type=file]').val('');
        img.cropper("destroy")
    });

    $('#impPopup .close').on('click', function () {
        $('#impPopup').fadeOut();
        $('#file').val('');
        img.cropper("destroy");
    });

    $('#editCropImg').on('click', function () {
        let imgUrl;
        imgUrl = img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
        $('#impPopup').fadeOut();
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
        $('.anketa-photo').html('<img src="' + imgUrl + '" />');
        img.cropper("destroy");
    });


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

    function makeChooseCountry() {
        getCountries().then(function (data) {
            let html = '<option value="" selected>Не выбрано</option>';
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
            document.getElementById('chooseCountry').innerHTML = html;
        });
    }

    makeChooseCountry();

    function makeChooseDepartment() {
        getDepartments().then(function (data) {
            let results;
            results = data.results;
            let html = '<option value="">Выбирите отдел> </option>';
            for (let i = 0; i < results.length; i++) {
                html += '<option value="' + results[i].id + '">' + results[i].title + '</option>';
            }
            document.getElementById('chooseDepartment').innerHTML = html;
            $('#chooseDepartment').attr('disabled', false);
        });
    }

    makeChooseDepartment();

    makeChooseStatus().then(function (html) {
        document.getElementById('chooseStatus').innerHTML = html;
    });

    makeChooseDivision().then(function (html) {
        document.getElementById('chooseDivision').innerHTML = html;
    });

    getManagers().then(function (data) {
        let html = '<option value="" selected>Не выбрано</option>';
        data.forEach(function (partnership) {
            html += '<option value="' + partnership.id + '">' + partnership.fullname + '</option>';
        });
        return html;
    }).then(function (html) {
        document.getElementById('chooseManager').innerHTML = html;
    });
    getResponsibleStatuses().then(function (data) {
        data = data.results;
        let html = '<option value="" selected>Не выбрано</option>';
        for (let i = 0; i < data.length; i++) {
            html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
        }
        return html;
    }).then(function (html) {
        if (document.getElementById('chooseResponsibleStatus')) {
            document.getElementById('chooseResponsibleStatus').innerHTML = html;
        }
    });
    getCountryCodes().then(function (data) {
        let codes = '<option value=""> </option>';
        for (let i = 0; i < data.length; i++) {
            if (data[i].phone_code == 38) {
                codes += '<option selected value="' + data[i].phone_code + '">' + data[i].title + ' ' + data[i].phone_code + '</option>';
            } else {
                codes += '<option value="' + data[i].phone_code + '">' + data[i].title + ' ' + data[i].phone_code + '</option>';
            }
        }
        return codes;
    }).then(function (codes) {
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
        let status = $('#chooseStatus').val();
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

    $("#chooseResponsibleStatus").on("change", function () {
        let status = $(this).val();
        let department = $('#chooseDepartment').val();
        if (department) {
            getResponsible(department, status).then(function (data) {
                makeChooseResponsible(data);
            });
        }
    });

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
})(jQuery);