export default function pageCursor () {
    let container = document.querySelector('#container'),
        loaded = sessionStorage.getItem('loaded'),
        url = sessionStorage.getItem('url');
    if (container) {
        container.onscroll = function () {
            let scrolledTop = container.pageYOffset || container.scrollTop;
            sessionStorage.setItem('url', window.location.href);
            sessionStorage.setItem('positionTop', scrolledTop);
        };
        if (loaded) {
            if (sessionStorage.getItem('url') != window.location.href) {
                sessionStorage.setItem('positionTop', '0');
            } else {
                let positionTop = sessionStorage.getItem('positionTop');
                container.scrollTo(0, parseInt(positionTop));
            }
        } else {
            sessionStorage.setItem('loaded', true);
        }
    }
}