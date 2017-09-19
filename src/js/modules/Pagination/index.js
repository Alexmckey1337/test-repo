export default function makePagination(config) {
    let container = document.createElement('div'),
        input = document.createElement('input'),
        text = document.createElement('span'),
        doubleLeft = document.createElement('a'),
        doubleRight = document.createElement('a'),
        left = document.createElement('a'),
        right = document.createElement('a');
    $(input).attr({
        "type": "number",
        "max": config.pages,
        "min": 1
    });
    $(doubleLeft).addClass('double__left').append('<i class="fa fa-angle-double-left" aria-hidden="true"></i>');
    $(doubleLeft).on('click', function () {
        $(this).closest('.pagination').find('.pagination__input').val(1).trigger('change');
    });
    $(left).addClass('left').append('<i class="fa fa-angle-left" aria-hidden="true"></i>');
    $(left).on('click', function () {
        let val = parseInt($(this).closest('.pagination').find('.pagination__input').val());
        if (!!(val - 1)) {
            $(this).closest('.pagination').find('.pagination__input').val(val - 1).trigger('change');
        }
    });
    $(doubleRight).addClass('double__right').append('<i class="fa fa-angle-double-right" aria-hidden="true"></i>');
    $(doubleRight).on('click', function () {
        $(this).closest('.pagination').find('.pagination__input').val(config.pages).trigger('change');
    });
    $(right).addClass('right').append('<i class="fa fa-angle-right" aria-hidden="true"></i>');
    $(right).on('click', function () {
        let val = parseInt($(this).closest('.pagination').find('.pagination__input').val());
        if (!(val + 1 > config.pages)) {
            $(this).closest('.pagination').find('.pagination__input').val(val + 1).trigger('change');
        }
    });

    $(input).addClass('pagination__input').val(config.currentPage);
    $(text).addClass('text').text(`из ${config.pages}`);
    $(container).append(doubleLeft).append(left).append(input).append(text).append(right).append(doubleRight);

    $(container).find('.pagination__input').change(function () {
        let val = parseInt($(this).val());
        if (val <= 0) {
            $(container).find('.pagination__input').val(1).trigger('change');
            return
        }
        if (val > config.pages) {
            $(container).find('.pagination__input').val(config.pages).trigger('change');
            return
        }
        if (config.hasOwnProperty('id')) {
            config.callback({
                page: val
            }, config.id);
        } else {
            config.callback({
                page: val
            });
        }

    });
    $(config.container).html(container);
}