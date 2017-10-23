export default function (text, maxLength = 18) {
    let ret = text;
    if (ret.length > maxLength) {
        ret = ret.substr(0, maxLength) + "...";
    }
    return ret;
}