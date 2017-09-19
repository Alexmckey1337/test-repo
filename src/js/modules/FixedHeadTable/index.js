export default function fixedTableHead() {
    let $tableOffset = $("#table-1").offset().top,
        $header = $("#table-1 > thead").clone(),
        $fixedHeader = $("#header-fixed").append($header),
        arrCellWidth = [];
    if ($tableOffset > 0) {
        $('.table').attr('data-offset', $tableOffset);
    } else {
        $tableOffset = $('.table').attr('data-offset');
    }
    $('#table-1 > thead').find('th').each(function () {
        let width = $(this).outerWidth();
        arrCellWidth.push(width);
    });
    $('#header-fixed > thead').find('th').each(function (index) {
        $(this).css({
            'width': arrCellWidth[index],
        })
    });

    $(".table").scroll(function () {
        let offset = $(this).scrollLeft(),
            sidebar = $('#sidebar').outerWidth();
        $('#header-fixed').css('left', (sidebar - offset));
    });

    $('#container').bind("scroll", function () {
        let offset = $(this).scrollTop();
        if (offset >= $tableOffset && $fixedHeader.is(":hidden")) {
            $fixedHeader.show();
        } else if (offset < $tableOffset) {
            $fixedHeader.hide();
        }
    });
}