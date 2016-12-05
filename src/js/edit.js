(function ($) {
    "use strict";
    $(document).ready(function () {
        init();
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

        $('#phone_number').click(function () {
            if ($(this).val().length === 0) {
                $(this).val('+')
            }
        });

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
        });

        $('#editCropImg').on('click', function () {
            let imgUrl;
            imgUrl = img.cropper('getCroppedCanvas').toDataURL('image/jpeg');
            $('#impPopup').fadeOut();
            $('#edit-photo').attr('data-source', document.querySelector("#impPopup img").src);
            $('.anketa-photo').html('<img src="' + imgUrl + '" />');
            img.cropper("destroy");
        });

        $("#partner_date").datepicker({
            dateFormat: "yy-mm-dd",
            onSelect: function (date) {

            }
        }).datepicker("setDate", new Date()).mousedown(function () {
            $('#ui-datepicker-div').toggle();
        });

        $('#create_partner_info').on('click', function () {
            let el = document.getElementById('partner_wrap');
            let create_el = document.getElementById('create_partner');
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
       $('#revert_edit').on('click', function () {
            let id = parseInt(id || getLastId());
            if (!id) {
                return
            }
            window.location.href = '/account/' + id
        });
        $('#save').on('click', function () {
            sendData();
        });
    });

    let data_for_drop = {};
    let img = $(".crArea img");

    function init(id) {
        id = parseInt(id || getLastId());
        if (!id) {
            return
        }
        ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/users/' + id + '/', null, function (data) {
            if (data.image) {
                $(".anketa-photo img").attr('src', data.image);
                convertImgToDataURLviaCanvas($(".anketa-photo img").attr('src'), function (data64) {
                    $(".anketa-photo img").attr('src', data64);
                })
            } else {
                $(".anketa-photo img").attr('src', '/static/img/no-usr.jpg');
                convertImgToDataURLviaCanvas($(".anketa-photo img").attr('src'), function (data64) {
                    $(".anketa-photo img").attr('src', data64);
                })
            }
            if ($('#edit-photo')) {
                $('#edit-photo').attr('data-source', data.image_source);
            }
            if (!data.fields) {
                return
            }
            let fullname;
            let social = data.fields.social;
            let repentance_date = data.fields.repentance_date;

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
            }).datepicker("setDate", data.fields.coming_date.value);

            $("#repentanceDate").datepicker({
                dateFormat: "yy-mm-dd",
                maxDate: new Date(),
                yearRange: '1920:+0',
                onSelect: function (date) {

                }
            }).datepicker("setDate", data.fields.repentance_date.value);

            for (let prop in data.fields) {
                if (!data.fields.hasOwnProperty(prop)) continue;

                if (prop == 'social') {

                    for (let soc in social) {

                        if (document.getElementById(soc)) {
                            document.getElementById(soc).value = social[soc];
                        }
                    }
                    continue
                }

                if (prop == 'fullname') {

                    fullname = data.fields[prop]['value'].split(' ');
                    document.getElementById('first_name').value = fullname[1];
                    document.getElementById('last_name').value = fullname[0];
                    document.getElementById('middle_name').value = fullname[2];
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
            data.fields['master_hierarchy'] = data.fields['master_hierarchy']['value'];

            initializeCountry('api/v1.0/countries/');

            document.getElementById('region_drop').innerHTML = '<option selected="selected" value="">' + data_for_drop["region"] + '</option>';
            document.getElementById('town_drop').innerHTML = '<option selected="selected" value="">' + data_for_drop["city"] + '</option>';
            //
            //console.log(document.getElementById('town_drop').innerHTML)
            initDropCustom('api/v1.0/departments/', 'department_drop', data.fields['department']['value']);

            initDropCustom('api/v1.0/hierarchy/', 'statuses_drop', data.fields['hierarchy']['value'],
                function () {
                    initDropCustom('api/v1.0/hierarchy/', 'statuses_drop_parent', data.fields['master_hierarchy'],
                        function () {
                            getLeader(data_for_drop['master'])
                        })
                });

            getDivisions(data.fields['divisions']['value']);
            getPatrnershipInfo();
        })
    }

    function convertImgToDataURLviaCanvas(url, callback, outputFormat) {
        let img = new Image();
        img.crossOrigin = 'Anonymous';
        img.onload = function () {
            let canvas = document.createElement('canvas');
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
        evt.preventDefault();
        let files = evt.target.files; // FileList object

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

    function dataURLtoBlob(dataurl) {
                        let arr = dataurl.split(',');
                        let mime = arr[0].match(/:(.*?);/)[1],
                            bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
                        while (n--) {
                            u8arr[n] = bstr.charCodeAt(n);
                        }
                        return new Blob([u8arr], {type: mime});
                    }

//inialize DATABASE LOCATIONS
    function initializeCountry(url) {

        ajaxRequest(config.DOCUMENT_ROOT + url, null, function (data) {

            let results = data;
            let html = '<option value=""></option><option>Не выбрано</option>';
            if (data_for_drop["country"] != '') {
                html += '<option selected value=" ">' + data_for_drop["country"] + '</option>';
            }
            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
            document.getElementById('country_drop').innerHTML = html;
            $('#country_drop').select2().on("change", initializeRegions);
        });
    }

    function initializeRegions() {
        //Country
        let opt = {};
        opt['country'] = $("#country_drop").val();
        //console.log(opt)

        ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/regions/', opt, function (data) {
            if (data.length == 0) {
                document.getElementById('region_drop').innerHTML = '<option value=""> </option>';
                $('#town_drop').select2({tags: true});
                document.getElementById('region_drop').removeAttribute('disabled');
                document.getElementById('town_drop').removeAttribute('disabled');
            }

            let results = data;
            let html = '<option value=""></option><option>Не выбрано</option>';

            for (let i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '">' + data[i].title + '</option>';
            }
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
        ajaxRequest(config.DOCUMENT_ROOT + url, null, function (data) {
            let results = data.results,
                html;
            if (parent_id == 'department_drop' || parent_id == 'statuses_drop') {
                html = '';
            } else {
                html = '<option>Не выбрано</option>';
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

            $eventSelect.select2();
            $eventSelect.on("change", function (e) {

                getLeader(data_for_drop['master']);
            });

            if (callback) {
                callback();
            }
        });
    }

    function getLeader(active) {
        let id_dep = parseInt($("#department_drop option:selected").val()) || null;
        let level = parseInt($("#statuses_drop_parent option:selected").val()) || null;

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

            $eventSelect.select2()
        })
    }

    function getDivisions(str) {
        let arr = str.split(',');
        ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/divisions/', null, function (data) {
            let html = '';
            let results = data.results;

            for (let i = 0; i < results.length; i++) {
                if ($.inArray(results[i].title, arr) != -1) {
                    html += '<option value="' + results[i].id + '" selected>' + results[i].title + '</option>';
                } else {
                    html += '<option value="' + results[i].id + '">' + results[i].title + '</option>';
                }
            }
            document.getElementById('division_drop').innerHTML = html;
            let $eventSelect = $('#division_drop');

            $eventSelect.select2({})
        })
    }

    function getPatrnershipInfo() {

        let id = parseInt(getLastId());
        if (!id) {
            return
        }
        let url = config.DOCUMENT_ROOT + 'api/v1.1/partnerships/for_edit/?user=' + id;

        ajaxRequest(url, null, function (data) {

            $('#create_partner').css('display', 'none');
           $('#partner_wrap').css('display', 'block');

            data_for_drop['responsible_id'] = data.responsible_id;

            let date = data.date.split('.');
            date = date[2] + '-' + date[1] + '-' + date[0];
            let val = data.value || 0;
            $('#partner').attr('checked', true);
            $('#partner').parent('li').hide();
            $('#partner').closest('#partner_wrap').find('.left-info').find('li:first-child').hide();
            if (date) {
                $("#partner_date").datepicker('setDate', date).mousedown(function () {
                    $('#ui-datepicker-div').toggle();
                })
            }
            $('#val_partnerships').val(val);

            getManagerList(data_for_drop['responsible_id'])
        }, 'GET', true, null, {
            404: function () {
                $('#create_partner').css('display', 'block');
                getManagerList(data_for_drop['responsible_id']);
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
            $('#partner_drop').html(html);
            let $eventSelect = $('#partner_drop');
            $eventSelect.select2();
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

        let data = {
            "first_name": $("#first_name").val(),
            "last_name": $("#last_name").val(),
            "middle_name": $("#middle_name").val(),
            "skype": $("#skype").val(),
            "email": $("#email").val(),
            "phone_number": $("#phone_number").val(),
            "additional_phone": $("#additional_phone").val(),
            "born_date": $("#datepicker_born_date").val() || '',
            "coming_date": $("input[name='first_visit']").val() || '',
            "repentance_date": $("input[name='repentance_date']").val() || '',
            'country': $('#country_drop option:selected').html() == "Не выбрано" ? '' : $('#country_drop option:selected').html(),
            'region': $('#region_drop option:selected').html() == "Не выбрано" ? '' : $('#region_drop option:selected').html(),
            'city': $('#town_drop option:selected').html() == "Не выбрано" ? '' : $('#town_drop option:selected').html(),
            "vkontakte": $('#vkontakte').val() || '',
            "facebook": $('#facebook').val() || '',
            "odnoklassniki": $('#odnoklassniki').val() || '',
            "address": $('#address').val() || '',
            'department': parseInt($('#department_drop').val()),
            'divisions': $("#division_drop").val() || [],
            'hierarchy': parseInt($('#statuses_drop').val()),
        };

        data['id'] = id;
        let master = $('#leader_drop option:selected');
        if (master.html() == "Не выбрано") {
            data['master'] = 0;
        } else {
            if (master.attr('value') != undefined) {
                data['master'] = master.attr('value');
            }
        }

        if (document.getElementById('partner') && document.getElementById('partner').checked) {
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

        let json = JSON.stringify(data);

        ajaxRequest(config.DOCUMENT_ROOT + 'api/v1.0/create_user/', json, function (data) {
            if (!data.redirect) {
                showPopup(data.message)
            }
            let send_image = true;

            if (data.redirect && send_image) {
                try {
                    let fd = new FormData(),
                        blob;
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
                    let xhr = new XMLHttpRequest();
                    xhr.withCredentials = true;
                    xhr.open('POST', config.DOCUMENT_ROOT + 'api/v1.0/create_user/', true);
                    xhr.onreadystatechange = function () {
                        if (xhr.readyState == 4) {
                            if (xhr.status == 200) {
                                window.location.href = '/account/' + data.id;
                            }
                        }
                    };
                    xhr.send(fd);
                } catch (err) {
                    console.log(err);
                    window.location.href = '/account/' + data.id;
                }
            }

        }, 'POST', true, {
            'Content-Type': 'application/json'
        });
    }
})(jQuery);