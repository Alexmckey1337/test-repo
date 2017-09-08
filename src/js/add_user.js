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
        position: 'top left',
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
    $('#partner').on('change', function () {
        $('.hidden-partner').toggle();
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
           $(this).validate(function (valid) {
               return flag = valid;
           });
           return flag;
        });
        if (!flag) {
               showPopup(`Обязательные поля не заполнены либо введены некорректные данные`);
           } else {
               $(this).closest('form').addClass('active');
               let user = `${$('#last_name').val()} ${$('#first_name').val()} ${$('#middle_name').val()}`;
               $('.second_step').find('.user').html(user);
        }
    });

    $('.btn-block').find('.prevForm').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').removeClass('active');
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

    $('.popap').on('click', function () {
        $(this).css('display', 'none');
    });

    $('.editprofile-screen').on('click', function (e) {
       e.stopPropagation();
    });

    function makeDuplicateUsers(config={}) {
        let firstName = $('#first_name').val() || null,
            middleName = $('#middle_name').val() || null,
            lastName = $('#last_name').val() || null,
            phoneNumber = $('#phoneNumber').val() || null;
        (firstName != null) && (config.first_name = firstName);
        (middleName != null) && (config.middle_name = middleName);
        (lastName != null) && (config.last_name = lastName);
        (phoneNumber != null) && (config.phone_number = phoneNumber);
        getDuplicates(config).then(data => {
            let table = `<table>
                        <thead>
                            <tr>
                                <th>ФИО</th>
                                <th>Город</th>
                                <th>Ответственный</th>
                                <th>Номер телефонна</th>
                            </tr>
                        </thead>
                        <tbody>${data.results.map(item => {
                            let master = item.master;
                            if (master == null) {
                                master = '';
                            } else {
                                master = master.fullname;
                            }
                            
                            return `<tr>
                                       <td><a target="_blank" href="${item.link}">${item.last_name} ${item.first_name} ${item.middle_name}</a></td>
                                       <td>${item.city}</td>
                                       <td>${master}</td>
                                       <td>********${item.phone_number.slice(-4)}</td>
                                     </tr>`;
                            }).join('')}</tbody>
                        </table>`;
            let count = data.count,
                page = config.page || 1,
                pages = Math.ceil(count / CONFIG.pagination_duplicates_count),
                showCount = (count < CONFIG.pagination_duplicates_count) ? count : data.results.length,
                text = `Показано ${showCount} из ${count}`,
                paginationConfig = {
                    container: ".duplicate_users__pagination",
                    currentPage: page,
                    pages: pages,
                    callback: makeDuplicateUsers
                };
            makePagination(paginationConfig);
            $('.pop-up_duplicate__table').find('.table__count').text(text);
            $('#table_duplicate').html('').append(table);
            $('#createUser').find('._preloader').css('opacity', '0');
            $('.preloader').css('display', 'none');
            $('.pop-up_duplicate__table').css('display', 'block');
        });
    }

        function makeDuplicateCount(config={}) {
        let firstName = $('#first_name').val() || null,
            middleName = $('#middle_name').val() || null,
            lastName = $('#last_name').val() || null,
            phoneNumber = $('#phoneNumber').val() || null;
        (firstName != null) && (config.first_name = firstName);
        (middleName != null) && (config.middle_name = middleName);
        (lastName != null) && (config.last_name = lastName);
        (phoneNumber != null) && (config.phone_number = phoneNumber);
        config.only_count = true;
        getDuplicates(config).then(data => {
            $('#duplicate_count').html(data.count);
            $('#createUser').find('._preloader').css('opacity', '0');
        });
    }

    let inputs = $('#first_name, #last_name, #middle_name, #phoneNumber');
    inputs.on('focusout', function () {
        $('#createUser').find('._preloader').css('opacity', '1');
        makeDuplicateCount();
    });

     $('#duplicate_link').on('click', function () {
         $('.preloader').css('display', 'block');
         makeDuplicateUsers();
     });

    $('.pop-up__table').find('.close_pop').on('click', function () {
        $('.pop-up__table').hide();
    });

    $('#last_name, #first_name, #middle_name, #phoneNumber').keypress(function (event) {
        let keycode = (event.keyCode ? event.keyCode : event.which);
	        if (keycode == '13') {
	            event.preventDefault();
	            $('#createUser').find('._preloader').css('opacity', '1');
	            makeDuplicateCount();
            }
	        event.stopPropagation();
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
})(jQuery);