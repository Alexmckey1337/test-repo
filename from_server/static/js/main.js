var config ={
    'DOCUMENT_ROOT':'http://vocrm.org/'
}

$(".sandwich, .menu_item").click(function() {
    $(".sandwich").toggleClass("active");
});


$('.edit-close').click(function() {
    $(this).parent().remove();
});

$('.checkbox, .table-button span').click(function() {
    $(this).toggleClass('active');
});

$(document).on('click', '.sandwich-button', function() {
    $(this).toggleClass('button_rotate');
    $(this).siblings('.sandwich-block').toggle();
    $(this).parent().toggleClass('sandwich-open');
});

$(document).on('click', '.sandwich-block ul li span', function() {
    var tx = $(this).text();
    $(this).parents().siblings('.sandwich-cont').text(tx);
    $(this).parents().siblings('.sandwich-cont').attr('data-id', this.parentNode.getAttribute('data-id'))
        //$(this).parents().siblings('.sandwich-cont').attr('data-level', this.parentNode.getAttribute('data-level'))
    $(this).parents('.sandwich-block').toggle();
    $(this).parents().siblings('.sandwich-button').toggleClass('button_rotate');
    $(this).parents('.sandwich-wrap').toggleClass('shadow');
    document.querySelector(".sandwich-wrap").setAttribute('data-master', this.parentNode.getAttribute('data-master'));
    var id = this.parentNode.getAttribute('data-id');
    //createHierarhyDropBoxes(id);
    var id_ = document.getElementsByClassName('sandwich-wrap')[0].getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');
    var level = document.getElementsByClassName('hierarchy-wrap')[0].getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');
    var level_ = document.getElementsByClassName('hierarchy-wrap')[1].getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');

    if (id_ && level && level_ && !isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont"))) {
        createHierarhyDropBox_last(id_, level_);
    }


});

$(document).on('click', '.hierarchy-wrap .sandwich-block ul li span', function() {

    if (isElementExists(document.querySelector(".sandwich-wrap.hierarchy__level .sandwich-cont"))) {
        document.querySelector(".sandwich-wrap.hierarchy__level").remove();
        var id_ = document.getElementsByClassName('sandwich-wrap')[0].getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');
        var level = document.getElementsByClassName('hierarchy-wrap')[0].getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');
        var level_ = document.getElementsByClassName('hierarchy-wrap')[1].getElementsByClassName('sandwich-cont')[0].getAttribute('data-id');
        createHierarhyDropBox_last(id_, level_);
    }

})


$(document).on('click', '.arrow-table', function() {
    $(this).toggleClass('button_rotate');
});

$(document).on('click', '.emplyee-middle .add-button', function() {
    $('.emplyee_pop').toggle();
    $(this).toggleClass('more');
});

$(document).on('click', '.event-main-button', function() {
    $(this).siblings('.add-edit-block').toggle();
    $(this).toggleClass('more');
});


$("div.selectTabs").each(function() {
    var tmp = $(this);
    $(tmp).find(".lineTabs li").each(function(i) {
        $(tmp).find(".lineTabs li:eq(" + i + ") a").click(function() {
            var tab_id = i + 1;
            $(tmp).find(".lineTabs li").removeClass("active");
            $(this).parent().addClass("active");
            $(tmp).find(".tab_content table").stop(false, false).hide();
            $(tmp).find(".tab" + tab_id).stop(false, false).fadeIn(300);
            return false;
        });
    });
});

$(function() {
    if (isElementExists(document.getElementsByClassName('news')[0])) {
        ajaxRequest(config.DOCUMENT_ROOT+'api/users/current', null, function(data) {
            currentUser(data);

            ajaxRequest(config.DOCUMENT_ROOT+'api/navigation/', null, function(data) {
                createMenu(data.results, 1);
            });

            if (isElementExists(document.getElementsByClassName('apply')[0])) {
                document.getElementsByClassName('apply')[0].click();
            }
            //не використовується ?
            if (isElementExists(document.getElementById('hierarhy_dropbox_wrapper'))) {
                createHierarhyDropBox();
            }

            if (isElementExists(document.querySelector('.personal-data'))) {

                document.getElementById('name').value = data.first_name;
                document.getElementById('surname').value = data.last_name;
                document.getElementById('pantronic').value = data.middle_name;
                document.querySelector('.personal-data .mail-input').value = data.email;
                document.getElementById('tel-input').value = data.phone_number;
            }
        });

    }
    if (document.getElementById('emplee_registry')) {
        document.getElementById('emplee_registry').addEventListener('click', function() {
            AddNewUser();
        })
    }
    if (document.getElementsByClassName('topic_container')[0]){
        document.getElementsByClassName('topic_container')[0].addEventListener('click',function(){
          
           var status = $('.content_block div.search_cont').css('display') == 'block' ? 'none' : 'block';
            $('.content_block div.search_cont').css('display',status); 
        })
    }
    
});


$(window).load(function() {
    if (isElementExists(document.getElementsByClassName('news')[0])) {

        $("[data-toggle]").click(function() {
            var toggle_el = $(this).data("toggle");
            $(toggle_el).toggleClass("open-sidebar");
        });
        $(".swipe-area").swipe({
            swipeStatus: function(event, phase, direction, distance, duration, fingers) {
                if (phase == "move" && direction == "right") {
                    $(".container").addClass("open-sidebar");
                    return false;
                }
                if (phase == "move" && direction == "left") {
                    $(".container").removeClass("open-sidebar");
                    return false;
                }
            }
        });
    }
});

jQuery(function($) {
    $.datepicker.regional['ru'] = {
        monthNames: ['Яварь', 'Февраль', 'Март', 'Апрель',
            'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
            'Октябрь', 'Ноябрь', 'Декабрь'
        ],
        dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
        firstDay: 1,
    };
    $.datepicker.setDefaults($.datepicker.regional['ru']);
});