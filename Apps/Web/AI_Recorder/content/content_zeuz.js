/* Content zeuz */
// const BrowserAppData = chrome || browser;

var hasChromeDebugger = false;

BrowserAppData.runtime.sendMessage({ 
    checkChromeDebugger: true
}).then(function(result) {
    hasChromeDebugger = result.status
});