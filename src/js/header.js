// //Hide element after click in another area display
document.body.addEventListener('click', function (el) {
    if (el.target == document.querySelector(".userImgWrap") || el.target == document.querySelector(".userImgWrap img")) {
        document.querySelector(".photo-hover").style.display == 'block' ? document.querySelector(".photo-hover").style.display = 'none' :
            document.querySelector(".photo-hover").style.display = 'block';
        document.querySelector('.massage-hover').style.display = 'none';
    } else if (el.target == document.querySelector('.sms') || el.target == document.querySelector('.sms span:last-child')) {
        document.querySelector('.massage-hover').style.display == 'block' ? document.querySelector('.massage-hover').style.display = 'none' :
            document.querySelector('.massage-hover').style.display = 'block';
        document.querySelector(".photo-hover").style.display = 'none';
    } else if (el.target == document.querySelector('.top input') || el.target == document.querySelector('#select2-filter-container')) {
        return
    } else {
        document.querySelector('.massage-hover').style.display = 'none';
        document.querySelector(".photo-hover").style.display = 'none';
        hideFilter();
    }
});
