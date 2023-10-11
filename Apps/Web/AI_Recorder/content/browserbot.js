var BrowserBot = function(topLevelApplicationWindow) {
   this.topWindow = topLevelApplicationWindow;
    this.topFrame = this.topWindow;
    this.baseUrl = window.location.href;
    this.count = 1;
    this.buttonWindow = window;
    this.currentWindow = this.topWindow;
    this.currentWindowName = null;
    this.allowNativeXpath = true;
    this.xpathEvaluator = new XPathEvaluator('ajaxslt');
    this.isSubFrameSelected = false;
    this.altKeyDown = false;
    this.controlKeyDown = false;
    this.shiftKeyDown = false;
    this.metaKeyDown = false;
    this.modalDialogTest = null;
    this.recordedAlerts = new Array();
    this.recordedConfirmations = new Array();
    this.recordedPrompts = new Array();
    this.openedWindows = {};
    this.openedWindows["win_ser_local"] = this.topWindow;
    this.nextConfirmResult = true;
    this.nextPromptResult = '';
    this.newPageLoaded = false;
    this.pageLoadError = null;
    this.ignoreResponseCode = false;
    this.xhr = null;
    this.abortXhr = false;
    this.isXhrSent = false;
    this.isXhrDone = false;
    this.xhrOpenLocation = null;
    this.xhrResponseCode = null;
    this.xhrStatusText = null;
    this.shouldHighlightLocatedElement = false;
    this.uniqueId = "seleniumMarker" + new Date().getTime();
    this.pollingForLoad = new Object();
    this.permDeniedCount = new Object();
    this.windowPollers = new Array();
    this.browserbot = this;

    var self = this;

    objectExtend(this, PageBot.prototype);
    this._registerAllLocatorFunctions();

    this.recordPageLoad = function(elementOrWindow) {
        try {
            if (elementOrWindow.location && elementOrWindow.location.href) {
            } else if (elementOrWindow.contentWindow && elementOrWindow.contentWindow.location && elementOrWindow.contentWindow.location.href) {
            } else {
            }
        } catch (e) {
            self.pageLoadError = e;
            return;
        }
        self.newPageLoaded = true;
    };

    this.isNewPageLoaded = function() {
        var e;

        if (this.pageLoadError) {
            if (this.pageLoadError.stack) {
            }
            e = this.pageLoadError;
            this.pageLoadError = null;
            throw e;
        }

        if (self.ignoreResponseCode) {
            return self.newPageLoaded;
        } else {
            if (self.isXhrSent && self.isXhrDone) {
                if (!((self.xhrResponseCode >= 200 && self.xhrResponseCode <= 399) || self.xhrResponseCode == 0)) {
                    // TODO: for IE status like: 12002, 12007, ... provide corresponding statusText messages also.
                    e = "XHR ERROR: URL = " + self.xhrOpenLocation + " Response_Code = " + self.xhrResponseCode + " Error_Message = " + self.xhrStatusText;
                    self.abortXhr = false;
                    self.isXhrSent = false;
                    self.isXhrDone = false;
                    self.xhrResponseCode = null;
                    self.xhrStatusText = null;
                    throw new SeleniumError(e);
                }
            }
            return self.newPageLoaded && (self.isXhrSent ? (self.abortXhr || self.isXhrDone) : true);
        }
    };

    this.setAllowNativeXPath = function(allow) {
        this.xpathEvaluator.setAllowNativeXPath(allow);
    };

    this.setIgnoreAttributesWithoutValue = function(ignore) {
        this.xpathEvaluator.setIgnoreAttributesWithoutValue(ignore);
    };

    this.setXPathEngine = function(engineName) {
        this.xpathEvaluator.setCurrentEngine(engineName);
    };

    this.getXPathEngine = function() {
        return this.xpathEvaluator.getCurrentEngine();
    };
};

var PageBot = function() {};

BrowserBot.createForWindow = function(window, proxyInjectionMode) {
    var browserbot;
    if (browserVersion.isIE) {
        browserbot = new IEBrowserBot(window);
    } else if (browserVersion.isKonqueror) {
        browserbot = new KonquerorBrowserBot(window);
    } else if (browserVersion.isOpera) {
        browserbot = new OperaBrowserBot(window);
    } else if (browserVersion.isSafari) {
        browserbot = new SafariBrowserBot(window);
    } else {
        browserbot = new MozillaBrowserBot(window);
    }

    browserbot.proxyInjectionMode = proxyInjectionMode;
    browserbot.getCurrentWindow();
    return browserbot;
};


BrowserBot.prototype.doModalDialogTest = function(test) {
    this.modalDialogTest = test;
};

BrowserBot.prototype.cancelNextConfirmation = function(result) {
    this.nextConfirmResult = result;
};

BrowserBot.prototype.hasAlerts = function() {
    return (this.recordedAlerts.length > 0);
};

BrowserBot.prototype.relayBotToRC = function(s) {
    var piMode = this.proxyInjectionMode;
    if (!piMode) {
        if (typeof(selenium) != "undefined") {
            piMode = selenium.browserbot && selenium.browserbot.proxyInjectionMode;
        }
    }
    if (piMode) {
        this.relayToRC("selenium." + s);
    }
};

BrowserBot.prototype.relayToRC = function(name) {
    var mySandbox = new Components.utils.Sandbox(this.currentWindow.location.href);
    mySandbox.name = name;
    var object = Components.utils.evalInSandbox(name, mySandbox);
    var s = 'state:' + serializeObject(name, object) + "\n";
    sendToRC(s, "state=true");
};

BrowserBot.prototype.resetPopups = function() {
    this.recordedAlerts = [];
    this.recordedConfirmations = [];
    this.recordedPrompts = [];
};

BrowserBot.prototype.getNextAlert = function() {
    var t = this.recordedAlerts.shift();
    if (t) {
        t = t.replace(/\n/g, " ");
    }
    this.relayBotToRC("browserbot.recordedAlerts");
    return t;
};

BrowserBot.prototype.hasConfirmations = function() {
    return (this.recordedConfirmations.length > 0);
};

BrowserBot.prototype.getNextConfirmation = function() {
    var t = this.recordedConfirmations.shift();
    this.relayBotToRC("browserbot.recordedConfirmations");
    return t;
};

BrowserBot.prototype.hasPrompts = function() {
    return (this.recordedPrompts.length > 0);
};

BrowserBot.prototype.getNextPrompt = function() {
    var t = this.recordedPrompts.shift();
    this.relayBotToRC("browserbot.recordedPrompts");
    return t;
};

BrowserBot.prototype.triggerMouseEvent = function(element, eventType, canBubble, clientX, clientY, button) {
    clientX = clientX ? clientX : 0;
    clientY = clientY ? clientY : 0;

    var screenX = 0;
    var screenY = 0;

    canBubble = (typeof(canBubble) == undefined) ? true : canBubble;
    var evt;
    if (element.fireEvent && element.ownerDocument && element.ownerDocument.createEventObject) {
        evt = createEventObject(element, this.controlKeyDown, this.altKeyDown, this.shiftKeyDown, this.metaKeyDown);
        evt.detail = 0;
        evt.button = button ? button : 1; 
        evt.relatedTarget = null;
        if (!screenX && !screenY && !clientX && !clientY && !this.controlKeyDown && !this.altKeyDown && !this.shiftKeyDown && !this.metaKeyDown) {
            element.fireEvent('on' + eventType);
        } else {
            evt.screenX = screenX;
            evt.screenY = screenY;
            evt.clientX = clientX;
            evt.clientY = clientY;
            try {
                window.event = evt;
            } catch (e) {
                selenium.browserbot.getCurrentWindow().selenium_event = evt;
            }
            element.fireEvent('on' + eventType, evt);
        }
    } else {
        var doc = goog.dom.getOwnerDocument(element);
        var view = goog.dom.getWindow(doc);

        evt = doc.createEvent('MouseEvents');
        if (evt.initMouseEvent) {
            evt.initMouseEvent(eventType, canBubble, true, view, 1, screenX, screenY, clientX, clientY,
                this.controlKeyDown, this.altKeyDown, this.shiftKeyDown, this.metaKeyDown, button ? button : 0, null);
        } else {
            evt.initEvent(eventType, canBubble, true);

            evt.shiftKey = this.shiftKeyDown;
            evt.metaKey = this.metaKeyDown;
            evt.altKey = this.altKeyDown;
            evt.ctrlKey = this.controlKeyDown;
            if (button) {
                evt.button = button;
            }
        }
        element.dispatchEvent(evt);
    }
};

