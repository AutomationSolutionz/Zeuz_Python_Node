const browserAppData = chrome || browser;
const tabs = {};
const inspectFile = 'inspect.js';
const activeIcon = 'active-64.png';
const defaultIcon = 'small_logo.png';
var zeuz_url;
var zeuz_key;
var zeuz_node_id;

fetch("data.json")
    .then(Response => Response.json())
    .then(data => {
        zeuz_url = data.url;
        zeuz_key = data.apiKey;
        zeuz_node_id = data.nodeId;
        browserAppData.storage.local.set({
            url: zeuz_url,
            key: zeuz_key,
            nodeId: zeuz_node_id,
        },
            function () {
                console.log("Logged in successfully!");
            });
    });

function logout() {
    browserAppData.storage.local.remove(['key'], function () {
        alert("Logged out successfully!");
    });
}

browserAppData.contextMenus.onClicked.addListener(logout);

const inspect = {
    toggleActivate: (id, type, icon) => {
        // this.id = id;
        // browserAppData.tabs.executeScript(id, { file: inspectFile }, () => { browserAppData.tabs.sendMessage(id, { action: type }); });
        // browserAppData.scripting.executeScript({
        //   target: {tabId: id},
        //   files: [inspectFile]
        // });
        browserAppData.tabs.sendMessage(id, {
            action: type
        }).then((response) => {
            console.log("Message from the content script:");
            console.log(response);
        })
            .catch((error) => {
                console.error(`Error: ${error}`)
            });
        browserAppData.action.setIcon({
            tabId: id,
            path: {
                19: 'icons/' + icon
            }
        });
    }
};

function isSupportedProtocolAndFileType(urlString) {
    if (!urlString) {
        return false;
    }
    const supportedProtocols = ['https:', 'http:', 'file:'];
    const notSupportedFiles = ['xml', 'pdf', 'rss'];
    const extension = urlString.split('.').pop().split(/\#|\?/)[0];
    // const url = document.createElement('a');
    // url.href = urlString;
    const cond = supportedProtocols.indexOf(urlString.split("/")[0]) !== -1 && notSupportedFiles.indexOf(extension) === -1;
    console.log(cond);
    console.log(urlString.split("/")[0]);
    return supportedProtocols.indexOf(urlString.split("/")[0]) !== -1 && notSupportedFiles.indexOf(extension) === -1;
}

function toggle(tab) {
    console.log("toggle()");

    if (!isSupportedProtocolAndFileType(tab.url)) return;

    if (!tabs[tab.id]) {
        tabs[tab.id] = Object.create(inspect);
        inspect.toggleActivate(tab.id, 'activate', activeIcon);
    }
    else {
        // deactivate plugin
        inspect.toggleActivate(tab.id, 'deactivate', defaultIcon);
        for (const tabId in tabs) {
            if (tabId == tab.id) delete tabs[tabId];
        }

    }

}

function deactivateItem(tab) {
    if (tab[0]) {
        if (isSupportedProtocolAndFileType(tab[0].url)) {
            for (const tabId in tabs) {
                if (tabId == tab[0].id) {
                    delete tabs[tabId];
                    inspect.toggleActivate(tab[0].id, 'deactivate', defaultIcon);
                }
            }
        }
    }
}

function getActiveTab() {
    browserAppData.tabs.query({
        active: true,
        currentWindow: true
    }, tab => {
        deactivateItem(tab);
    });
}

browserAppData.commands.onCommand.addListener(command => {
    if (command === 'toggle-xpath') {
        browserAppData.tabs.query({
            active: true,
            currentWindow: true
        }, tab => {
            toggle(tab[0]);
        });
    }
});

browserAppData.tabs.onUpdated.addListener(getActiveTab);
browserAppData.action.onClicked.addListener(toggle);
console.log(navigator.userAgentData.platform);
if (navigator.userAgentData.platform.toLowerCase().includes('mac')) {
    browserAppData.action.setTitle({
        title: "Cmd + Shift + X"
    });
}
browserAppData.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        if (request.apiName == 'ai_record_single_action') {
            var url = `${zeuz_url}/ai_record_single_action/`
            fetch(url, {
                method: "POST",
                headers: {
                    // "Content-Type": "application/json",
                    "X-Api-Key": zeuz_key,
                },
                body: request.data,
            })
                .then(response => response.json())
                .then(text => { console.log(text); sendResponse(text); })

            var url = `${zeuz_url}/node_ai_contents/`
            fetch(url, {
                method: "POST",
                headers: {
                    // "Content-Type": "application/json",
                    "X-Api-Key": zeuz_key,
                },
                body: JSON.stringify({
                    "dom_web": { "dom": request.html },
                    "node_id": zeuz_node_id
                }),
            })
                .then(response => response.json())
                .then(text => { console.log(text); sendResponse(text); })

            return true;  // Will respond asynchronously.
        } else if (request.apiName == 'node_ai_contents'){
            var url = `${zeuz_url}/node_ai_contents/`;
            fetch(url, {
                method: "POST",
                headers: {
                    // "Content-Type": "application/json",
                    "X-Api-Key": zeuz_key,
                },
                body: JSON.stringify({
                    "dom_web": { "dom": request.dom },
                    "node_id": zeuz_node_id
                }),
            })
                .then(response => response.json())
                .then(text => { console.log(text); sendResponse(text); })
        }
    }
);