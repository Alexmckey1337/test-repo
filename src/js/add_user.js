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

    $('.editprofile .top-text span').on('click', function () {
        $('.pop-up-splash').css('display', 'none');
    });

    $('button.close').on('click', function () {
        $('.pop-up-splash').css('display', 'none');
    });

})(jQuery);