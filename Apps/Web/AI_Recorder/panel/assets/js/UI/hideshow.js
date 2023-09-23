/* Zeuz show hide */
$(document).ready(function() {
    var showText = 'Show';
    var hideText = 'Hide';
    var is_visible = false;
    $('.toggle').prev().append(' <a href="#" class="toggleLink">' + hideText + '</a>');
    $('.toggle').show();
    $('a.toggleLink').click(function() {
        is_visible = !is_visible;
        if ($(this).text() == showText) {
            $(this).text(hideText);
            $(this).parent().next('.toggle').slideDown('slow');
        } else {
            $(this).text(showText);
            $(this).parent().next('.toggle').slideUp('slow');
        }
        return false;
    });
});

function getMouseActionElement(target) {
    let tagName = target.tagName;
    if ( tagName == "DIV") {
        return $("i." + target.id)[0];
    } else if (tagName == "I") {
        return target;
    }
    return null;
}


function setIconDisplay(display, element) {
    let plus = element.getElementsByClassName("fa fa-download")[0];
    let download = element.getElementsByClassName("fa fa-plus")[0];
    let color = display ? "rgb(156, 155, 155)": "rgb(223, 223, 223)";
    plus.style.color = color;
    download.style.color = color;
}

function mouseOnSuiteTitleIcon(event) {
    let tempElement = getMouseActionElement(event.target);
    if (tempElement == null) {
        return;
    }
    tempElement.style.color = "rgb(106, 105, 105)";
}

function mouseOnAndOutTestSuite(event) {
    var element = event.target;
    while (true) {
        if (element == undefined) {
            return;
        }
        if (element.id.includes("suite") && !element.id.includes("menu")) {
            break;
        }
        element = element.parentNode;
    }

    let display = undefined;
    if (event.type == "mouseover") {
        display = true;
    } else if (event.type == "mouseout") {
        display = false;
    }
    setIconDisplay(display, element);
}

function mouseOutSuiteTitleIcon(event) {
    let tempElement = getMouseActionElement(event.target);
    if (tempElement == null) {
        return;
    }
    tempElement.style.color = "rgb(167, 167, 167)";
}
