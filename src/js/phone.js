'use strict';
import 'select2';
import 'select2/dist/css/select2.css';
import 'air-datepicker';
import 'air-datepicker/dist/css/datepicker.css';

$('document').ready(function () {
    $('#tasksDate').datepicker({
        dateFormat: 'yyyy-mm-dd',
        autoClose: true
    });

    // Events
    $('#add').on('click', function () {
        $('.popup_text_change').css('display','none');
        $('.complete-task').css('display','none');
        setTimeout(function () {
            $('#addTasks').addClass('active');
            $('.bg').addClass('active');
        }, 100);
    });
    $('#filter_button').on('click', function () {
        setTimeout(function () {
            $('#filterPopup').addClass('active');
            $('.bg').addClass('active');
        }, 100);
    });

    $('#executor_filter').select2();
    $('#department_filter').select2();
    $('#user_filter').select2();
    $('#type_filter').select2();
});
