(function ($) {
    let flagCroppImg = false;
    let $img = $(".crArea img");

    function croppUploadImg() {
        $('.anketa-photo').on('click', function () {

            $("#impPopup").css('display', 'block');
            $img.cropper({
                aspectRatio: 1 / 1,
                built: function () {
                    $img.cropper("setCropBoxData", {width: "100", height: "50"});
                }
            });
            return flagCroppImg = true;
        });
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
            reader.onload = (function () {
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
        croppUploadImg();
    }

    function accordionAddUser() {
        $('.second_step').find('h2').on('click', function () {
            $(this).next('.info').slideToggle().siblings('.info:visible').slideUp();
            $(this).toggleClass('active').siblings('h2').removeClass('active');
        });
    }

    let img = $(".crArea img");

    $('#file').on('change', handleFileSelect);
    $('#file_upload').on('click', function (e) {
        e.preventDefault();
        $('#file').click();
    });

    $('#impPopup').click(function (el) {
        if (el.target != this) {
            return
        }
        $('#impPopup').fadeOut(300, function () {
            img.cropper("destroy");
        });
        $('input[type=file]').val('');
    });

    $('#impPopup .close').on('click', function () {
        $('#impPopup').fadeOut(300, function () {
            img.cropper("destroy");
        });
        $('#file').val('');
    });

    $('#editCropImg').on('click', function () {
        let imgUrl;
        imgUrl = img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
        $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
        $('.anketa-photo').html('<img src="' + imgUrl + '" />');
        $('#impPopup').fadeOut(300, function () {
            img.cropper("destroy");
        });
        return flagCroppImg = false;

    });

    $("#bornDate").datepicker({
        minDate: new Date(new Date().setFullYear(new Date().getFullYear() - 120)),
        maxDate: new Date(),
        dateFormat: 'yyyy-mm-dd',
        autoClose: true,
    });

    $("#firsVisit").datepicker().datepicker({
        dateFormat: 'yyyy-mm-dd',
        maxDate: new Date(),
        setDate: new Date(),
        autoClose: true,
    });

    $("#repentanceDate").datepicker({
        dateFormat: 'yyyy-mm-dd',
        maxDate: new Date(),
        setDate: new Date(),
        autoClose: true,
        // onSelect: function () {
        //     $('#spir_level').attr('disabled', false).select2();
        // }
    });
    $('#partnerFrom').datepicker({
        dateFormat: 'yyyy-mm-dd',
        maxDate: new Date(),
        setDate: new Date(),
        autoClose: true,
    });
    $('#partner').click(function () {
        $('.hidden-partner').toggle()
    });

    $('.editprofile .top-text span').on('click', function () {
        $('.pop-up-splash').css('display', 'none');
    });

    $('button.close').on('click', function () {
        $('.pop-up-splash').css('display', 'none');
    });

    $('.btn-block').find('.closeForm').on('click', function (e) {
        e.preventDefault();
        $('#addNewUserPopup').css('display', 'none');
        $(this).closest('form').get(0).reset();
        $(this).closest('form').find('input[type=file]').val('');
        $(this).closest('form').find('#edit-photo img').attr('src', '/static/img/no-usr.jpg');
    });

    $('.btn-block').find('.nextForm').on('click', function (e) {
        e.preventDefault();
        let flag = false;
        $('.must').each(function () {
           $(this). validate(function (valid) {
               return flag = valid;
           });
        });
        if (!flag) {
               showPopup(`Обязательные поля не заполнены либо введены некорректные данные`);
           } else {
               $(this).closest('form').css("transform","translate3d(-1020px, 0px, 0px)");
               let user = `${$('#last_name').val()} ${$('#first_name').val()} ${$('#middle_name').val()}`;
               $('.second_step').find('.user').html(user);
        }
    });

    $('.btn-block').find('.prevForm').on('click', function (e) {
        e.preventDefault();
        if ($('.second_step').find('h2').hasClass('active')) {
            $('.second_step').find('h2').removeClass('active');
            $('.second_step').find('.info:visible').slideUp(function () {
                $(this).closest('form').css("transform","translate3d(0px, 0px, 0px)");
        });
        } else {
            $(this).closest('form').css("transform","translate3d(0px, 0px, 0px)");
        }
    });

    $("#createUser").find('input').each(function () {

        $(this).keypress(function(event) {
	        let keycode = (event.keyCode ? event.keyCode : event.which);
	        if (keycode == '13') {
	            event.preventDefault();
            }
	        event.stopPropagation();
        });
    });


    accordionAddUser();

    $('.popap').on('click', function () {
        $(this).css('display', 'none');
    });
    $('.editprofile-screen').on('click', function (e) {
       e.stopPropagation();
    });

})(jQuery);