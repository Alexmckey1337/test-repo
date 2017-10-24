'use strict';

export default function pasteLink(el, link) {
    $(el).closest('.input').find('a').attr('href', link);
}