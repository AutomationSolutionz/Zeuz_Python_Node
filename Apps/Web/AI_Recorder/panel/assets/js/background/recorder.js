/* Zeuz Background Start */
browserAppData = chrome || browser;
class BackgroundRecorder {

    /* Exq initial time */
    constructor() {
        this.currentRecordingTabId = {};
        this.openedTabNames = {};
        this.currentRecordingFrameLocation = {};
        this.currentRecordingWindowId = {};
        this.openedTabIds = {};
        this.openedTabCount = {};
        this.openedWindowIds = {};
        this.selfWindowId = -1;
        this.contentWindowId = -1;
        this.attached = false;
        this.rebind();
        setInterval(async ()=>{
            if (!this.attached) return;
			browserAppData.storage.local.get(null, function (result) {
				if (result.recorded_actions.length === 0) return;
                console.log("Opacity =================", result.recorded_actions);
				for(let i = 0; i < result.recorded_actions.length; i++){
					if (result.recorded_actions[i] === 'empty'){
                        // console.log("Opacity 2222 =================", result.recorded_actions);
						$("#record_label").text("Recording...");
						$("#record").attr('disabled', true).css('opacity',0.5);
						return;
					}
				}
                if($("#record_label").text() == 'Recording...'){
                    $("#record").removeAttr('disabled').css('opacity',1);
                    $("#record_label").text("Stop");
                    $('#record_icon').text('stop');
                }
			})
			return;
		}, 500)
        this.recording_flag = false
        setInterval(async ()=>{
            if (!this.attached) return;
			browserAppData.storage.local.get(null, function (result) {
				if (result.recorded_actions.length === 0) return;
				for(let i = 0; i < result.recorded_actions.length; i++){
					if (result.recorded_actions[i] === 'empty'){
						if (!this.recording_flag) this.recording_flag = true;
                        else{
                            var new_arr = [];
                            for (const action of result.recorded_actions) {
                                if (action !== 'empty') new_arr.push(action);
                            }
                            result.recorded_actions = new_arr;
                            browserAppData.storage.local.set({
                                recorded_actions: new_arr
                            })
                            this.recording_flag = false;
                            if($("#record_label").text() == 'Recording...'){
                                $("#record").removeAttr('disabled').css('opacity',1);
                                $("#record_label").text("Stop");
                                $('#record_icon').text('stop');
                            }
                        }
						return;
					}
				}
			})
			return;
		}, 30000)
    }

    /* Bind initial time */
    rebind() {
        this.tabsOnActivatedHandler = this.tabsOnActivatedHandler.bind(this);
        this.windowsOnFocusChangedHandler = this.windowsOnFocusChangedHandler.bind(this);
        this.tabsOnRemovedHandler = this.tabsOnRemovedHandler.bind(this);
        this.webNavigationOnCreatedNavigationTargetHandler = this.webNavigationOnCreatedNavigationTargetHandler.bind(this);
        this.addCommandMessageHandler = this.addCommandMessageHandler.bind(this);
    }

    /* Attach */
    attach() {
        console.log('attach1',this.attached);
        if (this.attached) {
            return;
        }
        this.attached = true;
        browserAppData.tabs.onActivated.addListener(this.tabsOnActivatedHandler);
        browserAppData.windows.onFocusChanged.addListener(this.windowsOnFocusChangedHandler);
        browserAppData.tabs.onRemoved.addListener(this.tabsOnRemovedHandler);
        browserAppData.webNavigation.onCreatedNavigationTarget.addListener(this.webNavigationOnCreatedNavigationTargetHandler);
        browserAppData.runtime.onMessage.addListener(this.addCommandMessageHandler);
    }

    /* Detach  */
    detach() {
        if (!this.attached) {
            return;
        }
        this.attached = false;
        browserAppData.tabs.onActivated.removeListener(this.tabsOnActivatedHandler);
        browserAppData.windows.onFocusChanged.removeListener(this.windowsOnFocusChangedHandler);
        browserAppData.tabs.onRemoved.removeListener(this.tabsOnRemovedHandler);
        browserAppData.webNavigation.onCreatedNavigationTarget.removeListener(this.webNavigationOnCreatedNavigationTargetHandler);
        browserAppData.runtime.onMessage.removeListener(this.addCommandMessageHandler);
    }