BrowserBot.prototype.triggerDragEvent = function(element, target) {
    var getXpathOfElement = function(element) {
        if (element == null) {
            return "null";
        }
        if (element.parentElement == null) {
            return "/" + element.tagName;
        }


        var siblingElement = element.parentElement.children;
        var tagCount = 0;
        var totalTagCount = 0;
        var isFound = false;

        for (var i = 0; i < siblingElement.length; i++) {
            if (siblingElement[i].tagName == element.tagName && !isFound) {
                tagCount++;
                totalTagCount++;
            } else if (siblingElement[i].tagName == element.tagName) {
                totalTagCount++;
            }
            if (siblingElement[i] == element) {
                isFound = true;
            }
        }

        if (totalTagCount > 1) {
            return getXpathOfElement(element.parentElement) + "/" + element.tagName + "[" + tagCount + "]";
        }

        return getXpathOfElement(element.parentElement) + "/" + element.tagName;
    };
    var script = "                                              \
        function simulateDragDrop(sourceNode, destinationNode){\
        function createCustomEvent(type) {                     \
            var event = new CustomEvent('CustomEvent');        \
            event.initCustomEvent(type, true, true, null);     \
            event.dataTransfer = {                             \
                data: {                                        \
                },                                             \
                setData: function(type, val) {                 \
                    this.data[type] = val;                     \
                },                                             \
                getData: function(type) {                      \
                    return this.data[type];                    \
                }                                              \
            };                                                 \
            return event;                                      \
        }                                                      \
        function dispatchEvent(node, type, event) {            \
            if (node.dispatchEvent) {                          \
                return node.dispatchEvent(event);              \
            }                                                  \
            if (node.fireEvent) {                              \
                return node.fireEvent('on' + type, event);     \
            }                                                  \
        }                                                      \
        var event = createCustomEvent('dragstart');            \
        dispatchEvent(sourceNode, 'dragstart', event);         \
                                                               \
        var dropEvent = createCustomEvent('drop');             \
        dropEvent.dataTransfer = event.dataTransfer;           \
        dispatchEvent(destinationNode, 'drop', dropEvent);     \
                                                               \
        var dragEndEvent = createCustomEvent('dragend');       \
        dragEndEvent.dataTransfer = event.dataTransfer;        \
        dispatchEvent(sourceNode, 'dragend', dragEndEvent);    \
    }                                                          \
    simulateDragDrop(document.evaluate('" + getXpathOfElement(element) + "', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue, document.evaluate('" + getXpathOfElement(target) + "', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue);\
    ";
    var win = this.browserbot.getCurrentWindow();
    var doc = win.document;
    var scriptTag = doc.createElement("script");
    scriptTag.type = "text/javascript";
    scriptTag.text = script;
    doc.body.appendChild(scriptTag);
};
// END

BrowserBot.prototype._windowClosed = function(win) {
    try {
        var c = win.closed;
        if (c == null) return true;
        return c;
    } catch (ignored) {
        return true;
    }
};

BrowserBot.uniqueKey = 1;

BrowserBot.prototype._modifyWindow = function(win) {
    if (this._windowClosed(win)) {
        if (!this.proxyInjectionMode) {
        }
        return null;
    }
    if (!this.proxyInjectionMode) {
    }

    win.seleniumKey = BrowserBot.uniqueKey++;

    this.modifyWindowToRecordPopUpDialogs(win, this);

    if (!this.proxyInjectionMode) {
        this.modifySeparateTestWindowToDetectPageLoads(win);
    }
    if (win.frames && win.frames.length && win.frames.length > 0) {
        for (var i = 0; i < win.frames.length; i++) {
            try {
                this._modifyWindow(win.frames[i]);
            } catch (e) {}
        }
    }
    return win;
};

BrowserBot.prototype.selectWindow = function(target) {
    if (!target || target == "null") {
        this._selectTopWindow();
        return;
    }
    var result = target.match(/^([a-zA-Z]+)=(.*)/);
    if (!result) {
        this._selectWindowByWindowId(target);
        return;
    }
    locatorType = result[1];
    locatorValue = result[2];
    if (locatorType == "title") {
        this._selectWindowByTitle(locatorValue);
    }

    else if (locatorType == "name") {
        this._selectWindowByName(locatorValue);
    } else if (locatorType == "var") {
        var win = this.getCurrentWindow().eval(locatorValue);
        if (win) {
            this._selectWindowByName(win.name);
        } else {
            throw new SeleniumError("Window not found by var: " + locatorValue);
        }
    } else {
        throw new SeleniumError("Window locator not recognized: " + locatorType);
    }
};

BrowserBot.prototype.selectPopUp = function(windowId) {
    if (!windowId || windowId == 'null') {
        this._selectFirstNonTopWindow();
    } else {
        this._selectWindowByWindowId(windowId);
    }
};

BrowserBot.prototype._selectWindowByWindowId = function(windowId) {
    try {
        this._selectWindowByName(windowId);
    } catch (e) {
        this._selectWindowByTitle(windowId);
    }
};

BrowserBot.prototype._selectTopWindow = function() {
    this.currentWindowName = null;
    this.currentWindow = this.topWindow;
    this.topFrame = this.topWindow;
    this.isSubFrameSelected = false;
};

BrowserBot.prototype._selectWindowByName = function(target) {
    this.currentWindow = this.getWindowByName(target, false);
    this.topFrame = this.currentWindow;
    this.currentWindowName = target;
    this.isSubFrameSelected = false;
};

BrowserBot.prototype._selectFirstNonTopWindow = function() {
    var names = this.getNonTopWindowNames();
    if (names.length) {
        this._selectWindowByName(names[0]);
    }
};

BrowserBot.prototype._selectWindowByTitle = function(target) {
    var windowName = this.getWindowNameByTitle(target);
    if (!windowName) {
        this._selectTopWindow();
    } else {
        this._selectWindowByName(windowName);
    }
};

BrowserBot.prototype.selectFrame = function(target) {
    var frame;

    if (target.indexOf("index=") == 0) {
        target = target.substr(6);
        frame = this.getCurrentWindow().frames[target];
        if (frame == null) {
            throw new SeleniumError("Not found: frames[" + target + "]");
        }
        if (!frame.document) {
            throw new SeleniumError("frames[" + target + "] is not a frame");
        }
        this.currentWindow = frame;
        this.isSubFrameSelected = true;
    } else if (target == "relative=up" || target == "relative=parent") {
        this.currentWindow = this.getCurrentWindow().parent;
        this.isSubFrameSelected = (this._getFrameElement(this.currentWindow) != null);
    } else if (target == "relative=top") {
        this.currentWindow = this.topFrame;
        this.isSubFrameSelected = false;
    } else {
        frame = this.findElement(target);
        if (frame == null) {
            throw new SeleniumError("Not found: " + target);
        }
        var match = false;
        if (frame.contentWindow) {
            if (browserVersion.isHTA) {
                target = frame.contentWindow.name;
            } else {
                this.currentWindow = frame.contentWindow;
                this.isSubFrameSelected = true;
                match = true;
            }
        } else if (frame.document && frame.location) {
            // must be an actual window frame
            this.currentWindow = frame;
            this.isSubFrameSelected = true;
            match = true;
        }

        if (!match) {
            var win = this.getCurrentWindow();

            if (win && win.frames && win.frames.length) {
                for (var i = 0; i < win.frames.length; i++) {
                    if (win.frames[i].name == target) {
                        this.currentWindow = win.frames[i];
                        this.isSubFrameSelected = true;
                        match = true;
                        break;
                    }
                }
            }
            if (!match) {
                throw new SeleniumError("Not a frame: " + target);
            }
        }
    }
    this.getCurrentWindow();
};

BrowserBot.prototype.doesThisFrameMatchFrameExpression = function(currentFrameString, target) {
    var isDom = false;
    if (target.indexOf("dom=") == 0) {
        target = target.substr(4);
        isDom = true;
    } else if (target.indexOf("index=") == 0) {
        target = "frames[" + target.substr(6) + "]";
        isDom = true;
    }
    var t;
    //Evalinsandbox
    var mySandbox = new Components.utils.Sandbox(this.currentWindow.location.href);
    mySandbox.currentFrameString = currentFrameString;
    mySandbox.target = target;
    try {
        t = Components.utils.evalInSandbox(currentFrameString + "." + target, mySandbox);
    } catch (e) {}
    var autWindow = this.browserbot.getCurrentWindow();
    if (t != null) {
        try {
            if (t.window == autWindow) {
                return true;
            }
            if (t.window.uniqueId == autWindow.uniqueId) {
                return true;
            }
            return false;
        } catch (permDenied) {
        }
    }
    if (isDom) {
        return false;
    }
    var currentFrame = Components.utils.evalInSandbox(currentFrameString, mySandbox);
    if (target == "relative=up") {
        if (currentFrame.window.parent == autWindow) {
            return true;
        }
        return false;
    }
    if (target == "relative=top") {
        if (currentFrame.window.top == autWindow) {
            return true;
        }
        return false;
    }
    if (currentFrame.window == autWindow.parent) {
        if (autWindow.name == target) {
            return true;
        }
        try {
            var element = this.findElement(target, currentFrame.window);
            if (element.contentWindow == autWindow) {
                return true;
            }
        } catch (e) {}
    }
    return false;
};

BrowserBot.prototype.abortXhrRequest = function() {
    if (this.ignoreResponseCode) {
    } else {
        if (this.abortXhr == false && this.isXhrSent && !this.isXhrDone) {
            this.abortXhr = true;
            this.xhr.abort();
        }
    }
};

BrowserBot.prototype.onXhrStateChange = function(method) {
   
    if (this.xhr.readyState == 4) {
        if (this.abortXhr == true) {
            this.xhrResponseCode = 0;
            this.xhrStatusText = "Request Aborted";
            this.isXhrDone = true;
            return;
        }

        try {
            if (method == "HEAD" && (this.xhr.status == 501 || this.xhr.status == 405)) {
                this.xhr = XmlHttp.create();
                this.xhr.onreadystatechange = this.onXhrStateChange.bind(this, "GET");
                this.xhr.open("GET", this.xhrOpenLocation, true);
                this.xhr.setRequestHeader("Range", "bytes:0-1");
                this.xhr.send("");
                this.isXhrSent = true;
                return;
            }
            this.xhrResponseCode = this.xhr.status;
            this.xhrStatusText = this.xhr.statusText;
        } catch (ex) {
            this.xhrResponseCode = -1;
            this.xhrStatusText = "Request Error";
        }

        this.isXhrDone = true;
    }
};

