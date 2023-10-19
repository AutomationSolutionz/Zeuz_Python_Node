const metaData = {};
const browserAppData = chrome || browser;

import './back_zeuz.js';
// import '../common_files/poly_fill.js';

/* Zeuz function start */
var master = {};
var clickEnabled = true;

/* Open panel */

// import {getWindowSize} from "/back_zeuz.js";
function getWindowSize(callback) {
    chrome.storage.local.get('window', function(result) {
        var height = 740;
        //var width = 780;
        var width = 1110;
        if (result) {
            try {
                result = result.window;
                if (result.height) {
                    height = result.height;
                }
                if (result.width) {
                    width = result.width;
                }
            } catch (e) {
            }
        }
        callback(height, width);
    });
}

function open_panel(tab) {
    browserAppData.storage.local.set({
        meta_data: metaData
    })
    let contentWindowId = tab.windowId;
    if (master[contentWindowId] != undefined) {
        browserAppData.windows.update(master[contentWindowId], {
            focused: true
        }).catch(function(e) {
            master[contentWindowId] == undefined;
            open_panel(tab);
        });
        return;
    } else if (!clickEnabled) {
        return;
    }

    clickEnabled = false;
    setTimeout(function() {
        clickEnabled = true;
    }, 1000);

    var f = function(height, width) {
        browserAppData.windows.create({
            url: browserAppData.runtime.getURL("panel/index.html"),
            type: "popup",
            //height: 705,
            height: height,
            //width: 1366
            width: width
        }).then(function waitForPanelLoaded(panelWindowInfo) {
            return new Promise(function(resolve, reject) {
                let count = 0;
                let interval = setInterval(function() {
                    if (count > 100) {
                        reject("editor has no response");
                        clearInterval(interval);
                    }

                    browserAppData.tabs.query({
                        active: true,
                        windowId: panelWindowInfo.id,
                        status: "complete"
                    }).then(function(tabs) {
                        if (tabs.length != 1) {
                            count++;
                            return;
                        } else {
                            master[contentWindowId] = panelWindowInfo.id;
                            if (Object.keys(master).length === 1) {
                                create_menus();
                            }
                            resolve(panelWindowInfo);
                            clearInterval(interval);
                        }
                    })
                }, 200);
            });
        }).then(function bridge(panelWindowInfo){
            return browserAppData.tabs.sendMessage(panelWindowInfo.tabs[0].id, {
                selfWindowId: panelWindowInfo.id,
                commWindowId: contentWindowId
            });
        }).catch(function(e) {
            console.log(e);
        });
    };
    getWindowSize(f);
}

/* Create menu */
function create_menus() {
    browserAppData.contextMenus.create({
        id: "verifyText",
        title: "verifyText",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "verifyTitle",
        title: "verifyTitle",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "verifyValue",
        title: "verifyValue",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "assertText",
        title: "assertText",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "assertTitle",
        title: "assertTitle",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "assertValue",
        title: "assertValue",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "storeText",
        title: "storeText",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "storeTitle",
        title: "storeTitle",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
    browserAppData.contextMenus.create({
        id: "storeValue",
        title: "storeValue",
        documentUrlPatterns: ["<all_urls>"],
        contexts: ["all"]
    });
}


browserAppData.action.onClicked.addListener(open_panel);
browserAppData.windows.onRemoved.addListener(function(windowId) {
    let keys = Object.keys(master);
    for (let key of keys) {
        if (master[key] === windowId) {
            delete master[key];
            if (keys.length === 1) {
                browserAppData.contextMenus.removeAll();
            }
        }
    }
});

var port;
browserAppData.contextMenus.onClicked.addListener(function(info, tab) {
    port.postMessage({ cmd: info.menuItemId });
});

browserAppData.runtime.onConnect.addListener(function(m) {
    port = m;
});

/* After install open the url */
chrome.runtime.onInstalled.addListener(function (details) {
    if (details.reason === 'install') {
        console.log("Recorder Installed");
    }
});