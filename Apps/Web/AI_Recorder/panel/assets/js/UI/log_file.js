/* Start zuez log function */
class Log {

    /* exq the initial time */
    constructor(container) {
        this.container = container;
    }

    info(str) {
        this._write("Passed : " + str, "log-info");
        var successCount = $('#passed_record').html();
        var newCount = parseInt(successCount) + 1;
        $('#passed_record').html(newCount);
    }

    log(str) {
        this._write(str, "log-info");
    }

    error(str) {
        this._write("Failed : " + str, "log-error");
        var errorCount = $('#failed_record').html();
        var newCount = parseInt(errorCount) + 1;
        $('#failed_record').html(newCount);
    };

    _write(str, className) {
        let textElement = document.createElement('p');
        textElement.setAttribute("class", className);
        textElement.textContent = str;
        this.container.appendChild(textElement);
        this.container.scrollIntoView(false);

        var disableCounter = $('#disable-count').val();
        $('#disable_record').html(disableCounter);
    }

    logHTML(str) {
        this.container.innerHTML = str;
        this.container.scrollIntoView(false);
    }

    logScreenshot(imgSrc, title) {
        let className = "log-info";
        let textElement = document.createElement('p');
        textElement.setAttribute("class", className);

        var a = $('<a></a>').attr('target', '_blank').attr('href', imgSrc).attr('title', title).attr('download', title);
        var img = $('<img>').attr('src', imgSrc).addClass('thumbnail').css('display','none');

        $(textElement).append(a.append(img));
        this.container.appendChild(textElement);
        this.container.scrollIntoView(false);
    }
}

var help_log = new Log(document.getElementById("refercontainer"));
var zeuz_log = new Log(document.getElementById("logcontainer"));

document.getElementById("clear-log").addEventListener("click", function() {
    emptyNode(document.getElementById("logcontainer"));
}, false);