BrowserBot.prototype.checkedOpen = function(target) {
    var url = absolutify(target, this.baseUrl);
    this.isXhrDone = false;
    this.abortXhr = false;
    this.xhrResponseCode = null;
    this.xhrOpenLocation = url;
    try {
        this.xhr = XmlHttp.create();
    } catch (ex) {
        return;
    }
    this.xhr.onreadystatechange = this.onXhrStateChange.bind(this, "HEAD");
    this.xhr.open("HEAD", url, true);
    this.xhr.send("");
    this.isXhrSent = true;
};

BrowserBot.prototype.openLocation = function(target) {
    var win = this.getCurrentWindow();
    this.newPageLoaded = false;
    if (!this.ignoreResponseCode) {
        this.checkedOpen(target);
    }
    this.setOpenLocation(win, target);
};

BrowserBot.prototype.setIFrameLocation = function(iframe, location) {
    iframe.src = location;
};

BrowserBot.prototype.openWindow = function(url, windowID) {
    if (url != "") {
        url = "https://www.google.com";
    }
    if (browserVersion.isHTA) {
        var child = this.getCurrentWindow().open(url, windowID, 'resizable=yes');
        selenium.browserbot.openedWindows[windowID] = child;
    } else {
        this.getCurrentWindow().open(url, windowID, 'resizable=yes');
    }
};

BrowserBot.prototype.setOpenLocation = function(win, loc) {
    loc = absolutify(loc, this.baseUrl);
    if (browserVersion.isHTA) {
        var oldHref = win.location.href;
        win.location.href = loc;
        var marker = null;
        try {
            marker = this.isPollingForLoad(win);
            if (marker && win.location[marker]) {
                win.location[marker] = false;
            }
        } catch (e) {}
    } else {
        try {
            if (win.location.href === loc) {
                win.location.reload();
            } else {
                win.location.href = loc;
            }
            // END
        } catch (err) {
            //Samit: Fix: SeleniumIDE under Firefox 4 breaks if you try to open chrome URL on (XPCNativeWrapper) unwrapped window objects
            if (err.name && err.name == "NS_ERROR_FAILURE") {
                ////LOG.debug("wrapping and retrying");
                try {
                    XPCNativeWrapper(win).location.href = loc; //wrap it and try again
                } catch (e) {
                    throw err; //throw the original error, not this one
                }
            } else {
                throw err; //throw the original error, since we cannot fix it
            }
        }
    }
};

BrowserBot.prototype.getCurrentPage = function() {
    return this;
};


BrowserBot.prototype.windowNeedsModifying = function(win, uniqueId) {

    try {
        var appInfo = Components.classes['@mozilla.org/xre/app-info;1'].
        getService(Components.interfaces.nsIXULAppInfo);
        var versionChecker = Components.
        classes['@mozilla.org/xpcom/version-comparator;1'].
        getService(Components.interfaces.nsIVersionComparator);

        if (versionChecker.compare(appInfo.version, '4.0b1') >= 0) {
            return win.alert.toString().indexOf("native code") != -1;
        }
    } catch (ignored) {}
    return !win[uniqueId];
};


BrowserBot.prototype.modifyWindowToRecordPopUpDialogs = function(originalWindow, browserBot) {
    var self = this;
    var windowToModify = core.firefox.unwrap(originalWindow);
    if (!windowToModify) {
        windowToModify = originalWindow;
    }

    windowToModify.seleniumAlert = windowToModify.alert;

    if (!self.windowNeedsModifying(windowToModify, browserBot.uniqueId)) {
        return;
    }

    windowToModify.alert = function(alert) {
        browserBot.recordedAlerts.push(alert);
        self.relayBotToRC.call(self, "browserbot.recordedAlerts");
    };

    windowToModify.confirm = function(message) {
        browserBot.recordedConfirmations.push(message);
        var result = browserBot.nextConfirmResult;
        browserBot.nextConfirmResult = true;
        self.relayBotToRC.call(self, "browserbot.recordedConfirmations");
        return result;
    };

    windowToModify.prompt = function(message) {
        browserBot.recordedPrompts.push(message);
        var result = !browserBot.nextConfirmResult ? null : browserBot.nextPromptResult;
        browserBot.nextConfirmResult = true;
        browserBot.nextPromptResult = '';
        self.relayBotToRC.call(self, "browserbot.recordedPrompts");
        return result;
    };

    var originalOpen = windowToModify.open;
    var originalOpenReference;
    if (browserVersion.isHTA) {
        originalOpenReference = 'selenium_originalOpen' + new Date().getTime();
        windowToModify[originalOpenReference] = windowToModify.open;
    }

    var isHTA = browserVersion.isHTA;

    var newOpen = function(url, windowName, windowFeatures, replaceFlag) {
        var myOriginalOpen = originalOpen;
        if (isHTA) {
            myOriginalOpen = this[originalOpenReference];
        }

        if (windowName == "" || windowName == "_blank" || typeof windowName === "undefined") {
            windowName = "win_ser_" + self.count;
            self.count += 1;
        }

        var openedWindow = myOriginalOpen(url, windowName, windowFeatures, replaceFlag);
        
        if (windowName != null) {
            openedWindow["seleniumWindowName"] = windowName;
        }
        selenium.browserbot.openedWindows[windowName] = openedWindow;
        return openedWindow;
    };

    if (browserVersion.isHTA) {
        originalOpenReference = 'selenium_originalOpen' + new Date().getTime();
        newOpenReference = 'selenium_newOpen' + new Date().getTime();
        var setOriginalRef = "this['" + originalOpenReference + "'] = this.open;";

        if (windowToModify.eval) {
            windowToModify.eval(setOriginalRef);
            windowToModify.open = newOpen;
        } else {
            setOriginalRef += "this.open = this['" + newOpenReference + "'];";
            windowToModify[newOpenReference] = newOpen;
            windowToModify.setTimeout(setOriginalRef, 0);
        }
    } else {
        windowToModify.open = newOpen;
    }
};


BrowserBot.prototype.modifySeparateTestWindowToDetectPageLoads = function(windowObject) {
    if (!windowObject) {
        return;
    }
    if (this._windowClosed(windowObject)) {
        return;
    }
    var oldMarker = this.isPollingForLoad(windowObject);
    if (oldMarker) {
        return;
    }

    var marker = 'selenium' + new Date().getTime();
    this.pollingForLoad[marker] = true;

    var frameElement = this._getFrameElement(windowObject);

    var htaSubFrame = this._isHTASubFrame(windowObject);
    if (frameElement && !htaSubFrame) {
        //LOG.debug("modifySeparateTestWindowToDetectPageLoads: this window is a frame; attaching a load listener");
        addLoadListener(frameElement, this.recordPageLoad);
        frameElement[marker] = true;
        frameElement["frame" + this.uniqueId] = marker;
        //LOG.debug("dgf this.uniqueId="+this.uniqueId);
        //LOG.debug("dgf marker="+marker);
        //LOG.debug("dgf frameElement['frame'+this.uniqueId]="+frameElement['frame'+this.uniqueId]);
        frameElement[this.uniqueId] = marker;
        //LOG.debug("dgf frameElement[this.uniqueId]="+frameElement[this.uniqueId]);
    } else {
        windowObject.location[marker] = true;
        windowObject[this.uniqueId] = marker;
        this.pollForLoad(this.recordPageLoad, windowObject, windowObject.document, windowObject.location, windowObject.location.href, marker);
    }
};

BrowserBot.prototype._isHTASubFrame = function(win) {
    if (!browserVersion.isHTA) return false;
    return this.isSubFrameSelected;
};

BrowserBot.prototype._getFrameElement = function(win) {
    var frameElement = null;
    var caught;
    try {
        frameElement = win.frameElement;
    } catch (e) {
        caught = true;
    }
    if (caught) {
        var parentContainsIdenticallyNamedFrame = false;
        try {
            parentContainsIdenticallyNamedFrame = win.parent.frames[win.name];
        } catch (e) {}
        if (parentContainsIdenticallyNamedFrame) {
            var result;
            try {
                result = parentContainsIdenticallyNamedFrame.frameElement;
                if (result) {
                    return result;
                }
            } catch (e) {}
            result = this._getFrameElementByName(win.name, win.parent.document, win);
            return result;
        }
    }
    if (frameElement) {
    }
    return frameElement;
};

BrowserBot.prototype._getFrameElementByName = function(name, doc, win) {
    var frames;
    var frame;
    var i;
    frames = doc.getElementsByTagName("iframe");
    for (i = 0; i < frames.length; i++) {
        frame = frames[i];
        if (frame.name === name) {
            return frame;
        }
    }
    frames = doc.getElementsByTagName("frame");
    for (i = 0; i < frames.length; i++) {
        frame = frames[i];
        if (frame.name === name) {
            return frame;
        }
    }
   
    return BrowserBot.prototype.locateElementByName(win.name, win.parent.document);
};

