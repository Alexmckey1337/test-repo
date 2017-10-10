'use strict';

export default function beautifyNumber(number) {
    return String(number).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ')
}