    /* Call window in focus change */
    windowsOnFocusChangedHandler(windowId) {
        // let testCase = getSelectedCase();
        let testCase = null;
        if (!testCase) {
            return;
        }
        let testCaseId = testCase.id;
        if (!this.openedTabIds[testCaseId]) {
            return;
        }

        if (windowId === browserAppData.windows.WINDOW_ID_NONE) {
            return;
        }

        if (this.currentRecordingWindowId[testCaseId] === windowId)
            return;

        let self = this;

        browserAppData.tabs.query({
            windowId: windowId,
            active: true
        }).then(function(tabs) {
            if(tabs.length === 0 || self.isPrivilegedPage(tabs[0].url)) {
                return;
            }

            if (tabs[0].id !== self.currentRecordingTabId[testCaseId]) {
                if (getRecordsArray().length === 0)
                    return;
                if (self.openedTabIds[testCaseId][tabs[0].id] == undefined)
                    return;
                self.currentRecordingWindowId[testCaseId] = windowId;
                self.currentRecordingTabId[testCaseId] = tabs[0].id;
                self.currentRecordingFrameLocation[testCaseId] = "root";
                addCommandAuto("selectWindow", [[self.openedTabIds[testCaseId][tabs[0].id]]], "");
            }
        });
    }

    /* call on remove hander */
    tabsOnRemovedHandler(tabId, removeInfo) {
        let testCase = getSelectedCase();
        if (!testCase) {
            return;
        }
        let testCaseId = testCase.id;
        if (!this.openedTabIds[testCaseId]) {
            return;
        }

        if (this.openedTabIds[testCaseId][tabId] != undefined) {
            if (this.currentRecordingTabId[testCaseId] !== tabId) {
                addCommandAuto("selectWindow", [
                    [this.openedTabIds[testCaseId][tabId]]
                ], "");
                addCommandAuto("close", [
                    [this.openedTabIds[testCaseId][tabId]]
                ], "");
                addCommandAuto("selectWindow", [
                    [this.openedTabIds[testCaseId][this.currentRecordingTabId[testCaseId]]]
                ], "");
            } else {
                addCommandAuto("close", [
                    [this.openedTabIds[testCaseId][tabId]]
                ], "");
            }
            delete this.openedTabNames[testCaseId][this.openedTabIds[testCaseId][tabId]];
            delete this.openedTabIds[testCaseId][tabId];
            this.currentRecordingFrameLocation[testCaseId] = "root";
        }
    }

    /* active handelar */
    tabsOnActivatedHandler(activeInfo) {
        let testCase = getSelectedCase();
        if (!testCase) {
            return;
        }
        let testCaseId = testCase.id;
        if (!this.openedTabIds[testCaseId]) {
            return;
        }

        var self = this;
        setTimeout(function() {
            if (self.currentRecordingTabId[testCaseId] === activeInfo.tabId && self.currentRecordingWindowId[testCaseId] === activeInfo.windowId)
                return;
            if (getRecordsArray().length === 0)
                return;
            if (self.openedTabIds[testCaseId][activeInfo.tabId] == undefined)
                return;
            self.currentRecordingTabId[testCaseId] = activeInfo.tabId;
            self.currentRecordingWindowId[testCaseId] = activeInfo.windowId;
            self.currentRecordingFrameLocation[testCaseId] = "root";
            addCommandAuto("selectWindow", [[self.openedTabIds[testCaseId][activeInfo.tabId]]], "");
        }, 150);
    }

    webNavigationOnCreatedNavigationTargetHandler(details) {
        let testCase = getSelectedCase();
        if (!testCase)
            return;
        let testCaseId = testCase.id;
        if (this.openedTabIds[testCaseId][details.sourceTabId] != undefined) {
            this.openedTabNames[testCaseId]["win_ser_" + this.openedTabCount[testCaseId]] = details.tabId;
            this.openedTabIds[testCaseId][details.tabId] = "win_ser_" + this.openedTabCount[testCaseId];
            if (details.windowId != undefined) {
                this.setOpenedWindow(details.windowId);
            } else {
                let self = this;
                browserAppData.tabs.get(details.tabId)
                .then(function(tabInfo) {
                    self.setOpenedWindow(tabInfo.windowId);
                });
            }
            this.openedTabCount[testCaseId]++;
        }
    };

    isPrivilegedPage (url) {
        if (url.substr(0, 13) == 'moz-extension' ||
            url.substr(0, 16) == 'chrome-extension') {
            return true;
        }
        return false;
    }
    