BrowserBot.prototype.pollForLoad = function(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker) {
    try {
        windowObject = core.firefox.unwrap(windowObject);
        if (this._windowClosed(windowObject)) {
            delete this.pollingForLoad[marker];
            return;
        }

        var isSamePage = this._isSamePage(windowObject, originalDocument, originalLocation, originalHref, marker);
        var rs = this.getReadyState(windowObject, windowObject.document);

        if (!isSamePage && rs == 'complete') {
            var currentHref = windowObject.location.href;
            delete this.pollingForLoad[marker];
            this._modifyWindow(windowObject);
            var newMarker = this.isPollingForLoad(windowObject);
            if (!newMarker) {
                this.modifySeparateTestWindowToDetectPageLoads(windowObject);
            }
            newMarker = this.isPollingForLoad(windowObject);
            var currentlySelectedWindow;
            var currentlySelectedWindowMarker;
            currentlySelectedWindow = this.getCurrentWindow(true);
            currentlySelectedWindowMarker = currentlySelectedWindow[this.uniqueId];

            if (/(TestRunner-splash|Blank)\.html\?start=true$/.test(currentHref)) {
            } else if (currentlySelectedWindowMarker == newMarker) {
                loadFunction(currentlySelectedWindow);
            } else {
            }
            return;
        }

        this.reschedulePoller(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
    } catch (e) {
        this.pageLoadError = e;
    }
};

BrowserBot.prototype._isSamePage = function(windowObject, originalDocument, originalLocation, originalHref, marker) {
    var currentDocument = windowObject.document;
    var currentLocation = windowObject.location;
    var currentHref = currentLocation.href;

    var sameDoc = this._isSameDocument(originalDocument, currentDocument);

    var sameLoc = (originalLocation === currentLocation);

    var currentHash = currentHref.indexOf('#');
    if (currentHash > 0) {
        currentHref = currentHref.substring(0, currentHash);
    }
    var originalHash = originalHref.indexOf('#');
    if (originalHash > 0) {
        originalHref = originalHref.substring(0, originalHash);
    }

    var sameHref = (originalHref === currentHref);
    var markedLoc = currentLocation[marker];

    if (browserVersion.isKonqueror || browserVersion.isSafari) {
        markedLoc = true;
    }

    return sameDoc && sameLoc && sameHref && markedLoc;
};

BrowserBot.prototype._isSameDocument = function(originalDocument, currentDocument) {
    return originalDocument === currentDocument;
};


BrowserBot.prototype.getReadyState = function(windowObject, currentDocument) {
    var rs = currentDocument.readyState;
    if (rs == null) {
        if ((this.buttonWindow != null && this.buttonWindow.document.readyState == null)
            ||
            (top.document.readyState == null)) {
            if (typeof currentDocument.getElementsByTagName != 'undefined' && typeof currentDocument.getElementById != 'undefined' && (currentDocument.getElementsByTagName('body')[0] != null || currentDocument.body != null)) {
                if (windowObject.frameElement && windowObject.location.href == "about:blank" && windowObject.frameElement.src != "about:blank") {
                    return null;
                }
                
                for (var i = 0; i < windowObject.frames.length; i++) {
                    if (this.getReadyState(windowObject.frames[i], windowObject.frames[i].document) != 'complete') {
                        return null;
                    }
                }

                rs = 'complete';
            } else {
            }
        }
    } else if (rs == "loading" && browserVersion.isIE) {
        this.pageUnloading = true;
    }
    return rs;
};

BrowserBot.prototype.XXXreschedulePoller = function(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker) {
    var self = this;
    window.setTimeout(function() {
        self.pollForLoad(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
    }, 500);
};

BrowserBot.prototype.XXXreschedulePoller = function(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker) {
    var doc = this.buttonWindow.document;
    var button = doc.createElement("button");
    var buttonName = doc.createTextNode(marker + " - " + windowObject.name);
    button.appendChild(buttonName);
    var tools = doc.getElementById("tools");
    var self = this;
    button.onclick = function() {
        tools.removeChild(button);
        self.pollForLoad(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
    };
    tools.appendChild(button);
    window.setTimeout(button.onclick, 500);
};

BrowserBot.prototype.reschedulePoller = function(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker) {
    var self = this;
    var pollerFunction = function() {
        self.pollForLoad(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
    };
    this.windowPollers.push(pollerFunction);
};

BrowserBot.prototype.runScheduledPollers = function() {
    var oldPollers = this.windowPollers;
    this.windowPollers = new Array();
    for (var i = 0; i < oldPollers.length; i++) {
        oldPollers[i].call();
    }
};

BrowserBot.prototype.isPollingForLoad = function(win) {
    var marker;
    var frameElement = this._getFrameElement(win);
    var htaSubFrame = this._isHTASubFrame(win);
    if (frameElement && !htaSubFrame) {
        marker = frameElement["frame" + this.uniqueId];
    } else {
        marker = win[this.uniqueId];
    }
    if (!marker) {
        return false;
    }
    if (!this.pollingForLoad[marker]) {
        return false;
    }
    return marker;
};

BrowserBot.prototype.getWindowByName = function(windowName, doNotModify) {
    var targetWindow = this.openedWindows[windowName];
    if (!targetWindow) {
        targetWindow = this.topWindow[windowName];
    }
    if (!targetWindow && windowName == "_blank") {
        for (var winName in this.openedWindows) {
            if (/^selenium_blank/.test(winName)) {
                targetWindow = this.openedWindows[winName];
                var ok;
                try {
                    if (!this._windowClosed(targetWindow)) {
                        ok = targetWindow.location.href;
                    }
                } catch (e) {}
                if (ok) break;
            }
        }
    }
    if (!targetWindow) {
        throw new SeleniumError("Window does not exist. If this looks like a Selenium bug, make sure to read http://seleniumhq.org/docs/02_selenium_ide.html#alerts-popups-and-multiple-windows for potential workarounds.");
    }
    if (browserVersion.isHTA) {
        try {
            targetWindow.location.href;
        } catch (e) {
            targetWindow = window.open("", targetWindow.name);
            this.openedWindows[targetWindow.name] = targetWindow;
        }
    }
    if (!doNotModify) {
        this._modifyWindow(targetWindow);
    }
    return targetWindow;
};

BrowserBot.prototype.getWindowNameByTitle = function(windowTitle) {
    for (var windowName in this.openedWindows) {
        var targetWindow = this.openedWindows[windowName];

        try {
            if (!this._windowClosed(targetWindow) &&
                targetWindow.document.title == windowTitle) {
                return windowName;
            }
        } catch (e) {
        }
    }

    try {
        if (this.topWindow.document.title == windowTitle) {
            return "";
        }
    } catch (e) {}

    throw new SeleniumError("Could not find window with title " + windowTitle);
};

BrowserBot.prototype.getNonTopWindowNames = function() {
    var nonTopWindowNames = [];

    for (var windowName in this.openedWindows) {
        var win = this.openedWindows[windowName];
        if (!this._windowClosed(win) && win != this.topWindow) {
            nonTopWindowNames.push(windowName);
        }
    }

    return nonTopWindowNames;
};

BrowserBot.prototype.getCurrentWindow = function(doNotModify) {
    if (this.proxyInjectionMode) {
        return window;
    }
    var testWindow = core.firefox.unwrap(this.currentWindow);
    if (!doNotModify) {
        this._modifyWindow(testWindow);
        this.newPageLoaded = false;
    }
    testWindow = this._handleClosedSubFrame(testWindow, doNotModify);
    bot.window_ = testWindow;
    return core.firefox.unwrap(testWindow);
};

BrowserBot.prototype.getUserWindow = function() {
    var userWindow = this.getCurrentWindow(true);
    return userWindow;
};

BrowserBot.prototype._handleClosedSubFrame = function(testWindow, doNotModify) {
    if (this.proxyInjectionMode) {
        return testWindow;
    }

    if (this.isSubFrameSelected) {
        var missing = true;
        if (testWindow.parent && testWindow.parent.frames && testWindow.parent.frames.length) {
            for (var i = 0; i < testWindow.parent.frames.length; i++) {
                var frame = testWindow.parent.frames[i];
                if (frame == testWindow || frame.seleniumKey == testWindow.seleniumKey) {
                    missing = false;
                    break;
                }
            }
        }
        if (missing) {
            this.selectFrame("relative=top");
            return this.getCurrentWindow(doNotModify);
        }
    } else if (this._windowClosed(testWindow)) {
        testWindow = this.topWindow;
    }
    return testWindow;
};

BrowserBot.prototype.highlight = function(element, force) {
    if (force || this.shouldHighlightLocatedElement) {
        try {
            highlight(element);
        } catch (e) {}
    }
    return element;
};

BrowserBot.prototype.setShouldHighlightElement = function(shouldHighlight) {
    this.shouldHighlightLocatedElement = shouldHighlight;
};


BrowserBot.prototype._registerAllLocatorFunctions = function() {
    this.locationStrategies = {};
    for (var functionName in this) {
        var result = /^locateElementBy([A-Z].+)$/.exec(functionName);
        if (result != null) {
            var locatorFunction = this[functionName];
            if (typeof(locatorFunction) != 'function') {
                continue;
            }
            var locatorPrefix = locatorFunction.prefix || result[1].toLowerCase();
            this.locationStrategies[locatorPrefix] = locatorFunction;
        }
    }

    this.findElementBy = function(locatorType, locator, inDocument, inWindow) {
        var locatorFunction = this.locationStrategies[locatorType];
        if (!locatorFunction) {
            throw new SeleniumError("Unrecognised locator type: '" + locatorType + "'");
        }
        return locatorFunction.call(this, locator, inDocument, inWindow);
    };

    this.locationStrategies['implicit'] = function(locator, inDocument, inWindow) {
        if (locator.startsWith('//')) {
            return this.locateElementByXPath(locator, inDocument, inWindow);
        }
        if (locator.startsWith('document.')) {
            return this.locateElementByDomTraversal(locator, inDocument, inWindow);
        }
        return this.locateElementByIdentifier(locator, inDocument, inWindow);
    };

};

BrowserBot.prototype.getDocument = function() {
    return core.firefox.unwrap(this.getCurrentWindow().document);
};

BrowserBot.prototype.getTitle = function() {
    var t = this.getDocument().title;
    if (typeof(t) == "string") {
        t = t.trim();
    }
    return t;
};

BrowserBot.prototype.getCookieByName = function(cookieName, doc) {
    if (!doc) doc = this.getDocument();
    var ck = doc.cookie;
    if (!ck) return null;
    var ckPairs = ck.split(/;/);
    for (var i = 0; i < ckPairs.length; i++) {
        var ckPair = ckPairs[i].trim();
        var ckNameValue = ckPair.split(/=/);
        var ckName = decodeURIComponent(ckNameValue[0]);
        if (ckName === cookieName) {
            return decodeURIComponent(ckNameValue.slice(1).join("="));
        }
    }
    return null;
};

BrowserBot.prototype.getAllCookieNames = function(doc) {
    if (!doc) doc = this.getDocument();
    var ck = doc.cookie;
    if (!ck) return [];
    var cookieNames = [];
    var ckPairs = ck.split(/;/);
    for (var i = 0; i < ckPairs.length; i++) {
        var ckPair = ckPairs[i].trim();
        var ckNameValue = ckPair.split(/=/);
        var ckName = decodeURIComponent(ckNameValue[0]);
        cookieNames.push(ckName);
    }
    return cookieNames;
};

BrowserBot.prototype.getAllRawCookieNames = function(doc) {
    if (!doc) doc = this.getDocument();
    var ck = doc.cookie;
    if (!ck) return [];
    var cookieNames = [];
    var ckPairs = ck.split(/;/);
    for (var i = 0; i < ckPairs.length; i++) {
        var ckPair = ckPairs[i].trim();
        var ckNameValue = ckPair.split(/=/);
        var ckName = ckNameValue[0];
        cookieNames.push(ckName);
    }
    return cookieNames;
};

function encodeURIComponentWithASPHack(uri) {
    var regularEncoding = encodeURIComponent(uri);
    var aggressiveEncoding = regularEncoding.replace(".", "%2E");
    aggressiveEncoding = aggressiveEncoding.replace("_", "%5F");
    return aggressiveEncoding;
}

BrowserBot.prototype.deleteCookie = function(cookieName, domain, path, doc) {
    if (!doc) doc = this.getDocument();
    var expireDateInMilliseconds = (new Date()).getTime() + (-1 * 1000);
    var _cookieName;
    var rawCookieNames = this.getAllRawCookieNames(doc);
    for (rawCookieNumber in rawCookieNames) {
        if (rawCookieNames[rawCookieNumber] == cookieName) {
            _cookieName = cookieName;
            break;
        } else if (rawCookieNames[rawCookieNumber] == encodeURIComponent(cookieName)) {
            _cookieName = encodeURIComponent(cookieName);
            break;
        } else if (rawCookieNames[rawCookieNumber] == encodeURIComponentWithASPHack(cookieName)) {
            _cookieName = encodeURIComponentWithASPHack(cookieName);
            break;
        }
    }

    var cookie = _cookieName + "=deleted; ";
    if (path) {
        cookie += "path=" + path + "; ";
    }
    if (domain) {
        cookie += "domain=" + domain + "; ";
    }
    cookie += "expires=" + new Date(expireDateInMilliseconds).toGMTString();
    doc.cookie = cookie;
};


BrowserBot.prototype._maybeDeleteCookie = function(cookieName, domain, path, doc) {
    this.deleteCookie(cookieName, domain, path, doc);
    return (!this.getCookieByName(cookieName, doc));
};


BrowserBot.prototype._recursivelyDeleteCookieDomains = function(cookieName, domain, path, doc) {
    var deleted = this._maybeDeleteCookie(cookieName, domain, path, doc);
    if (deleted) return true;
    var dotIndex = domain.indexOf(".");
    if (dotIndex == 0) {
        return this._recursivelyDeleteCookieDomains(cookieName, domain.substring(1), path, doc);
    } else if (dotIndex != -1) {
        return this._recursivelyDeleteCookieDomains(cookieName, domain.substring(dotIndex), path, doc);
    } else {
        return this._maybeDeleteCookie(cookieName, null, path, doc);
    }
};

BrowserBot.prototype._recursivelyDeleteCookie = function(cookieName, domain, path, doc) {
    var slashIndex = path.lastIndexOf("/");
    var finalIndex = path.length - 1;
    if (slashIndex == finalIndex) {
        slashIndex--;
    }
    if (slashIndex != -1) {
        deleted = this._recursivelyDeleteCookie(cookieName, domain, path.substring(0, slashIndex + 1), doc);
        if (deleted) return true;
    }
    return this._recursivelyDeleteCookieDomains(cookieName, domain, path, doc);
};

BrowserBot.prototype.recursivelyDeleteCookie = function(cookieName, domain, path, win) {
    if (!win) win = this.getCurrentWindow();
    var doc = win.document;
    if (!domain) {
        domain = doc.domain;
    }
    if (!path) {
        path = win.location.pathname;
    }
    var deleted = this._recursivelyDeleteCookie(cookieName, "." + domain, path, doc);
    if (deleted) return;
    deleted = this._recursivelyDeleteCookieDomains(cookieName, "." + domain, null, doc);
    if (deleted) return;
    throw new SeleniumError("Couldn't delete cookie " + cookieName);
};

BrowserBot.prototype.findElementRecursive = function(locatorType, locatorString, inDocument, inWindow) {
    var element = this.findElementBy(locatorType, locatorString, inDocument, inWindow);
    if (element != null) {
        return element;
    }

    for (var i = 0; i < inWindow.frames.length; i++) {
        try {
            if (inWindow.frames[i].document) {
                element = this.findElementRecursive(locatorType, locatorString, inWindow.frames[i].document, inWindow.frames[i]);
                if (element != null) {
                    return element;
                }
            }
        } catch (e) {
            return null;
        }
    }
};

BrowserBot.prototype.findElementOrNull = function(locator, win) {
    locator = parse_locator(locator);

    if (win == null) {
        win = this.getCurrentWindow();
    }

    var element = this.findElementBy(locator.type, locator.string, win.document, win);
    element = core.firefox.unwrap(element);

    if (element != null) {
        return this.browserbot.highlight(element);
    }

    return null;
};

BrowserBot.prototype.findElement = function(locator, win) {
    var element = this.findElementOrNull(locator, win);
    if (element == null) {
        if (locator.includes("d-XPath")) {
            throw new SeleniumError("Element located by TAC not found");
        } else if (locator == "auto-located-by-tac") {
            throw new SeleniumError("The value \"auto-located-by-tac\" only can be automatically generated when recording a command");
        } else throw new SeleniumError("Element " + locator + " not found");
    }
    return core.firefox.unwrap(element);
};


BrowserBot.prototype.findElementsLikeWebDriver = function(how, using, root) {
    var by = {};
    by[how] = using;

    var all = bot.locators.findElements(by, root);
    var toReturn = '';

    for (var i = 0; i < all.length - 1; i++) {
        toReturn += bot.inject.cache.addElement(core.firefox.unwrap(all[i])) + ',';
    }
    if (all[all.length - 1]) {
        var last = core.firefox.unwrap(all[all.length - 1]);
        toReturn += bot.inject.cache.addElement(core.firefox.unwrap(all[all.length - 1]));
    }

    return toReturn;
};

BrowserBot.prototype.locateElementByIdentifier = function(identifier, inDocument, inWindow) {
    return this.locateElementById(identifier, inDocument, inWindow) || BrowserBot.prototype.locateElementByName(identifier, inDocument, inWindow) || null;
};

BrowserBot.prototype.locateElementById = function(identifier, inDocument, inWindow) {
    var element = inDocument.getElementById(identifier);
    if (element && element.getAttribute('id') === identifier) {
        return element;
    } else if (browserVersion.isIE || browserVersion.isOpera) {
        var elements = inDocument.getElementsByTagName('*');

        for (var i = 0, n = elements.length; i < n; ++i) {
            element = elements[i];

            if (element.tagName.toLowerCase() == 'form') {
                if (element.attributes['id'].nodeValue == identifier) {
                    return element;
                }
            } else if (element.getAttribute('id') == identifier) {
                return element;
            }
        }

        return null;
    } else {
        return null;
    }
};


BrowserBot.prototype.locateElementByDomTraversal = function(domTraversal, document, window) {

    var browserbot = this.browserbot;
    var element = null;

    var mySandbox = new Components.utils.Sandbox(this.currentWindow.location.href);
    mySandbox.domTraversal = domTraversal;
    try {
        element = Components.utils.evalInSandbox(domTraversal, mySandbox);
    } catch (e) {
        return null;
    }

    if (!element) {
        return null;
    }

    return element;
};

BrowserBot.prototype.locateElementByName = function(locator, document, inWindow) {
    var elements = document.getElementsByTagName("*");
    var filter = 'name=' + locator;
    elements = this.selectElements(filter, elements, 'value');

    if (elements.length > 0) {
        return elements[0];
    }
    return null;
};


BrowserBot.prototype.locateElementByDomTraversal.prefix = "dom";


BrowserBot.prototype.locateElementByStoredReference = function(locator, document, window) {
    try {
        return core.locators.findElement("stored=" + locator);
    } catch (e) {
        return null;
    }
};
BrowserBot.prototype.locateElementByStoredReference.prefix = "stored";


BrowserBot.prototype.locateElementByWebDriver = function(locator, document, window) {
    try {
        return core.locators.findElement("webdriver=" + locator);
    } catch (e) {
        return null;
    }
};
BrowserBot.prototype.locateElementByWebDriver.prefix = "webdriver";

BrowserBot.prototype.locateElementByXPath = function(xpath, inDocument, inWindow) {
    return this.xpathEvaluator.selectSingleNode(inDocument, xpath, null,
        inDocument.createNSResolver ? inDocument.createNSResolver(inDocument.documentElement) : this._namespaceResolver);
};

BrowserBot.prototype.locateElementsByXPath = function(xpath, inDocument, inWindow) {
    return this.xpathEvaluator.selectNodes(inDocument, xpath, null,
        inDocument.createNSResolver ? inDocument.createNSResolver(inDocument.documentElement) : this._namespaceResolver);
};


BrowserBot.prototype._namespaceResolver = function(prefix) {
    if (prefix == 'html' || prefix == 'xhtml' || prefix == 'x') {
        return 'http://www.w3.org/1999/xhtml';
    } else if (prefix == 'mathml') {
        return 'http://www.w3.org/1998/Math/MathML';
    } else if (prefix == 'svg') {
        return 'http://www.w3.org/2000/svg';
    } else {
        throw new Error("Unknown namespace: " + prefix + ".");
    }
};


BrowserBot.prototype.evaluateXPathCount = function(selector, inDocument) {
    var locator = parse_locator(selector);
    var opts = {};
    opts['namespaceResolver'] =
        inDocument.createNSResolver ? inDocument.createNSResolver(inDocument.documentElement) : this._namespaceResolver;
    if (locator.type == 'xpath' || locator.type == 'implicit') {
        return eval_xpath(locator.string, inDocument, opts).length;
    } else {
        return 0;
    }
};


BrowserBot.prototype.evaluateCssCount = function(selector, inDocument) {
    var locator = parse_locator(selector);
    if (locator.type == 'css' || locator.type == 'implicit') {
        return eval_css(locator.string, inDocument).length;
    } else {
        return 0;
    }
};

BrowserBot.prototype.locateElementByLinkText = function(linkText, inDocument, inWindow) {
    var links = inDocument.getElementsByTagName('a');
    for (var i = 0; i < links.length; i++) {
        var element = links[i];
        if (PatternMatcher.matches(linkText, getText(element))) {
            return element;
        }
    }
    return null;
};

BrowserBot.prototype.locateElementByLinkText.prefix = "link";

BrowserBot.prototype.findAttribute = function(locator) {
    var attributePos = locator.lastIndexOf("@");
    var elementLocator = locator.slice(0, attributePos);
    var attributeName = locator.slice(attributePos + 1);

    // Find the element.
    var element = this.findElement(elementLocator);
    var attributeValue = bot.dom.getAttribute(element, attributeName);
    return goog.isDefAndNotNull(attributeValue) ? attributeValue.toString() : null;
};

BrowserBot.prototype.selectOption = function(element, optionToSelect) {
    bot.events.fire(element, bot.events.EventType.FOCUS);
    var changed = false;
    for (var i = 0; i < element.options.length; i++) {
        var option = element.options[i];
        if (option.selected && option != optionToSelect) {
            option.selected = false;
            changed = true;
        } else if (!option.selected && option == optionToSelect) {
            option.selected = true;
            changed = true;
        }
    }

    if (changed) {
        bot.events.fire(element, bot.events.EventType.CHANGE);
    }
};

BrowserBot.prototype.addSelection = function(element, option) {
    this.checkMultiselect(element);
    bot.events.fire(element, bot.events.EventType.FOCUS);
    if (!option.selected) {
        option.selected = true;
        bot.events.fire(element, bot.events.EventType.CHANGE);
    }
};

BrowserBot.prototype.removeSelection = function(element, option) {
    this.checkMultiselect(element);
    bot.events.fire(element, bot.events.EventType.FOCUS);
    if (option.selected) {
        option.selected = false;
        bot.events.fire(element, bot.events.EventType.CHANGE);
    }
};

BrowserBot.prototype.checkMultiselect = function(element) {
    if (!element.multiple) {
        throw new SeleniumError("Not a multi-select");
    }

};

BrowserBot.prototype.replaceText = function(element, stringValue) {
    bot.events.fire(element, bot.events.EventType.FOCUS);
    bot.events.fire(element, bot.events.EventType.SELECT);
    var maxLengthAttr = element.getAttribute("maxLength");
    var actualValue = stringValue;
    if (maxLengthAttr != null) {
        var maxLength = parseInt(maxLengthAttr);
        if (stringValue.length > maxLength) {
            actualValue = stringValue.substr(0, maxLength);
        }
    }

    if (getTagName(element) == "body") {
        if (element.ownerDocument && element.ownerDocument.designMode) {
            var designMode = new String(element.ownerDocument.designMode).toLowerCase();
            if (designMode == "on") {
                element.innerHTML = actualValue;
            }
        }
    } else {
        element.value = actualValue;
    }
    try {
        bot.events.fire(element, bot.events.EventType.CHANGE);
    } catch (e) {}
};

BrowserBot.prototype.submit = function(formElement) {
    var actuallySubmit = true;
    this._modifyElementTarget(formElement);

    if (formElement.onsubmit) {
        if (browserVersion.isHTA) {
            // run the code in the correct window so alerts are handled correctly even in HTA mode
            var win = this.browserbot.getCurrentWindow();
            var now = new Date().getTime();
            var marker = 'marker' + now;
            win[marker] = formElement;
            win.setTimeout("var actuallySubmit = " + marker + ".onsubmit();" +
                "if (actuallySubmit) { " +
                marker + ".submit(); " +
                "if (" + marker + ".target && !/^_/.test(" + marker + ".target)) {" +
                "window.open('', " + marker + ".target);" +
                "}" +
                "};" +
                marker + "=null", 0);
            var terminationCondition = function() {
                return !win[marker];
            };
            return Selenium.decorateFunctionWithTimeout(terminationCondition, 2000);
        } else {
            actuallySubmit = formElement.onsubmit();
            if (actuallySubmit) {
                formElement.submit();
                if (formElement.target && !/^_/.test(formElement.target)) {
                    this.browserbot.openWindow('', formElement.target);
                }
            }
        }
    } else {
        formElement.submit();
    }
};

BrowserBot.prototype.clickElement = function(element, clientX, clientY) {
    this._fireEventOnElement("click", element, clientX, clientY);
};

BrowserBot.prototype.doubleClickElement = function(element, clientX, clientY) {
    this._fireEventOnElement("dblclick", element, clientX, clientY);
};

BrowserBot.prototype.contextMenuOnElement = function(element, clientX, clientY) {
    this._fireEventOnElement("contextmenu", element, clientX, clientY);
};

BrowserBot.prototype._modifyElementTarget = function(e) {
    var element = this.findClickableElement(e) || e;
    if (element.target) {
        if (element.target == "_blank" || /^selenium_blank/.test(element.target)) {
            var tagName = getTagName(element);
            if (tagName == "a" || tagName == "form") {
                var newTarget = "win_ser_" + this.count;
                this.count += 1;
                this.browserbot.openWindow('', newTarget);
                element.target = newTarget;
            }
        } else {
            var newTarget = element.target;
            this.browserbot.openWindow('', newTarget);
            element.target = newTarget;
        }
    }
};

BrowserBot.prototype.findClickableElement = function(e) {
    if (!e.tagName) return null;
    var tagName = e.tagName.toLowerCase();
    var type = e.type;
    if (e.hasAttribute("onclick") || e.hasAttribute("href") || e.hasAttribute("url") || tagName == "button" ||
        (tagName == "input" &&
            (type == "submit" || type == "button" || type == "image" || type == "radio" || type == "checkbox" || type == "reset"))) {
        return e;
    } else {
        if (e.parentNode != null) {
            return this.findClickableElement(e.parentNode);
        } else {
            return null;
        }
    }
};


BrowserBot.prototype._handleClickingImagesInsideLinks = function(targetWindow, element) {
    var itrElement = element;
    while (itrElement != null) {
        if (itrElement.href) {
            targetWindow.location.href = itrElement.href;
            break;
        }
        itrElement = itrElement.parentNode;
    }
};

BrowserBot.prototype._getTargetWindow = function(element) {
    var targetWindow = element.ownerDocument.defaultView;
    if (element.target) {
        targetWindow = this._getFrameFromGlobal(element.target);
    }
    return targetWindow;
};

BrowserBot.prototype._getFrameFromGlobal = function(target) {

    if (target == "_self") {
        return this.getCurrentWindow();
    }
    if (target == "_top") {
        return this.topFrame;
    } else if (target == "_parent") {
        return this.getCurrentWindow().parent;
    } else if (target == "_blank") {
        return this.getCurrentWindow().open('', '_blank');
    }
    var frameElement = this.findElementBy("implicit", target, this.topFrame.document, this.topFrame);
    if (frameElement) {
        return frameElement.contentWindow;
    }
    var win = this.getWindowByName(target);
    if (win) return win;
    return this.getCurrentWindow().open('', target);
};


BrowserBot.prototype.bodyText = function() {
    if (!this.getDocument().body) {
        throw new SeleniumError("Couldn't access document.body.  Is this HTML page fully loaded?");
    }
    return getText(this.getDocument().body);
};

BrowserBot.prototype.getAllButtons = function() {
    var elements = this.getDocument().getElementsByTagName('input');
    var result = [];

    for (var i = 0; i < elements.length; i++) {
        if (elements[i].type == 'button' || elements[i].type == 'submit' || elements[i].type == 'reset') {
            result.push(elements[i].id);
        }
    }

    return result;
};


BrowserBot.prototype.getAllFields = function() {
    var elements = this.getDocument().getElementsByTagName('input');
    var result = [];

    for (var i = 0; i < elements.length; i++) {
        if (elements[i].type == 'text') {
            result.push(elements[i].id);
        }
    }

    return result;
};

BrowserBot.prototype.getAllLinks = function() {
    var elements = this.getDocument().getElementsByTagName('a');
    var result = [];

    for (var i = 0; i < elements.length; i++) {
        result.push(elements[i].id);
    }

    return result;
};

function isDefined(value) {
    return typeof(value) != undefined;
};

BrowserBot.prototype.goBack = function() {
    this.getCurrentWindow().history.back();
};

BrowserBot.prototype.goForward = function() {
    this.getCurrentWindow().history.forward();
};

BrowserBot.prototype.close = function() {
    if (browserVersion.isIE) {
        try {
            this.topFrame.name = new Date().getTime();
            window.open("", this.topFrame.name, "");
            this.topFrame.close();
            return;
        } catch (e) {}
    }
    if (browserVersion.isChrome || browserVersion.isSafari || browserVersion.isOpera) {
        this.topFrame.close();
    } else {
        this.getCurrentWindow().eval("window.top.close();");
    }
};

BrowserBot.prototype.refresh = function() {
    this.getCurrentWindow().location.reload(true);
};

BrowserBot.prototype.selectElementsBy = function(filterType, filter, elements) {
    var filterFunction = BrowserBot.filterFunctions[filterType];
    if (!filterFunction) {
        throw new SeleniumError("Unrecognised element-filter type: '" + filterType + "'");
    }

    return filterFunction(filter, elements);
};

BrowserBot.filterFunctions = {};

BrowserBot.filterFunctions.name = function(name, elements) {
    var selectedElements = [];
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].name === name) {
            selectedElements.push(elements[i]);
        }
    }
    return selectedElements;
};

BrowserBot.filterFunctions.value = function(value, elements) {
    var selectedElements = [];
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].value === value) {
            selectedElements.push(elements[i]);
        }
    }
    return selectedElements;
};

