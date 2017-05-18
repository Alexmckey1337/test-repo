(function ($) {
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
    });

    $('.btn-block').find('.nextForm').on('click', function (e) {
        e.preventDefault();
        $(this).closest('form').css("transform","translate3d(-530px, 0px, 0px)");
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

    accordionAddUser();

    //Test
    // let $selectDepartment = $('#departments');
    //
    // function makeHomeGroupsList(ID) {
    //     let churchID = ID || $('#church_list').val();
    //     if (churchID && typeof parseInt(churchID) == "number") {
    //         return getHomeGroupsINChurches(churchID)
    //     }
    //     return new Promise(function (reject) {
    //         reject(null);
    //     })
    // }
    //
    // makeHomeGroupsList().then(function (data) {
    //     if (!results) {
    //         return null
    //     }
    //     let homeGroupsID = $('#home_groups_list').val();
    //     let results = data.results;
    //     let options = [];
    //     let option = document.createElement('option');
    //     $(option).val('').text('Выберите домашнюю группу').attr('selected', true).attr('disabled', true);
    //     options.push(option);
    //     results.forEach(function (item) {
    //         let option = document.createElement('option');
    //         $(option).val(item.id).text(item.get_title);
    //         if (homeGroupsID == item.id) {
    //             $(option).attr('selected', true);
    //         }
    //         options.push(option);
    //     });
    //     $('#home_groups_list').html(options);
    // });
    //
    // function makeChurches() {
    //     let departmentID = $selectDepartment.val();
    //     if (departmentID && typeof parseInt(departmentID) == "number") {
    //         getChurchesListINDepartament(departmentID).then(function (data) {
    //             console.log(departmentID);
    //             let selectedChurchID = $('#church_list').val();
    //             let options = [];
    //             let option = document.createElement('option');
    //             $(option).val('').text('Выберите церковь').attr('selected', true).attr('disabled', true);
    //             options.push(option);
    //             data.forEach(function (item) {
    //                 let option = document.createElement('option');
    //                 $(option).val(item.id).text(item.get_title);
    //                 if (selectedChurchID == item.id) {
    //                     $(option).attr('selected', true);
    //                 }
    //                 options.push(option);
    //             });
    //             $('#church_list').html(options).on('change', function () {
    //                 let churchID = $(this).val();
    //                 if (churchID && typeof parseInt(churchID) == "number") {
    //                     makeHomeGroupsList(churchID).then(function (data) {
    //                         let options = [];
    //                         let option = document.createElement('option');
    //                         $(option).val('').text('Выберите домашнюю группу').attr('selected', true).attr('disabled', true);
    //                         options.push(option);
    //                         data.forEach(function (item) {
    //                             let option = document.createElement('option');
    //                             $(option).val(item.id).text(item.get_title);
    //                             options.push(option);
    //                         });
    //                         $('#home_groups_list').html(options);
    //                     });
    //                 }
    //             }).trigger('change');
    //         });
    //     }
    // }
    //
    // $selectDepartment.on('change', function () {
    //     let option = document.createElement('option');
    //     $(option).val('').text('Выберите церковь').attr('selected', true);
    //     makeChurches();
    //     $('#home_groups_list').html(option);
    // });
    // makeChurches();
    //
    // $('#departments').on('change', function () {
    //     let status = $('#selectHierarchy').find('option:selected').data('level');
    //     let department = $(this).val();
    //     makeResponsibleList(department, status);
    // });
    // // after fix
    // makeResponsibleList($('#departments').val(), $('#selectHierarchy').find('option:selected').data('level'));
    // $('#selectHierarchy').on('change', function () {
    //     let department = $('#departments').val();
    //     let status = $(this).find('option:selected').data('level');
    //     makeResponsibleList(department, status);
    // });
    //
    // $('#departments').select2();

})(jQuery);