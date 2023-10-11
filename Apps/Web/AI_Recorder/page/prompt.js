/* Start Zeuz promot js */
var originalPrompt = originalPrompt ? originalPrompt : window.prompt;
var nextPromptResult = false;
var recordedPrompt = null;

var originalConfirmation = originalConfirmation ? originalConfirmation : window.confirm;
var nextConfirmationResult = false;
var recordedConfirmation = null;

var originalAlert = originalAlert ? originalAlert : window.alert;
var nextAlertResult = false;
var recordedAlert = null;

function getFrameLocation() {
    let frameLocation = "";
    let currentWindow = window;
    let currentParentWindow;
    while (currentWindow !== window.top) {
        currentParentWindow = currentWindow.parent;
        for (let idx = 0; idx < currentParentWindow.frames.length; idx++)
            if (currentParentWindow.frames[idx] === currentWindow) {
                frameLocation = ":" + idx + frameLocation;
                currentWindow = currentParentWindow;
                break;
            }
    }
    frameLocation = "root" + frameLocation;
    return frameLocation;
}

if (window !== window.top) {

    window.prompt = function(text, defaultText) {
        if (document.body.hasAttribute("ZeuZPlayingFlag")) {
            return window.top.prompt(text, defaultText);
        } else {
            let result = originalPrompt(text, defaultText);
            let frameLocation = getFrameLocation();
            window.top.postMessage({
                direction: "from-page-script",
                recordedType: "prompt",
                recordedMessage: text,
                recordedResult: result,
                frameLocation: frameLocation
            }, "*");
            return result;
        }
    };

    window.confirm = function(text) {
        if (document.body.hasAttribute("ZeuZPlayingFlag")) {
            return window.top.confirm(text);
        } else {
            let result = originalConfirmation(text);
            let frameLocation = getFrameLocation();
            window.top.postMessage({
                direction: "from-page-script",
                recordedType: "confirm",
                recordedMessage: text,
                recordedResult: result,
                frameLocation: frameLocation
            }, "*");
            return result;
        }
    };

    window.alert = function(text) {
        if(document.body.hasAttribute("ZeuZPlayingFlag")){
            recordedAlert = text;
            window.top.postMessage({
                direction: "from-page-script",
                response: "alert",
                value: recordedAlert
            }, "*");
            return;
        } else {
            let result = originalAlert(text);
            let frameLocation = getFrameLocation();
            window.top.postMessage({
                direction:"from-page-script",
                recordedType: "alert",
                recordedMessage: text,
                recordedResult: result,
                frameLocation: frameLocation
            }, "*");
            return result;
        }
    };

} else {

    window.prompt = function(text, defaultText) {
        if (document.body.hasAttribute("setPrompt")) {
            recordedPrompt = text;
            document.body.removeAttribute("setPrompt");
            return nextPromptResult;
        } else {
            let result = originalPrompt(text, defaultText);
            let frameLocation = getFrameLocation();
            window.top.postMessage({
                direction: "from-page-script",
                recordedType: "prompt",
                recordedMessage: text,
                recordedResult: result,
                frameLocation: frameLocation
            }, "*");
            return result;
        }
    };
    window.confirm = function(text) {
        if (document.body.hasAttribute("setConfirm")) {
            recordedConfirmation = text;
            document.body.removeAttribute("setConfirm");
            return nextConfirmationResult;
        } else {
            let result = originalConfirmation(text);
            let frameLocation = getFrameLocation();
            window.top.postMessage({
                direction: "from-page-script",
                recordedType: "confirm",
                recordedMessage: text,
                recordedResult: result,
                frameLocation: frameLocation
            }, "*");
            return result;
        }
    };
    window.alert = function(text) {
        if(document.body.hasAttribute("ZeuZPlayingFlag")){
            recordedAlert = text;
            window.top.postMessage({
                direction: "from-page-script",
                response: "alert",
                value: recordedAlert
            }, "*");
            return;
        } else {
            let result = originalAlert(text);
            let frameLocation = getFrameLocation();
            window.top.postMessage({
                direction:"from-page-script",
                recordedType: "alert",
                recordedMessage: text,
                recordedResult: result,
                frameLocation: frameLocation
            }, "*");
            return result;
        }
    };
}

if (window == window.top) {
    window.addEventListener("message", function(event) {
        if (event.source == window && event.data &&
            event.data.direction == "from-content-script") {
            let result = undefined;
            switch (event.data.command) {
                case "setNextPromptResult":
                    nextPromptResult = event.data.target;
                    document.body.setAttribute("setPrompt", true);
                    window.postMessage({
                        direction: "from-page-script",
                        response: "prompt"
                    }, "*");
                    break;
                case "getPromptMessage":
                    result = recordedPrompt;
                    recordedPrompt = null;
                    window.postMessage({
                        direction: "from-page-script",
                        response: "prompt",
                        value: result
                    }, "*");
                    break;
                case "setNextConfirmationResult":
                    nextConfirmationResult = event.data.target;
                    document.body.setAttribute("setConfirm", true);
                    window.postMessage({
                        direction: "from-page-script",
                        response: "confirm"
                    }, "*");
                    break;
                case "getConfirmationMessage":
                    result = recordedConfirmation;
                    recordedConfirmation = null;
                    try{
                        console.error("no");
                        window.postMessage({
                            direction: "from-page-script",
                            response: "confirm",
                            value: result
                        }, "*");
                    } catch (e) {
                        console.error(e);
                    }
                    break;

                case "setNextAlertResult":
                    nextAlertResult = event.data.target;
                    document.body.setAttribute("setAlert", true);
                    window.postMessage({
                        direction: "from-page-script",
                        response: "alert"
                    }, "*");
                    break;
            }
        }
    });
}