BrowserBot.filterFunctions.index = function(index, elements) {
    index = Number(index);
    if (isNaN(index) || index < 0) {
        throw new SeleniumError("Illegal Index: " + index);
    }
    if (elements.length <= index) {
        throw new SeleniumError("Index out of range: " + index);
    }
    return [elements[index]];
};

BrowserBot.prototype.selectElements = function(filterExpr, elements, defaultFilterType) {

    var filterType = (defaultFilterType || 'value');

    var result = filterExpr.match(/^([A-Za-z]+)=(.+)/);
    if (result) {
        filterType = result[1].toLowerCase();
        filterExpr = result[2];
    }

    return this.selectElementsBy(filterType, filterExpr, elements);
};

BrowserBot.prototype.locateElementByClass = function(locator, document) {
    return elementFindFirstMatchingChild(document,
        function(element) {
            return element.className == locator;
        }
    );
};

BrowserBot.prototype.locateElementByAlt = function(locator, document) {
    return elementFindFirstMatchingChild(document,
        function(element) {
            return element.alt == locator;
        }
    );
};

BrowserBot.prototype.locateElementByCss = function(locator, document) {
    var elements = eval_css(locator, document);
    if (elements.length != 0)
        return elements[0];
    return null;
};

BrowserBot.prototype.locateElementByUIElement = function(locator, inDocument) {
    var locators = locator.split(/->/, 2);

    var locatedElement = null;
    var pageElements = UIMap.getInstance()
        .getPageElements(locators[0], inDocument);

    if (locators.length > 1) {
        for (var i = 0; i < pageElements.length; ++i) {
            var locatedElements = eval_locator(locators[1], inDocument,
                pageElements[i]);
            if (locatedElements.length) {
                locatedElement = locatedElements[0];
                break;
            }
        }
    } else if (pageElements.length) {
        locatedElement = pageElements[0];
    }

    return locatedElement;
};

