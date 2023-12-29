var metaData = {};

fetch("./data.json")
    .then(Response => Response.json())
    .then(data => {
        metaData = data;
    });

const browserAppData = chrome || browser;

import './back_zeuz.js';
import './sentiment_analyzer.js';
import './back_reocrder.js';
// import '../common_files/poly_fill.js';

var master = {};
var clickEnabled = true;

/* Create menu */
function create_menus() {
    let menus = [
        ["Go_to_link", "Go to link"],
        ["Save_Text", "Save Text"],
        ["Validate_Text", "Validate Text"],
        // ["Validate_Text_By_AI", "Validate Text by AI"],
        ["Wait_For_Element_To_Appear", "Wait for Element to Appear"],
        ["Wait_For_Element_To_Disappear", "Wait for Element to Disappear"],
    ]
    for(let i =0; i< menus.length; i++){
        browserAppData.contextMenus.create({
            id: menus[i][0],
            title: menus[i][1],
            documentUrlPatterns: [
                "http://*/*",
                "https://*/*"
            ],
            contexts: ["all"]
        })
    }
    browserAppData.runtime.sendMessage({
        action: 'content_classify',
        text: "Hello world",
    })
    .then(()=>{
        console.log("Classify init finished");
        browserAppData.contextMenus.create({
            id: "Validate_Text_By_AI",
            title: "Validate Text by AI",
            documentUrlPatterns: [
                "http://*/*",
                "https://*/*"
            ],
            contexts: ["all"]
        })
    });
}


function getWindowSize(callback) {
    browserAppData.storage.local.get('window', async function(result) {

        // var width = 1110;
        var win = await chrome.windows.getCurrent();
        var height = Math.round(win.height*0.9);
        var width = Math.round(win.width/2);
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
        meta_data: metaData,
        recorded_actions: [],
    });
    let contentWindowId = tab.windowId;
    if (master[contentWindowId] != undefined) {
        browserAppData.windows.update(master[contentWindowId], {
            focused: true
        }).catch(function(e) {
            master[contentWindowId] = undefined;
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

var panelWindow;
async function open_panel_2(tab) {
    browserAppData.storage.local.set({
        meta_data: metaData,
        recorded_actions: [],
    });
    let contentWindowId = tab.windowId;
    console.log('panelWindow', panelWindow);
    var result = await browserAppData.storage.local.get(['panelWindow']);
    console.log('result.panelWindow', result.panelWindow);
    // console.log('result.panelWindow', result.panelWindow);

    if (result.panelWindow && result.panelWindow[contentWindowId]) {
        browserAppData.windows.update(result.panelWindow[contentWindowId], {
            focused: true
        }).catch(function(e) {
            console.log('panelWindow catch error', panelWindow);
            console.error('error', e);
            var panel_dict = result.panelWindow
            panel_dict[contentWindowId] = undefined;
            panelWindow = undefined;
            browserAppData.storage.local.set({
                panelWindow: panel_dict
            }).then(open_panel(tab));
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
                    }).then(async function(tabs) {
                        if (tabs.length != 1) {
                            count++;
                            return;
                        } else {
                            var result = await browserAppData.storage.local.get(['panelWindow']);
                            if (result.panelWindow) var panel_dict = result.panelWindow;
                            else var panel_dict = {};
                            panel_dict[contentWindowId] = panelWindowInfo.id;
                            await browserAppData.storage.local.set({
                                panelWindow: panel_dict
                            });
                            console.log('panel_dict', panel_dict);
                            panelWindow = panelWindowInfo.id;
                            console.log('opening panelWindow', panelWindow);
                            create_menus();
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

browserAppData.action.onClicked.addListener(open_panel_2);
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
    console.log(port);
});

/* After install open the url */
browserAppData.runtime.onInstalled.addListener(function (details) {
    if (details.reason === 'install') {
        console.log("Recorder Installed");
    }
});

var i_am_running = 0;
setInterval(()=>{
    i_am_running++;
},200)