    addCommandMessageHandler(message, sender, sendRequest) {

        if (!message.command || this.openedWindowIds[sender.tab.windowId] == undefined)
            return;

        if (!getSelectedSuite() || !getSelectedCase()) {
            let id = "case" + zeuz_testCase.count;
            zeuz_testCase.count++;
            addTestCase("Untitled Test Case", id);
        }

        let testCaseId = getSelectedCase().id;

        if (!this.openedTabIds[testCaseId]) {
            this.openedTabIds[testCaseId] = {};
            this.openedTabNames[testCaseId] = {};
            this.currentRecordingFrameLocation[testCaseId] = "root";
            this.currentRecordingTabId[testCaseId] = sender.tab.id;
            this.currentRecordingWindowId[testCaseId] = sender.tab.windowId;
            this.openedTabCount[testCaseId] = 1;
        }

        if (Object.keys(this.openedTabIds[testCaseId]).length === 0) {
            this.currentRecordingTabId[testCaseId] = sender.tab.id;
            this.currentRecordingWindowId[testCaseId] = sender.tab.windowId;
            this.openedTabNames[testCaseId]["win_ser_local"] = sender.tab.id;
            this.openedTabIds[testCaseId][sender.tab.id] = "win_ser_local";
        }

        if (getRecordsArray().length === 0) {
            addCommandAuto("open", [
                [sender.tab.url]
            ], "");
        }

        /* Custom */
        //if (this.openedTabIds[testCaseId][sender.tab.id] == undefined)
        //return;

        if (message.frameLocation !== this.currentRecordingFrameLocation[testCaseId]) {
            let newFrameLevels = message.frameLocation.split(':');
            let oldFrameLevels = this.currentRecordingFrameLocation[testCaseId].split(':');
            while (oldFrameLevels.length > newFrameLevels.length) {
                addCommandAuto("selectFrame", [
                    ["relative=parent"]
                ], "");
                oldFrameLevels.pop();
            }
            while (oldFrameLevels.length != 0 && oldFrameLevels[oldFrameLevels.length - 1] != newFrameLevels[oldFrameLevels.length - 1]) {
                addCommandAuto("selectFrame", [
                    ["relative=parent"]
                ], "");
                oldFrameLevels.pop();
            }
            while (oldFrameLevels.length < newFrameLevels.length) {
                addCommandAuto("selectFrame", [
                    ["index=" + newFrameLevels[oldFrameLevels.length]]
                ], "");
                oldFrameLevels.push(newFrameLevels[oldFrameLevels.length]);
            }
            this.currentRecordingFrameLocation[testCaseId] = message.frameLocation;
        }

        if (message.command == "doubleClickAt") {
            var command = getRecordsArray();
            var select = getSelectedRecord();
            var length = (select == "") ? getRecordsNum() : select.split("-")[1] - 1;
            var equaln = getCommandName(command[length - 1]) == getCommandName(command[length - 2]);
            var equalt = getCommandTarget(command[length - 1]) == getCommandTarget(command[length - 2]);
            var equalv = getCommandValue(command[length - 1]) == getCommandValue(command[length - 2]);
            if (getCommandName(command[length - 1]) == "clickAt" && equaln && equalt && equalv) {
                deleteCommand(command[length - 1].id);
                deleteCommand(command[length - 2].id);
                if (select != "") {
                    var current = document.getElementById(command[length - 2].id)
                    current.className += ' selected';
                }
            }
        } else if(message.command.includes("Value") && typeof message.value === 'undefined') {
            zeuz_log.error("Error: This element does not have property 'value'. Please change to use storeText command.");
            return;
        } else if(message.command.includes("Text") && message.value === '') {
            zeuz_log.error("Error: This element does not have property 'Text'. Please change to use storeValue command.");
            return;
        } else if (message.command.includes("store")) {
            browserAppData.windows.update(this.selfWindowId, {focused: true})
            .then(function() {
                setTimeout(function() {
                    message.value = prompt("Enter the name of the variable");
                    if (message.insertBeforeLastCommand) {
                        addCommandBeforeLastCommand(message.command, message.target, message.value);
                    } else {
                        notification(message.command, message.target, message.value);
                        addCommandAuto(message.command, message.target, message.value);
                    }
                }, 100);
            })

            return;
        } 

        if (message.insertBeforeLastCommand) {
            addCommandBeforeLastCommand(message.command, message.target, message.value);
        } else {
            notification(message.command, message.target, message.value);
            addCommandAuto(message.command, message.target, message.value);
        }
    }

    setOpenedWindow(windowId) {
        this.openedWindowIds[windowId] = true;
    }

    setSelfWindowId(windowId) {
        this.selfWindowId = windowId;
    }

    getSelfWindowId() {
        return this.selfWindowId;
    }
}