BrowserBot.prototype.locateElementByUIElement.prefix = 'ui';

BrowserBot.prototype.locateElementByUIElement.is_fuzzy_match = function(node, target) {
    try {
        var isMatch = (
            (node == target) ||
            ((node.nodeName == 'A' || node.onclick) && is_ancestor(node, target))
        );
        return isMatch;
    } catch (e) {
        return false;
    }
};

BrowserBot.prototype.cancelNextPrompt = function() {
    return this.setNextPromptResult(null);
};

BrowserBot.prototype.setNextPromptResult = function(result) {
    this.promptResponse = false;
    let self = this;

    window.postMessage({
        direction: "from-content-script",
        command: "setNextPromptResult",
        target: result
    }, "*");

    let response = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!self.promptResponse) {
                count++;
                if (count > 60) {
                    reject("No response");
                    clearInterval(interval);
                }
            } else {
                resolve();
                self.promptResponse = false;
                clearInterval(interval);
            }
        }, 500);
    })
    return response;
}

BrowserBot.prototype.getPromptMessage = function() {
    this.promptResponse = false;
    this.promptMessage = null;
    let self = this;
    window.postMessage({
        direction: "from-content-script",
        command: "getPromptMessage",
    }, "*");
    let response = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!self.promptResponse) {
                count++;
                if (count > 60) {
                    reject("No response");
                    clearInterval(interval);
                }
            } else {
                resolve(self.promptMessage);
                self.promptResponse = false;
                self.promptMessage = null;
                clearInterval(interval);
            }
        }, 500);
    })
    return response;
}


