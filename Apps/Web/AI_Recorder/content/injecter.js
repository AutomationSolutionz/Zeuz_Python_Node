// inject scripts for promot command
const browser = chrome || browser;
var injectingScript = document.createElement("script");
injectingScript.src = browser.runtime.getURL("page/prompt.js");
(document.head || document.documentElement).appendChild(injectingScript);
if (window === window.top) {
    window.addEventListener("message", function(e) {
        if (e.source.top == window && e.data &&
            e.data.direction == "from-page-script") {
            if (e.data.response) {
                switch (e.data.response) {
                    case "confirm":
                        selenium.browserbot.confirmationResponse = true;
                        if (e.data.value)
                            selenium.browserbot.confirmationMessage = e.data.value;
                        break;

                    case "prompt":
                        selenium.browserbot.promptResponse = true;
                        if (e.data.value)
                            selenium.browserbot.promptMessage = e.data.value;
                        break;

                    case "alert":
                        selenium.browserbot.alertResponse = true;
                        if(e.data.value)
                            selenium.browserbot.alertMessage = e.data.value;
                        break;
                }
            }

            if (e.data.recordedType) {
                switch (e.data.recordedType) {
                    case "confirm":
                        if (e.data.recordedResult == true) {
                            recorder.record("chooseOkOnNextConfirmation", [[""]], "", true, e.data.frameLocation);
                        } else {
                            recorder.record("chooseCancelOnNextConfirmation", [[""]], "", true, e.data.frameLocation);
                        }
                        recorder.record("assertConfirmation", [[e.data.recordedMessage]], "", false, e.data.frameLocation);
                        break;

                    case "prompt":
                        if (e.data.recordedResult != null) {
                            recorder.record("answerOnNextPrompt", [[e.data.recordedResult]], "", true, e.data.frameLocation);
                        } else {
                            recorder.record("chooseCancelOnNextPrompt", [[""]], "", true, e.data.frameLocation);
                        }
                        recorder.record("assertPrompt", [[e.data.recordedMessage]], "", false, e.data.frameLocation);
                        break;
                    case "alert":
                        recorder.record("assertAlert", [[e.data.recordedMessage]], "", false, e.data.frameLocation);
                        break;
                }
            }
        }
    })
}



// inject scripts for run script command

var runInjectingScript = document.createElement("script");
runInjectingScript.src = browser.runtime.getURL("page/runScript.js");
(document.head || document.documentElement).appendChild(runInjectingScript);

window.addEventListener("message", function(e) {
    if (e.source.top == window && e.data && e.data.direction == "from-page-runscript") {
        selenium.browserbot.runScriptResponse = true;
        selenium.browserbot.runScriptMessage = e.data.result;
    }
});