
function escape_attr(str) {
    var spaceS = 0;
    var spaceE = -1;
    var tempStr = str;
    var tempAttr = "";
    var tempValue = "";
    var processedTag = "";
    var flag = false;

    do {
        spaceS = str.indexOf(" ");
        spaceE = str.indexOf(" ", spaceS + 1);

        if (spaceE >= 0) {
            while (str.charAt(spaceE - 1) != "\'" && str.charAt(spaceE - 1) != "\"") {
                spaceE = str.indexOf(" ", spaceE + 1);
                if (spaceE < 0)
                    break;
            }
        }
        if (spaceS >= 0 && spaceE >= 0) {
            tempAttr = str.substring(spaceS + 1, spaceE);
            tempStr = str.substring(0, spaceS + 1);
            str = str.substring(spaceE);
        } else if (spaceS >= 0 && spaceE < 0) {
            tempAttr = str.substring(spaceS + 1, str.length - 1);
            tempStr = str.substring(0, spaceS + 1);
            str = "";
        } else {
            if (flag)
                processedTag += ">";
            else
                processedTag = str;
            break;
        }

        flag = true;
        var equal = tempAttr.indexOf("=");

        if (tempAttr.charAt(equal + 1) == "\'") {
            if (tempAttr.indexOf("\'") != -1) {
                var quotS = tempAttr.indexOf("\'");
                var quotE = tempAttr.lastIndexOf("\'");
                tempValue = tempAttr.substring(quotS + 1, quotE);
                tempAttr = tempAttr.substring(0, quotS + 1);
                tempValue = replace_char(tempValue);
                tempAttr += tempValue + "\'";
            }
        }
        if (tempAttr.charAt(equal + 1) == "\"") {
            if (tempAttr.indexOf("\"") != -1) {
                var dquotS = tempAttr.indexOf("\"");
                var dquotE = tempAttr.lastIndexOf("\"");
                tempValue = tempAttr.substring(dquotS + 1, dquotE);
                tempAttr = tempAttr.substring(0, dquotS + 1);
                tempValue = replace_char(tempValue);
                tempAttr += tempValue + "\"";
            }
        }
        processedTag += tempStr + tempAttr;
    } while (true)

    return processedTag;
};

function unescapeHtml(str) {
    return str
        .replace(/&amp;/gi, "&")
        .replace(/&quot;/gi, "\"")
        .replace(/&lt;/gi, "<")
        .replace(/&gt;/gi, ">")
        .replace(/&#39;/gi, "'");
};

function do_escape(str) {
    return str.replace(/[&"'<>]/g, (m) => ({ "&": "&amp;", '"': "&quot;", "'": "&#39;", "<": "&lt;", ">": "&gt;" })[m]);
}

function check_type(cutStr, replaceStr, mode) {
    switch (mode) {
        case 1:
            return cutStr += replaceStr + "&amp;";
            break;
        case 2:
            return cutStr += replaceStr + "&quot;";
            break;
        case 3:
            return cutStr += replaceStr + "&#39;";
            break;
        case 4:
            return cutStr += replaceStr + "&lt;";
            break;
        case 5:
            return cutStr += replaceStr + "&gt;";
            break;
        default:
            return cutStr;
            break;
    }
}

function escapeHTML(str) {
    var smallIndex = str.indexOf("<");
    var greatIndex = str.indexOf(">");
    var tempStr = "";
    var tempTag = "";
    var processed = "";
    var tempSmallIndex = 0;

    while (true) {
        if (smallIndex >= 0) {
            if (greatIndex >= 0) {
                do {
                    smallIndex += tempSmallIndex;
                    tempStr = str.substring(0, smallIndex);
                    tempTag = str.substring(smallIndex, greatIndex + 1);
                    tempSmallIndex = tempTag.lastIndexOf("<");

                } while (tempSmallIndex != 0)

                tempTag = escape_attr(tempTag);

                str = str.substring(greatIndex + 1);
                processed += replace_char(tempStr) + tempTag;
            } else {
                replace_char(str);
                break;
            }
        } else {
            replace_char(str);
            break;
        }

        smallIndex = str.indexOf("<");
        greatIndex = 0;
        do {
            greatIndex = str.indexOf(">", greatIndex + 1);
        } while (greatIndex < smallIndex && greatIndex != -1)
    }

    if (str != "")
        processed += replace_char(str);

    return processed;
}

function replace_char(str) {
    var pos = -1;
    var cutStr = "";
    var replaceStr = "";
    var doFlag = 0;
    var charType;

    while (true) {
        pos = str.indexOf("&", pos + 1);
        charType = 0;
        if (pos != -1) {
            if (str.substring(pos, pos + 5) == "&amp;") {
                charType = 1;
                replaceStr = str.substring(0, pos);
                str = str.substring(pos + 5);
            } else if (str.substring(pos, pos + 6) == "&quot;") {
                charType = 2;
                replaceStr = str.substring(0, pos);
                str = str.substring(pos + 6);
            } else if (str.substring(pos, pos + 5) == "&#39;") {
                charType = 3;
                replaceStr = str.substring(0, pos);
                str = str.substring(pos + 5);
            } else if (str.substring(pos, pos + 4) == "&lt;") {
                charType = 4;
                replaceStr = str.substring(0, pos);
                str = str.substring(pos + 4);
            } else if (str.substring(pos, pos + 4) == "&gt;") {
                charType = 5;
                replaceStr = str.substring(0, pos);
                str = str.substring(pos + 4);
            }

            if (charType != 0) {
                pos = -1;
                replaceStr = do_escape(replaceStr);
                cutStr = check_type(cutStr, replaceStr, charType);
                doFlag = 1;
            }
        } else {
            cutStr += str;
            break;
        }
    }
    if (doFlag == 0)
        return do_escape(str);
    else
        return cutStr;
};