BrowserBot.prototype.setNextConfirmationResult = function(result) {
    this.confirmationResponse = false;
    let self = this;
    window.postMessage({
        direction: "from-content-script",
        command: "setNextConfirmationResult",
        target: result
    }, "*");
    let response = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!self.confirmationResponse) {
                count++;
                if (count > 60) {
                    reject("No response");
                    clearInterval(interval);
                }
            } else {
                resolve();
                self.confirmationResponse = false;
                clearInterval(interval);
            }
        }, 500);
    })
    return response;
}

BrowserBot.prototype.getConfirmationMessage = function() {
    this.confirmationResponse = false;
    this.confirmationMessage = null;
    let self = this;
    window.postMessage({
        direction: "from-content-script",
        command: "getConfirmationMessage",
    }, "*");
    let response = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!self.confirmationResponse) {
                count++;
                if (count > 60) {
                    reject("No response");
                    clearInterval(interval);
                }
            } else {
                resolve(self.confirmationMessage);
                self.confirmationResponse = false;
                self.confirmationMessage = null;
                clearInterval(interval);
            }
        }, 500);
    })
    return response;
}

BrowserBot.prototype.getAlertMessage = function() {
    let self = this;
    let response = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!self.alertResponse) {
                count++;
                if (count > 60) {
                    reject("No response!!!!");
                    clearInterval(interval);
                }
            } else {
                resolve(self.alertMessage);
                self.alertResponse = false;
                self.alertMessage = null;
                clearInterval(interval);
            }
        }, 500);
    })
    return response;
}

BrowserBot.prototype.getRunScriptMessage = function() {
    let self = this;
    let response = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!self.runScriptResponse) {
                count++;
                if (count > 4) {
                    resolve("No error!!!!");
                    clearInterval(interval);
                }
            } else {
                resolve(self.runScriptMessage);
                self.runScriptResponse = false;
                self.runScriptMessage = null;
                clearInterval(interval);
            }
        }, 200);
    })
    return response;
}


function MozillaBrowserBot(frame) {
    BrowserBot.call(this, frame);
}
objectExtend(MozillaBrowserBot.prototype, BrowserBot.prototype);

function KonquerorBrowserBot(frame) {
    BrowserBot.call(this, frame);
}
objectExtend(KonquerorBrowserBot.prototype, BrowserBot.prototype);

KonquerorBrowserBot.prototype.setIFrameLocation = function(iframe, location) {
    iframe.src = "about:blank";
    iframe.src = location;
};

KonquerorBrowserBot.prototype.setOpenLocation = function(win, loc) {
    loc = absolutify(loc, this.baseUrl);
    loc = canonicalize(loc);
    var startUrl = win.location.href;
    if ("about:blank" != win.location.href) {
        var startLoc = parseUrl(win.location.href);
        startLoc.hash = null;
        startUrl = reassembleLocation(startLoc);
    }

    if (startUrl == loc) {
        this.refresh();
    } else {
        win.location.href = loc;
    }

    var marker = this.isPollingForLoad(win);
    if (marker) {
        delete win.location[marker];
    }
};

KonquerorBrowserBot.prototype._isSameDocument = function(originalDocument, currentDocument) {
    if (originalDocument) {
        return originalDocument.location == currentDocument.location;
    } else {
        return originalDocument === currentDocument;
    }
};

function SafariBrowserBot(frame) {
    BrowserBot.call(this, frame);
}
objectExtend(SafariBrowserBot.prototype, BrowserBot.prototype);

