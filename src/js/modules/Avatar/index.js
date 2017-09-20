'use strict';
import 'cropper';
import 'cropper/dist/cropper.css';

export function handleFileSelect(e) {
    let $img = $(".crArea img"),
        files = e.target.files; // FileList object
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
                $img.attr('src', e.target.result);
                $("#impPopup").css('display', 'block');
                $img.cropper({
                    aspectRatio: 1 / 1,
                    built: function () {
                        $img.cropper("setCropBoxData", {width: "100", height: "100"});
                    }
                });
            };
        })();
        // Read in the image file as a data URL.
        reader.readAsDataURL(file);
    }
    croppUploadImg();
}

export function croppUploadImg() {
    $('.anketa-photo').on('click', function () {
        let $img = $(".crArea img"),
            flagCroppImg;
        $("#impPopup").css('display', 'block');
        $img.cropper({
            aspectRatio: 1 / 1,
            built: function () {
                $img.cropper("setCropBoxData", {width: "100", height: "100"});
            }
        });
        return flagCroppImg = true;
    });
}

export function dataURLtoBlob(dataurl) {
    let arr = dataurl.split(',');
    let mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type: mime});
}