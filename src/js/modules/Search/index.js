'use strict';

export default function getSearch(title) {
    let search = $('input[name="fullsearch"]').val();
    if (!search) return {};
    return {
        [title]: search
    }
}