SafariBrowserBot.prototype.setIFrameLocation = KonquerorBrowserBot.prototype.setIFrameLocation;
SafariBrowserBot.prototype.setOpenLocation = KonquerorBrowserBot.prototype.setOpenLocation;


function OperaBrowserBot(frame) {
    BrowserBot.call(this, frame);
};
objectExtend(OperaBrowserBot.prototype, BrowserBot.prototype);
OperaBrowserBot.prototype.setIFrameLocation = function(iframe, location) {
    if (iframe.src == location) {
        iframe.src = location + '?reload';
    } else {
        iframe.src = location;
    }
};

function IEBrowserBot(frame) {
    BrowserBot.call(this, frame);
};
objectExtend(IEBrowserBot.prototype, BrowserBot.prototype);

IEBrowserBot.prototype._handleClosedSubFrame = function(testWindow, doNotModify) {
    if (this.proxyInjectionMode) {
        return testWindow;
    }

    try {
        testWindow.location.href;
        this.permDenied = 0;
    } catch (e) {
        this.permDenied++;
    }
    if (this._windowClosed(testWindow) || this.permDenied > 4) {
        if (this.isSubFrameSelected) {
            this.selectFrame("relative=top");
            return this.getCurrentWindow(doNotModify);
        } else {
            var closedError = new SeleniumError("Current window or frame is closed!");
            closedError.windowClosed = true;
            throw closedError;
        }
    }
    return testWindow;
};

IEBrowserBot.prototype.modifyWindowToRecordPopUpDialogs = function(windowToModify, browserBot) {
    BrowserBot.prototype.modifyWindowToRecordPopUpDialogs(windowToModify, browserBot);

    oldShowModalDialog = windowToModify.showModalDialog;

    windowToModify.showModalDialog = function(url, args, features) {
        var doc_location = document.location.toString();
        var end_of_base_ref = doc_location.indexOf('TestRunner.html');
        var base_ref = doc_location.substring(0, end_of_base_ref);
        var runInterval = '';

        if (typeof(window.runOptions) != 'undefined') {
            runInterval = "&runInterval=" + runOptions.runInterval;
        }

        var testRunnerURL = "TestRunner.html?auto=true&singletest=" + escape(browserBot.modalDialogTest) + "&autoURL=" + escape(url) + runInterval;
        var fullURL = base_ref + testRunnerURL;
        browserBot.modalDialogTest = null;

        if (this.proxyInjectionMode) {
            var sessionId = runOptions.getSessionId();
            if (sessionId == undefined) {
                sessionId = injectedSessionId;
            }
            if (sessionId != undefined) {
            }
            fullURL = url;
        }
        var returnValue = oldShowModalDialog(fullURL, args, features);
        return returnValue;
    };
};

IEBrowserBot.prototype.modifySeparateTestWindowToDetectPageLoads = function(windowObject) {
    this.pageUnloading = false;
    var self = this;
    var pageUnloadDetector = function() {
        self.pageUnloading = true;
    };
    if (windowObject.addEventListener) {
        windowObject.addEventListener('beforeunload', pageUnloadDetector, true);
    } else {
        windowObject.attachEvent('onbeforeunload', pageUnloadDetector);
    }
    BrowserBot.prototype.modifySeparateTestWindowToDetectPageLoads.call(this, windowObject);
};

IEBrowserBot.prototype.pollForLoad = function(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker) {

    if (!this.permDeniedCount[marker]) this.permDeniedCount[marker] = 0;
    BrowserBot.prototype.pollForLoad.call(this, loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
    var self;
    if (this.pageLoadError) {
        if (this.pageUnloading) {
            self = this;
            
            this.reschedulePoller(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
            this.pageLoadError = null;
            return;
        } else if (((this.pageLoadError.message == "Permission denied") || (/^Access is denied/.test(this.pageLoadError.message))) && this.permDeniedCount[marker]++ < 8) {
            if (this.permDeniedCount[marker] > 4) {
                var canAccessThisWindow;
                var canAccessCurrentlySelectedWindow;
                try {
                    windowObject.location.href;
                    canAccessThisWindow = true;
                } catch (e) {}
                try {
                    this.getCurrentWindow(true).location.href;
                    canAccessCurrentlySelectedWindow = true;
                } catch (e) {}
                if (canAccessCurrentlySelectedWindow & !canAccessThisWindow) {
                    this.pageLoadError = null;
                    return;
                }
            }

            self = this;
            
            this.reschedulePoller(loadFunction, windowObject, originalDocument, originalLocation, originalHref, marker);
            this.pageLoadError = null;
            return;
        }

    }
};

IEBrowserBot.prototype._windowClosed = function(win) {
    try {
        var c = win.closed;
        if (!c) {
            try {
                win.document;
            } catch (de) {
                if (de.message == "Permission denied") {
                    return false;
                } else if (/^Access is denied/.test(de.message)) {
                    return false;
                } else {
                    return true;
                }
            }
        }
        if (c == null) {
            return true;
        }
        return c;
    } catch (e) {
       

        if (browserVersion.isHTA) {
            if (e.message == "Permission denied") {
                return false;
            } else {
                return true;
            }
        } else {
            return false;
        }
    }
};

IEBrowserBot.prototype.locateElementByIdentifer = function(identifier, inDocument, inWindow) {
    return inDocument.getElementById(identifier);
};

SafariBrowserBot.prototype.modifyWindowToRecordPopUpDialogs = function(windowToModify, browserBot) {
    BrowserBot.prototype.modifyWindowToRecordPopUpDialogs(windowToModify, browserBot);

    var originalOpen = windowToModify.open;
 
    windowToModify.open = function(url, windowName, windowFeatures, replaceFlag) {

        if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("/")) {
            return originalOpen(url, windowName, windowFeatures, replaceFlag);
        }

        var currentPath = windowToModify.location.pathname || "/";
        currentPath = currentPath.replace(/\/[^\/]*$/, "/");

        url = url.replace(/^\.\//, "");

        newUrl = currentPath + url;

        var openedWindow = originalOpen(newUrl, windowName, windowFeatures, replaceFlag);
        
        if (windowName != null) {
            openedWindow["seleniumWindowName"] = windowName;
        }
        return openedWindow;
    };
};

MozillaBrowserBot.prototype._fireEventOnElement = function(eventType, element, clientX, clientY) {
    var win = this.getCurrentWindow();
    bot.events.fire(element, bot.events.EventType.FOCUS);
    var savedEvent = null;

    element.addEventListener(eventType, function(evt) {
        savedEvent = evt;
    }, false);

    this.browserbot.triggerMouseEvent(element, eventType, true, clientX, clientY);

    if (this._windowClosed(win)) {
        return;
    }
};


OperaBrowserBot.prototype._fireEventOnElement = function(eventType, element, clientX, clientY) {
    var win = this.getCurrentWindow();
    bot.events.fire(element, bot.events.EventType.FOCUS);

    this._modifyElementTarget(element);

    this.browserbot.triggerMouseEvent(element, eventType, true, clientX, clientY);

    if (this._windowClosed(win)) {
        return;
    }

};


KonquerorBrowserBot.prototype._fireEventOnElement = function(eventType, element, clientX, clientY) {
    var win = this.getCurrentWindow();
    bot.events.fire(element, bot.events.EventType.FOCUS);

    this._modifyElementTarget(element);

    if (element[eventType]) {
        element[eventType]();
    } else {
        this.browserbot.triggerMouseEvent(element, eventType, true, clientX, clientY);
    }

    if (this._windowClosed(win)) {
        return;
    }

};

SafariBrowserBot.prototype._fireEventOnElement = function(eventType, element, clientX, clientY) {
    bot.events.fire(element, bot.events.EventType.FOCUS);
    var wasChecked = element.checked;

    this._modifyElementTarget(element);

    if (element[eventType]) {
        element[eventType]();
    }

    else {
        var targetWindow = this.browserbot._getTargetWindow(element);
        this.browserbot.triggerMouseEvent(element, eventType, true, clientX, clientY);

    }

};

SafariBrowserBot.prototype.refresh = function() {
    var win = this.getCurrentWindow();
    if (win.location.hash) {
        win.location.hash = "";
        var actuallyReload = function() {
            win.location.reload(true);
        };
        window.setTimeout(actuallyReload, 1);
    } else {
        win.location.reload(true);
    }
};

IEBrowserBot.prototype._fireEventOnElement = function(eventType, element, clientX, clientY) {
    var win = this.getCurrentWindow();
    bot.events.fire(element, bot.events.EventType.FOCUS);

    var wasChecked = element.checked;

    var pageUnloading = false;
    var pageUnloadDetector = function() {
        pageUnloading = true;
    };
    if (win.addEventListener) {
        win.addEventListener('beforeunload', pageUnloadDetector, true);
    } else {
        win.attachEvent('onbeforeunload', pageUnloadDetector);
    }
    this._modifyElementTarget(element);
    if (element[eventType]) {
        element[eventType]();
    } else {
        this.browserbot.triggerMouseEvent(element, eventType, true, clientX, clientY);
    }


    
    try {
        if (win.removeEventListener) {
            win.removeEventListener('onbeforeunload', pageUnloadDetector, true);
        } else {
            win.detachEvent('onbeforeunload', pageUnloadDetector);
        }

        if (this._windowClosed(win)) {
            return;
        }

        if (isDefined(element.checked) && wasChecked != element.checked) {
            bot.events.fire(element, bot.events.EventType.CHANGE);
        }

    } catch (e) {
        if (pageUnloading) {
            return;
        }
        throw e;
    }
};
