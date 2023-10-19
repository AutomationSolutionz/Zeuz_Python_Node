/* zeuz selenium start */
var storedVars = new Object();
var unicodeToKeys = {};
var keyboardEventKeys = {};
function getClientXY(element, coordString) {
    var coords = null;
    var x;
    var y;
    if (coordString) {
        coords = coordString.split(/,/);
        x = Number(coords[0]);
        y = Number(coords[1]);
    } else {
        x = y = 0;
    }

    return [Selenium.prototype.getElementPositionLeft(element) + x, Selenium.prototype.getElementPositionTop(element) + y];
}


function add_sendkeys_key(keyboardEventKey, key, unicodeChar, alias, botKey) {
    botKey = botKey || key;
    if (bot.Keyboard.Keys[botKey]) {
        unicodeToKeys[unicodeChar] = bot.Keyboard.Keys[botKey];
        storedVars['KEY_' + key] = unicodeChar;
        if (alias) {
            storedVars['KEY_' + alias] = unicodeChar;
        }

        if (keyboardEventKey) {
            keyboardEventKeys[unicodeChar] = keyboardEventKey;
        }
        return true;
    }
    return false;
}

build_sendkeys_maps();


function build_sendkeys_maps() {
    add_sendkeys_key("Backspace", "BACKSPACE", '\uE003', "BKSP");
    add_sendkeys_key("Tab", "TAB", '\uE004');
    add_sendkeys_key("Enter", "ENTER", '\uE007');
    add_sendkeys_key("Shift", "SHIFT", '\uE008');
    add_sendkeys_key("Control", "CONTROL", '\uE009', "CTRL");
    add_sendkeys_key("Alt", "ALT", '\uE00A');
    add_sendkeys_key("Pause", "PAUSE", '\uE00B');
    add_sendkeys_key("Escape", "ESC", '\uE00C', "ESCAPE");
    add_sendkeys_key(null, "SPACE", '\uE00D');
    add_sendkeys_key("PageUp", "PAGE_UP", '\uE00E', "PGUP");
    add_sendkeys_key("PageDown", "PAGE_DOWN", '\uE00F', "PGDN");
    add_sendkeys_key("End", "END", '\uE010');
    add_sendkeys_key("Home", "HOME", '\uE011');
    add_sendkeys_key("ArrowLeft", "LEFT", '\uE012');
    add_sendkeys_key("ArrowUp", "UP", '\uE013');
    add_sendkeys_key("ArrowRight", "RIGHT", '\uE014');
    add_sendkeys_key("ArrowDown", "DOWN", '\uE015');
    add_sendkeys_key("Insert", "INSERT", '\uE016', "INS");
    add_sendkeys_key("Delete", "DELETE", '\uE017', "DEL");
    add_sendkeys_key(null, "SEMICOLON", '\uE018');
    add_sendkeys_key(null, "EQUALS", '\uE019');
    add_sendkeys_key(null, "NUMPAD0", '\uE01A', "N0", "NUM_ZERO");
    add_sendkeys_key(null, "NUMPAD1", '\uE01B', "N1", "NUM_ONE");
    add_sendkeys_key(null, "NUMPAD2", '\uE01C', "N2", "NUM_TWO");
    add_sendkeys_key(null, "NUMPAD3", '\uE01D', "N3", "NUM_THREE");
    add_sendkeys_key(null, "NUMPAD4", '\uE01E', "N4", "NUM_FOUR");
    add_sendkeys_key(null, "NUMPAD5", '\uE01F', "N5", "NUM_FIVE");
    add_sendkeys_key(null, "NUMPAD6", '\uE020', "N6", "NUM_SIX");
    add_sendkeys_key(null, "NUMPAD7", '\uE021', "N7", "NUM_SEVEN");
    add_sendkeys_key(null, "NUMPAD8", '\uE022', "N8", "NUM_EIGHT");
    add_sendkeys_key(null, "NUMPAD9", '\uE023', "N9", "NUM_NINE");
    add_sendkeys_key(null, "MULTIPLY", '\uE024', "MUL", "NUM_MULTIPLY");
    add_sendkeys_key(null, "ADD", '\uE025', "PLUS", "NUM_PLUS");
    add_sendkeys_key(null, "SEPARATOR", '\uE026', "SEP");
    add_sendkeys_key(null, "SUBTRACT", '\uE027', "MINUS", "NUM_MINUS");
    add_sendkeys_key(null, "DECIMAL", '\uE028', "PERIOD", "NUM_PERIOD");
    add_sendkeys_key(null, "DIVIDE", '\uE029', "DIV", "NUM_DIVISION");
    add_sendkeys_key("F1", "F1", '\uE031');
    add_sendkeys_key("F2", "F2", '\uE032');
    add_sendkeys_key("F3", "F3", '\uE033');
    add_sendkeys_key("F4", "F4", '\uE034');
    add_sendkeys_key("F5", "F5", '\uE035');
    add_sendkeys_key("F6", "F6", '\uE036');
    add_sendkeys_key("F7", "F7", '\uE037');
    add_sendkeys_key("F8", "F8", '\uE038');
    add_sendkeys_key("F9", "F9", '\uE039');
    add_sendkeys_key("F10", "F10", '\uE03A');
    add_sendkeys_key("F11", "F11", '\uE03B');
    add_sendkeys_key("F12", "F12", '\uE03C');

    add_sendkeys_key(null, "META", '\uE03D', "COMMAND");

}


function Selenium(browserbot) {
    this.browserbot = browserbot;
    this.optionLocatorFactory = new OptionLocatorFactory();
    this.page = function() {
        return browserbot;
    };
    this.defaultTimeout = Selenium.DEFAULT_TIMEOUT;
    this.mouseSpeed = Selenium.DEFAULT_MOUSE_SPEED;

    if (bot && bot.locators && bot.locators.add) {
        bot.locators.add('xpath', {
            single: function(target, opt_root) {
                return browserbot.locateElementByXPath(target, opt_root);
            },
            many: function(target, opt_root) {
                return browserbot.locateElementsByXPath(target, opt_root);
            }
        });

        bot.locators.add('css', {
            single: function(target, opt_root) {
                return browserbot.locateElementByCss(target, opt_root);
            },
            many: function(target, opt_root) {
                return eval_css(target, opt_root);
            }
        });
    }
}

Selenium.DEFAULT_TIMEOUT = 30 * 1000;
Selenium.DEFAULT_MOUSE_SPEED = 10;
Selenium.RIGHT_MOUSE_CLICK = 2;

Selenium.decorateFunctionWithTimeout = function(f, timeout, callback) {
    if (f == null) {
        return null;
    }

    var timeoutTime = getTimeoutTime(timeout);

    return function() {
        if (new Date().getTime() > timeoutTime) {
            if (callback != null) {
                callback();
            }
            throw new SeleniumError("Timed out after " + timeout + "ms");
        }
        return f();
    };
};

Selenium.prototype.reset = function() {
    this.defaultTimeout = Selenium.DEFAULT_TIMEOUT;
    this.browserbot.selectWindow("null");
    this.browserbot.resetPopups();
};

Selenium.prototype.doStore = function(value, varName) {
    browser.runtime.sendMessage({ "storeStr": value, "storeVar": varName });
};

Selenium.prototype.doEcho = function(value) {
    browser.runtime.sendMessage({ "echoStr": value });
};
Selenium.prototype.doStoreEval = function(value, varName) {
    browser.runtime.sendMessage({ "storeStr": this.getEval(value), "storeVar": varName });
};

Selenium.prototype.doPrePageWait = function() {
    // The following code is untested!! just replaced Eval()
    // window.zeuz_new_page = window.eval('(function() {return window.new_page;}())');
    window.zeuz_new_page = window.new_page;;
};
Selenium.prototype.doPageWait = function() {
    // The following code is untested!! just replaced Eval()
    // var expression = 'if(window.document.readyState=="complete"){return true;}else{return false;}';
    // window.zeuz_page_done = window.eval('(function() {' + expression + '}())');
    window.zeuz_page_done = window.document.readyState=="complete";
};

Selenium.prototype.doAjaxWait = function() {
    // var expression = 'if (window.ajax_obj) { if (window.ajax_obj.length == 0) {return true;} else {\
    //                   for (var index in window.ajax_obj) {\
    //                   if (window.ajax_obj[index].readyState !== 4 &&\
    //                   window.ajax_obj[index].readyState !== undefined &&\
    //                   window.ajax_obj[index].readyState !== 0) {return false;}}return true;}}\
    //                   else {if (window.origXMLHttpRequest) {window.origXMLHttpRequest = "";}return true;}';
    // window.zeuz_ajax_done = window.eval('(function() {' + expression + '}())');

    // The following code is untested!! just replaced Eval()
    if (window.ajax_obj) { 
        if (window.ajax_obj.length == 0) {
            window.zeuz_ajax_done= true;
        } 
        else {
            for (var index in window.ajax_obj) {
                if (window.ajax_obj[index].readyState !== 4 &&
                window.ajax_obj[index].readyState !== undefined &&
                window.ajax_obj[index].readyState !== 0) {
                    window.zeuz_ajax_done = false;
                    break;
                }
            }
            return true;
        }
    }
    else {
        if (window.origXMLHttpRequest) {
            window.origXMLHttpRequest = "";
        }
        window.zeuz_ajax_done = true; 
    };
};

Selenium.createForWindow = function(window, proxyInjectionMode) {
    if (!window.location) {
        throw "error: not a window!";
    }
    return new Selenium(BrowserBot.createForWindow(window, proxyInjectionMode));
};


Selenium.prototype.doWaitPreparation = function() {
    // window.eval('function setNewPageValue(e) {window.new_page = true;};\
    //             window.addEventListener("beforeunload", setNewPageValue, false);\
    //             if (window.XMLHttpRequest) {if (!window.origXMLHttpRequest || !window.ajax_obj) {\
    //             window.ajax_obj = []; window.origXMLHttpRequest = window.XMLHttpRequest;\
    //             window.XMLHttpRequest = function() { var xhr = new window.origXMLHttpRequest();\
    //             window.ajax_obj.push(xhr); return xhr;}}} function setDOMModifiedTime() {\
    //             window.domModifiedTime = Date.now();}var _win = window.document.body;\
    //             _win.addEventListener("DOMNodeInserted", setDOMModifiedTime, false);\
    //             _win.addEventListener("DOMNodeInsertedIntoDocument", setDOMModifiedTime, false);\
    //             _win.addEventListener("DOMNodeRemoved", setDOMModifiedTime, false);\
    //             _win.addEventListener("DOMNodeRemovedFromDocument", setDOMModifiedTime, false);\
    //             _win.addEventListener("DOMSubtreeModified", setDOMModifiedTime, false);');

    // The following code is untested!! just replaced Eval()
    function setNewPageValue(e) {
        window.new_page = true;
    };
    window.addEventListener("beforeunload", setNewPageValue, false);
    if (window.XMLHttpRequest) {
        if (!window.origXMLHttpRequest || !window.ajax_obj) {
            window.ajax_obj = []; window.origXMLHttpRequest = window.XMLHttpRequest;
            window.XMLHttpRequest = function() { var xhr = new window.origXMLHttpRequest();
            window.ajax_obj.push(xhr); return xhr;}
        }
    }
    function setDOMModifiedTime() {
        window.domModifiedTime = Date.now();
    }
    var _win = window.document.body;
    _win.addEventListener("DOMNodeInserted", setDOMModifiedTime, false);
    _win.addEventListener("DOMNodeInsertedIntoDocument", setDOMModifiedTime, false);
    _win.addEventListener("DOMNodeRemoved", setDOMModifiedTime, false);
    _win.addEventListener("DOMNodeRemovedFromDocument", setDOMModifiedTime, false);
    _win.addEventListener("DOMSubtreeModified", setDOMModifiedTime, false);
};


Selenium.prototype.doDomWait = function() {
    //sdx
    // window.zeuz_dom_time = window.eval('(function() {return window.domModifiedTime;}())');
    // The following code is untested!! just replaced Eval()

    window.zeuz_dom_time = window.domModifiedTime;
};

Selenium.prototype.doClick = function(locator) {
    var element = this.browserbot.findElement(locator);
    var elementWithHref = getAncestorOrSelfWithJavascriptHref(element);
    this.browserbot.clickElement(element);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true);
};

Selenium.prototype.doDoubleClick = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.clickElement(element);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true);
    this.browserbot.clickElement(element);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true);
    this.browserbot.doubleClickElement(element);
};

Selenium.prototype.doClickAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString);
    this.browserbot.clickElement(element, clientXY[0], clientXY[1]);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true, clientXY[0], clientXY[1]);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true, clientXY[0], clientXY[1]);
};

Selenium.prototype.doDoubleClickAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true, clientXY[0], clientXY[1]);
    this.browserbot.clickElement(element, clientXY[0], clientXY[1]);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true, clientXY[0], clientXY[1]);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true, clientXY[0], clientXY[1]);
    this.browserbot.clickElement(element, clientXY[0], clientXY[1]);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true, clientXY[0], clientXY[1]);
    this.browserbot.doubleClickElement(element, clientXY[0], clientXY[1]);
};


Selenium.prototype.doContextMenu = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.contextMenuOnElement(element);
};


Selenium.prototype.doContextMenuAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString)
    this.browserbot.contextMenuOnElement(element, clientXY[0], clientXY[1]);
};

Selenium.prototype.doFireEvent = function(locator, eventName) {
    var element = this.browserbot.findElement(locator);
    var doc = goog.dom.getOwnerDocument(element);
    var view = goog.dom.getWindow(doc);

    if (element.fireEvent && element.ownerDocument && element.ownerDocument.createEventObject) { // IE
        var ieEvent = createEventObject(element, false, false, false, false);
        element.fireEvent('on' + eventName, ieEvent);
    } else {
        var evt = doc.createEvent('HTMLEvents');
        evt.initEvent(eventName, true, true);
        element.dispatchEvent(evt);
    }
};

Selenium.prototype.doFocus = function(locator) {
    var element = this.browserbot.findElement(locator);
    if (element.focus) {
        element.focus();
    } else {
        bot.events.fire(element, bot.events.EventType.FOCUS);
    }
}

Selenium.prototype.doKeyPress = function(locator, keySequence) {
    var element = this.browserbot.findElement(locator);
    triggerKeyEvent(element, 'keypress', keySequence, true,
        this.browserbot.controlKeyDown,
        this.browserbot.altKeyDown,
        this.browserbot.shiftKeyDown,
        this.browserbot.metaKeyDown);
};

Selenium.prototype.doShiftKeyDown = function() {
    this.browserbot.shiftKeyDown = true;
    core.events.shiftKeyDown_ = true;
};

Selenium.prototype.doShiftKeyUp = function() {
    this.browserbot.shiftKeyDown = false;
    core.events.shiftKeyDown_ = false;
};

Selenium.prototype.doMetaKeyDown = function() {
    this.browserbot.metaKeyDown = true;
    core.events.metaKeyDown_ = true;
};

Selenium.prototype.doMetaKeyUp = function() {
    this.browserbot.metaKeyDown = false;
    core.events.metaKeyDown_ = false;
};

Selenium.prototype.doAltKeyDown = function() {
    this.browserbot.altKeyDown = true;
    core.events.altKeyDown_ = true;
};

Selenium.prototype.doAltKeyUp = function() {
    this.browserbot.altKeyDown = false;
    core.events.altKeyDown_ = false;
};

Selenium.prototype.doControlKeyDown = function() {
    this.browserbot.controlKeyDown = true;
    core.events.controlKeyDown_ = true;
};

Selenium.prototype.doControlKeyUp = function() {
    this.browserbot.controlKeyDown = false;
    core.events.controlKeyDown_ = false;
};

Selenium.prototype.doKeyUp = function(locator, keySequence) {
    var element = this.browserbot.findElement(locator);
    triggerKeyEvent(element, 'keyup', keySequence, true,
        this.browserbot.controlKeyDown,
        this.browserbot.altKeyDown,
        this.browserbot.shiftKeyDown,
        this.browserbot.metaKeyDown);
};

Selenium.prototype.doKeyDown = function(locator, keySequence) {
    var element = this.browserbot.findElement(locator);
    triggerKeyEvent(element, 'keydown', keySequence, true,
        this.browserbot.controlKeyDown,
        this.browserbot.altKeyDown,
        this.browserbot.shiftKeyDown,
        this.browserbot.metaKeyDown);
};


Selenium.prototype.doMouseOver = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mouseover', true);
};

Selenium.prototype.doMouseOut = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mouseout', true);
};

Selenium.prototype.doMouseDown = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true);
};

Selenium.prototype.doMouseDownRight = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mousedown', true, undefined, undefined, Selenium.RIGHT_MOUSE_CLICK);
};

Selenium.prototype.doMouseDownAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString)

    this.browserbot.triggerMouseEvent(element, 'mousedown', true, clientXY[0], clientXY[1]);
};

Selenium.prototype.doMouseDownRightAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString)

    this.browserbot.triggerMouseEvent(element, 'mousedown', true, clientXY[0], clientXY[1], Selenium.RIGHT_MOUSE_CLICK);
};

Selenium.prototype.doMouseUp = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true);
};

Selenium.prototype.doMouseUpRight = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true, undefined, undefined, Selenium.RIGHT_MOUSE_CLICK);
};

Selenium.prototype.doMouseUpAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString)

    this.browserbot.triggerMouseEvent(element, 'mouseup', true, clientXY[0], clientXY[1]);
};

Selenium.prototype.doMouseMove = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.triggerMouseEvent(element, 'mousemove', true);
};

Selenium.prototype.doMouseMoveAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString)

    this.browserbot.triggerMouseEvent(element, 'mousemove', true, clientXY[0], clientXY[1]);
};

Selenium.prototype.doType = function(locator, value) {
    var element = this.browserbot.findElement(locator);

    if (element.type === 'file') {
        if (hasChromeDebugger) {
            return new Promise(function(resolve, reject) {
                var krId = new Date().getTime() + '-' + Math.random();
                element.setAttribute('zeuz-recorder-id', krId);
                browser.runtime.sendMessage({ 
                    uploadFile: true,
                    locator: '[zeuz-recorder-id="' + krId + '"]',
                    krId: krId,
                    file: value
                }).then(function(result) {
                    if (result.status) {
                        resolve('success');
                    } else {
                        reject(result.err);
                    }
                });
            });
        } else {
            var self = this;
            return new Promise(function(resolve, reject) {
                element.focus();
                setTimeout(
                    function() {
                        $.ajax({
                            type: "POST",
                            url: 'http://localhost:18910/upload',
                            data: {
                                path: value
                            },
                            success: function() {
                                setTimeout(
                                    function() {
                                        resolve('success')
                                    },
                                    3000
                                );
                            },
                            error: function(jqXHR, textStatus, errorThrown) {
                                reject(textStatus);
                            }
                        });
                    },
                    500
                )
            });
        }
    }

    if (this.browserbot.controlKeyDown || this.browserbot.altKeyDown || this.browserbot.metaKeyDown) {
        throw new SeleniumError("type not supported immediately after call to controlKeyDown() or altKeyDown() or metaKeyDown()");
    }
    core.events.setValue(element, '');
    bot.action.type(element, value);
};

Selenium.prototype.doMouseUpRightAt = function(locator, coordString) {
    var element = this.browserbot.findElement(locator);
    var clientXY = getClientXY(element, coordString)

    this.browserbot.triggerMouseEvent(element, 'mouseup', true, clientXY[0], clientXY[1], Selenium.RIGHT_MOUSE_CLICK);
};

Selenium.prototype.doSetText = function(locator, value) {
    var element = this.browserbot.findElement(locator);
    core.events.setValue(element, value);
};

Selenium.prototype.doTypeKeys = function(locator, value) {
    var keys = new String(value).split("");
    for (var i = 0; i < keys.length; i++) {
        var c = keys[i];
        this.doKeyDown(locator, c);
        this.doKeyUp(locator, c);
        this.doKeyPress(locator, c);
    }
};


Selenium.prototype.doSendKeys = function(locator, value) {
    if (this.browserbot.controlKeyDown || this.browserbot.altKeyDown || this.browserbot.metaKeyDown) {
        throw new SeleniumError("type not supported immediately after call to controlKeyDown() or altKeyDown() or metaKeyDown()");
    }

    var element = this.browserbot.findElement(locator);
    if (value.match(/[\uE000-\uF8FF]/)) {
        var keysRa = value.split(/([\0-\uDFFF]+)|([\uE000-\uF8FF])/).filter(function(key) {
            return (key && key.length > 0);
        }).map(function(key) {
            if (key.match(/[\uE000-\uF8FF]/) && unicodeToKeys.hasOwnProperty(key)) {
                return unicodeToKeys[key];
            }
            return key;
        });

        bot.action.type(element, keysRa);
    } else {
        bot.action.type(element, value);
    }
};


Selenium.prototype.doSetSpeed = function(value) {
};

Selenium.prototype.getSpeed = function() {
};

Selenium.prototype.findToggleButton = function(locator) {
    var element = this.browserbot.findElement(locator);
    if (element.checked == null) {
        Assert.fail("Element " + locator + " is not a toggle-button.");
    }
    return element;
};

Selenium.prototype.doCheck = function(locator) {
    this.findToggleButton(locator).checked = true;
};

Selenium.prototype.doUncheck = function(locator) {
    this.findToggleButton(locator).checked = false;
};

Selenium.prototype.doAddSelection = function(locator, optionLocator) {
    var element = this.browserbot.findElement(locator);
    if (!("options" in element)) {
        throw new SeleniumError("Specified element is not a Select (has no options)");
    }
    var locator = this.optionLocatorFactory.fromLocatorString(optionLocator);
    var option = locator.findOption(element);
    this.browserbot.addSelection(element, option);
};

Selenium.prototype.doRemoveSelection = function(locator, optionLocator) {
    var element = this.browserbot.findElement(locator);
    if (!("options" in element)) {
        throw new SeleniumError("Specified element is not a Select (has no options)");
    }
    var locator = this.optionLocatorFactory.fromLocatorString(optionLocator);
    var option = locator.findOption(element);
    this.browserbot.removeSelection(element, option);
};

Selenium.prototype.doRemoveAllSelections = function(locator) {
    var element = this.browserbot.findElement(locator);
    if (!("options" in element)) {
        throw new SeleniumError("Specified element is not a Select (has no options)");
    }
    for (var i = 0; i < element.options.length; i++) {
        this.browserbot.removeSelection(element, element.options[i]);
    }
}

Selenium.prototype.doSubmit = function(formLocator) {
    var form = this.browserbot.findElement(formLocator);
    return this.browserbot.submit(form);

};

Selenium.prototype.doSelect = function(selectLocator, optionLocator) {
    var element = this.browserbot.findElement(selectLocator);
    if (!("options" in element)) {
        throw new SeleniumError("Specified element is not a Select (has no options)");
    }
    var locator = this.optionLocatorFactory.fromLocatorString(optionLocator);
    var option = locator.findOption(element);
    this.browserbot.selectOption(element, option);
};


Selenium.prototype.makePageLoadCondition = function(timeout) {
    if (timeout == null) {
        timeout = this.defaultTimeout;
    }

    if (timeout == 0) {
        this._abortXhrRequest();
        return;
    }
    return Selenium.decorateFunctionWithTimeout(fnBind(this._isNewPageLoaded, this), timeout, fnBind(this._abortXhrRequest, this));
};

Selenium.prototype.doOpen = function(url, ignoreResponseCode) {
    if (ignoreResponseCode == null || ignoreResponseCode.length == 0) {
        this.browserbot.ignoreResponseCode = true;
    } else if (ignoreResponseCode.toLowerCase() == "true") {
        this.browserbot.ignoreResponseCode = true;
    } else {
        this.browserbot.ignoreResponseCode = false;
    }
    this.browserbot.openLocation(url);
    if (window["proxyInjectionMode"] == null || !window["proxyInjectionMode"]) {
        return this.makePageLoadCondition();
    }
};

Selenium.prototype.doOpenWindow = function(url, windowID) {
    this.browserbot.openWindow(url, windowID);
};

Selenium.prototype.doSelectWindow = function(windowID) {
    this.browserbot.selectWindow(windowID);
};

Selenium.prototype.doSelectPopUp = function(windowID) {
    this.browserbot.selectPopUp(windowID);
};

Selenium.prototype.doDeselectPopUp = function() {
    this.browserbot.selectWindow();
}

Selenium.prototype.doSelectFrame = function(locator) {
    this.browserbot.selectFrame(locator);
};

Selenium.prototype.getWhetherThisFrameMatchFrameExpression = function(currentFrameString, target) {
    return this.browserbot.doesThisFrameMatchFrameExpression(currentFrameString, target);
};

Selenium.prototype.getWhetherThisWindowMatchWindowExpression = function(currentWindowString, target) {
    if (window.opener != null && window.opener[target] != null && window.opener[target] == window) {
        return true;
    }
    return false;
};

Selenium.prototype.doWaitForPopUp = function(windowID, timeout) {
    if (!timeout) {
        timeout = this.defaultTimeout;
    }
    var timeoutTime = getTimeoutTime(timeout);

    var popupLoadedPredicate = function() {
        var targetWindow;
        try {
            if (windowID && windowID != 'null') {
                targetWindow = selenium.browserbot.getWindowByName(windowID, true);
            } else {
                var names = selenium.browserbot.getNonTopWindowNames();
                targetWindow = selenium.browserbot.getWindowByName(names[0], true);
            }
        } catch (e) {
            if (new Date().getTime() > timeoutTime) {
                throw e;
            }
        }

        if (!targetWindow) return false;
        try {
            if (!targetWindow.location) return false;
            if ("about:blank" == targetWindow.location) return false;
        } catch (e) {
            return false;
        }
        if (browserVersion.isKonqueror) {
            if ("/" == targetWindow.location.href) {
                return false;
            }
        }
        if (browserVersion.isSafari) {
            if (targetWindow.location.href == selenium.browserbot.buttonWindow.location.href) {
                return false;
            }
        }
        if (!targetWindow.document) return false;
        if (!selenium.browserbot.getCurrentWindow().document.readyState) {
            return true;
        }
        if ('complete' != targetWindow.document.readyState) return false;
        return true;
    };

    return Selenium.decorateFunctionWithTimeout(popupLoadedPredicate, timeout);
}

Selenium.prototype.doWaitForPopUp.dontCheckAlertsAndConfirms = true;

Selenium.prototype.doGoBack = function() {
    this.browserbot.goBack();
};

Selenium.prototype.doRefresh = function() {
    this.browserbot.refresh();
};

Selenium.prototype.ensureNoUnhandledPopups = function() {
    if (this.browserbot.hasAlerts()) {
        throw new SeleniumError("There was an unexpected Alert! [" + this.browserbot.getNextAlert() + "]");
    }
    if (this.browserbot.hasConfirmations()) {
        throw new SeleniumError("There was an unexpected Confirmation! [" + this.browserbot.getNextConfirmation() + "]");
    }
};

Selenium.prototype.isAlertPresent = function() {
    return this.browserbot.hasAlerts();
};

Selenium.prototype.doClose = function() {
    this.browserbot.close();
};

Selenium.prototype.isPromptPresent = function() {
    return this.browserbot.hasPrompts();
};

Selenium.prototype.isConfirmationPresent = function() {
    return this.browserbot.hasConfirmations();
};
Selenium.prototype.getAlert = function() {
    if (!this.browserbot.hasAlerts()) {
        Assert.fail("There were no alerts");
    }
    return this.browserbot.getNextAlert();
};
Selenium.prototype.getAlert.dontCheckAlertsAndConfirms = true;

Selenium.prototype.getConfirmation = function() {
    if (!this.browserbot.hasConfirmations()) {
        Assert.fail("There were no confirmations");
    }
    return this.browserbot.getNextConfirmation();
};
Selenium.prototype.getConfirmation.dontCheckAlertsAndConfirms = true;

Selenium.prototype.getPrompt = function() {
    if (!this.browserbot.hasPrompts()) {
        Assert.fail("There were no prompts");
    }
    return this.browserbot.getNextPrompt();
};

Selenium.prototype.getLocation = function() {
    return this.browserbot.getCurrentWindow().location.href;
};

Selenium.prototype.getTitle = function() {
    return this.browserbot.getTitle();
};


Selenium.prototype.getBodyText = function() {
    return this.browserbot.bodyText();
};


Selenium.prototype.getValue = function(locator) {
    var element = this.browserbot.findElement(locator)
    return getInputValue(element).trim();
};

Selenium.prototype.getText = function(locator) {
    var element = this.browserbot.findElement(locator);
    return core.text.getElementText(element);
};

Selenium.prototype.doHighlight = function(locator) {
    var element = this.browserbot.findElement(locator);
    this.browserbot.highlight(element, true);
};

// The following code is untested!! just replaced Eval()

// Selenium.prototype.getEval = function(script) {
//     try {
//         var window = this.browserbot.getCurrentWindow();
//         var result = eval(script);
//         if (null == result) return "null";
//         return result;
//     } catch (e) {
//         throw new SeleniumError("Threw an exception: " + extractExceptionMessage(e));
//     }
// };

Selenium.prototype.isChecked = function(locator) {
    var element = this.browserbot.findElement(locator);
    if (element.checked == null) {
        throw new SeleniumError("Element " + locator + " is not a toggle-button.");
    }
    return element.checked;
};

Selenium.prototype.getTable = function(tableCellAddress) {
    pattern = /(.*)\.(\d+)\.(\d+)/;

    if (!pattern.test(tableCellAddress)) {
        throw new SeleniumError("Invalid target format. Correct format is tableName.rowNum.columnNum");
    }

    pieces = tableCellAddress.match(pattern);

    tableName = pieces[1];
    row = pieces[2];
    col = pieces[3];

    var table = this.browserbot.findElement(tableName);
    if (row > table.rows.length) {
        Assert.fail("Cannot access row " + row + " - table has " + table.rows.length + " rows");
    } else if (col > table.rows[row].cells.length) {
        Assert.fail("Cannot access column " + col + " - table row has " + table.rows[row].cells.length + " columns");
    } else {
        actualContent = getText(table.rows[row].cells[col]);
        return actualContent.trim();
    }
    return null;
};

Selenium.prototype.getSelectedLabels = function(selectLocator) {
    return this.findSelectedOptionProperties(selectLocator, "text");
};

Selenium.prototype.getSelectedLabel = function(selectLocator) {
    return this.findSelectedOptionProperty(selectLocator, "text");
};

Selenium.prototype.getSelectedValues = function(selectLocator) {
    return this.findSelectedOptionProperties(selectLocator, "value");
};

Selenium.prototype.getSelectedValue = function(selectLocator) {
    return this.findSelectedOptionProperty(selectLocator, "value");
}

Selenium.prototype.getSelectedIndexes = function(selectLocator) {
    return this.findSelectedOptionProperties(selectLocator, "index");
};

Selenium.prototype.getSelectedIndex = function(selectLocator) {
    return this.findSelectedOptionProperty(selectLocator, "index");
};

Selenium.prototype.getSelectedIds = function(selectLocator) {
    return this.findSelectedOptionProperties(selectLocator, "id");
};

Selenium.prototype.getSelectedId = function(selectLocator) {
    return this.findSelectedOptionProperty(selectLocator, "id");
};

Selenium.prototype.isSomethingSelected = function(selectLocator) {
    var element = this.browserbot.findElement(selectLocator);
    if (!("options" in element)) {
        throw new SeleniumError("Specified element is not a Select (has no options)");
    }

    var selectedOptions = [];

    for (var i = 0; i < element.options.length; i++) {
        if (element.options[i].selected) {
            return true;
        }
    }
    return false;
};

Selenium.prototype.findSelectedOptionProperties = function(locator, property) {
    var element = this.browserbot.findElement(locator);
    if (!("options" in element)) {
        throw new SeleniumError("Specified element is not a Select (has no options)");
    }

    var selectedOptions = [];

    for (var i = 0; i < element.options.length; i++) {
        if (element.options[i].selected) {
            var propVal = element.options[i][property];
            selectedOptions.push(propVal);
        }
    }
    if (selectedOptions.length == 0) Assert.fail("No option selected");
    return selectedOptions;
};

Selenium.prototype.findSelectedOptionProperty = function(locator, property) {
    var selectedOptions = this.findSelectedOptionProperties(locator, property);
    if (selectedOptions.length > 1) {
        Assert.fail("More than one selected option!");
    }
    return selectedOptions[0];
};

Selenium.prototype.getSelectOptions = function(selectLocator) {
    var element = this.browserbot.findElement(selectLocator);

    var selectOptions = [];

    for (var i = 0; i < element.options.length; i++) {
        var option = element.options[i].text;
        selectOptions.push(option);
    }

    return selectOptions;
};


Selenium.prototype.getAttribute = function(attributeLocator) {
    var result = this.browserbot.findAttribute(attributeLocator);
    if (result == null) {
        throw new SeleniumError("Could not find element attribute: " + attributeLocator);
    }
    return result;
};

Selenium.prototype.isTextPresent = function(pattern) {
    var allText = this.browserbot.bodyText();

    var patternMatcher = new PatternMatcher(pattern);
    if (patternMatcher.strategy == PatternMatcher.strategies.glob) {
        if (pattern.indexOf("glob:") == 0) {
            pattern = pattern.substring("glob:".length); // strip off "glob:"
        }
        patternMatcher.matcher = new PatternMatcher.strategies.globContains(pattern);
    } else if (patternMatcher.strategy == PatternMatcher.strategies.exact) {
        pattern = pattern.substring("exact:".length); // strip off "exact:"
        return allText.indexOf(pattern) != -1;
    }
    return patternMatcher.matches(allText);
};

Selenium.prototype.isElementPresent = function(locator) {
    var element = this.browserbot.findElementOrNull(locator);
    if (element == null) {
        return false;
    }
    return true;
};

Selenium.prototype.isVisible = function(locator) {
    var element;
    element = this.browserbot.findElement(locator);
    if (element.tagName) {
        var tagName = new String(element.tagName).toLowerCase();
        if (tagName == "input") {
            if (element.type) {
                var elementType = new String(element.type).toLowerCase();
                if (elementType == "hidden") {
                    return false;
                }
            }
        }
    }
    var visibility = this.findEffectiveStyleProperty(element, "visibility");
    var _isDisplayed = this._isDisplayed(element);
    return (visibility != "hidden" && _isDisplayed);
};

Selenium.prototype.findEffectiveStyleProperty = function(element, property) {
    var effectiveStyle = this.findEffectiveStyle(element);
    var propertyValue = effectiveStyle[property];
    if (propertyValue == 'inherit' && element.parentNode.style) {
        return this.findEffectiveStyleProperty(element.parentNode, property);
    }
    return propertyValue;
};

Selenium.prototype._isDisplayed = function(element) {
    var display = this.findEffectiveStyleProperty(element, "display");
    if (display == "none") return false;
    if (element.parentNode.style) {
        return this._isDisplayed(element.parentNode);
    }
    return true;
};

Selenium.prototype.findEffectiveStyle = function(element) {
    if (element.style == undefined) {
        return undefined;
    }
    var window = this.browserbot.getCurrentWindow();
    if (window.getComputedStyle) {
        return window.getComputedStyle(element, null);
    }
    if (element.currentStyle) {
        return element.currentStyle;
    }

    if (window.document.defaultView && window.document.defaultView.getComputedStyle) {
        return window.document.defaultView.getComputedStyle(element, null);
    }


    throw new SeleniumError("cannot determine effective stylesheet in this browser");
};

Selenium.prototype.isEditable = function(locator) {
    var element = this.browserbot.findElement(locator);
    if (element.value == undefined) {
        Assert.fail("Element " + locator + " is not an input.");
    }
    if (element.disabled) {
        return false;
    }
    var readOnlyNode = element.getAttributeNode('readonly');
    if (readOnlyNode) {
        if (typeof(readOnlyNode.nodeValue) == "boolean") {
            var readOnly = readOnlyNode.nodeValue;
            if (readOnly) {
                return false;
            }
        } else {
            return false;
        }
    }
    return true;
};

Selenium.prototype.getAllButtons = function() {
    return this.browserbot.getAllButtons();
};

Selenium.prototype.getAllLinks = function() {
    return this.browserbot.getAllLinks();
};

Selenium.prototype.getAllFields = function() {
    return this.browserbot.getAllFields();
};

// The following code is untested!! just replaced Eval()

// Selenium.prototype.getAttributeFromAllWindows = function(attributeName) {
//     var attributes = new Array();

//     var win = selenium.browserbot.topWindow;
//     try {
//         attributes.push(eval("win." + attributeName));
//     } catch (ignored) {
//     }
//     for (var windowName in this.browserbot.openedWindows) {
//         try {
//             win = selenium.browserbot.openedWindows[windowName];
//             if (!selenium.browserbot._windowClosed(win)) {
//                 attributes.push(eval("win." + attributeName));
//             }
//         } catch (e) {}
//     }
//     return attributes;
// };


// The following code is untested!! just replaced Eval()

// Selenium.prototype.findWindow = function(soughtAfterWindowPropertyValue) {
//     var targetPropertyName = "name";
//     if (soughtAfterWindowPropertyValue.match("^title=")) {
//         targetPropertyName = "document.title";
//         soughtAfterWindowPropertyValue = soughtAfterWindowPropertyValue.replace(/^title=/, "");
//     } else {
//         if (PatternMatcher.matches(soughtAfterWindowPropertyValue, "")) {
//             return this.browserbot.getCurrentWindow();
//         }
//     }

//     if (PatternMatcher.matches(soughtAfterWindowPropertyValue, eval("this.browserbot.topWindow." + targetPropertyName))) {
//         return this.browserbot.topWindow;
//     }
//     for (windowName in selenium.browserbot.openedWindows) {
//         var openedWindow = selenium.browserbot.openedWindows[windowName];
//         if (PatternMatcher.matches(soughtAfterWindowPropertyValue, eval("openedWindow." + targetPropertyName))) {
//             return openedWindow;
//         }
//     }
//     throw new SeleniumError("could not find window with property " + targetPropertyName + " matching " + soughtAfterWindowPropertyValue);
// };

Selenium.prototype.doSetMouseSpeed = function(pixels) {
    var intValue = new Number(pixels);
    if (intValue.constructor != Number ||
        intValue < 0) {
        this.mouseSpeed = Selenium.DEFAULT_MOUSE_SPEED;
    } else {
        this.mouseSpeed = pixels;
    }
}

Selenium.prototype.getMouseSpeed = function() {
    return this.mouseSpeed;
}


Selenium.prototype.doDragAndDrop = function(locator, movementsString) {
    var element = this.browserbot.findElement(locator);
    var clientStartXY = getClientXY(element)
    var clientStartX = clientStartXY[0];
    var clientStartY = clientStartXY[1];

    var movements = movementsString.split(/,/);
    var movementX = Number(movements[0]);
    var movementY = Number(movements[1]);

    var clientFinishX = ((clientStartX + movementX) < 0) ? 0 : (clientStartX + movementX);
    var clientFinishY = ((clientStartY + movementY) < 0) ? 0 : (clientStartY + movementY);

    var mouseSpeed = this.mouseSpeed;
    var move = function(current, dest) {
        if (current == dest) return current;
        if (Math.abs(current - dest) < mouseSpeed) return dest;
        return (current < dest) ? current + mouseSpeed : current - mouseSpeed;
    }

    this.browserbot.triggerMouseEvent(element, 'mousedown', true, clientStartX, clientStartY);
    this.browserbot.triggerMouseEvent(element, 'mousemove', true, clientStartX, clientStartY);
    var clientX = clientStartX;
    var clientY = clientStartY;

    while ((clientX != clientFinishX) || (clientY != clientFinishY)) {
        clientX = move(clientX, clientFinishX);
        clientY = move(clientY, clientFinishY);
        this.browserbot.triggerMouseEvent(element, 'mousemove', true, clientX, clientY);
    }

    this.browserbot.triggerMouseEvent(element, 'mousemove', true, clientFinishX, clientFinishY);
    this.browserbot.triggerMouseEvent(element, 'mouseup', true, clientFinishX, clientFinishY);
};

Selenium.prototype.doDragAndDropToObjectByJqueryUI = function(locatorOfObjectToBeDragged, locatorOfDragDestinationObject) {
    var draggable = $(this.browserbot.findElement(locatorOfObjectToBeDragged));
    var droppable = $(this.browserbot.findElement(locatorOfDragDestinationObject));

    droppableOffset = droppable.offset(),
    draggableOffset = draggable.offset(),
    dx = droppableOffset.left + (droppable.width() / 2) - draggableOffset.left,
    dy = droppableOffset.top + (droppable.height() / 2) - draggableOffset.top;

    draggable.simulate( "drag", {
        dx: dx,
        dy: dy
    });
}

Selenium.prototype.doDragAndDropToObject = function(locatorOfObjectToBeDragged, locatorOfDragDestinationObject) {
    if (!this.browserbot.findElement(locatorOfObjectToBeDragged).draggable) {
        var startX = this.getElementPositionLeft(locatorOfObjectToBeDragged);
        var startY = this.getElementPositionTop(locatorOfObjectToBeDragged);

        var destinationLeftX = this.getElementPositionLeft(locatorOfDragDestinationObject);
        var destinationTopY = this.getElementPositionTop(locatorOfDragDestinationObject);
        var destinationWidth = this.getElementWidth(locatorOfDragDestinationObject);
        var destinationHeight = this.getElementHeight(locatorOfDragDestinationObject);

        var endX = Math.round(destinationLeftX + (destinationWidth / 2));
        var endY = Math.round(destinationTopY + (destinationHeight / 2));

        var deltaX = endX - startX;
        var deltaY = endY - startY;

        var movementsString = "" + deltaX + "," + deltaY;
        this.doDragAndDrop(locatorOfObjectToBeDragged, movementsString);
    } else {
        var element = this.browserbot.findElement(locatorOfObjectToBeDragged);
        var target = this.browserbot.findElement(locatorOfDragDestinationObject);
        this.browserbot.triggerDragEvent(element, target);
    }
};

Selenium.prototype.doWindowFocus = function() {
    this.browserbot.getCurrentWindow().focus();
};


Selenium.prototype.doWindowMaximize = function() {
    var window = this.browserbot.getCurrentWindow();
    if (window != null && window.screen) {
        window.moveTo(0, 0);
        if (window.screenX != 0) {
            window.moveTo(0, 1);
        }

        window.resizeTo(screen.availWidth, screen.availHeight);
    }
};

Selenium.prototype.getAllWindowIds = function() {
    return this.getAttributeFromAllWindows("id");
};

Selenium.prototype.getAllWindowNames = function() {
    return this.getAttributeFromAllWindows("name");
};

Selenium.prototype.getAllWindowTitles = function() {
    return this.getAttributeFromAllWindows("document.title");
};

Selenium.prototype.getHtmlSource = function() {
    return this.browserbot.getDocument().getElementsByTagName("html")[0].innerHTML;
};

Selenium.prototype.doSetCursorPosition = function(locator, position) {
    var element = this.browserbot.findElement(locator);
    if (element.value == undefined) {
        Assert.fail("Element " + locator + " is not an input.");
    }
    if (position == -1) {
        position = element.value.length;
    }

    if (element.setSelectionRange && !browserVersion.isOpera) {
        element.focus();
        element.setSelectionRange( /*start*/ position, /*end*/ position);
    } else if (element.createTextRange) {
        bot.events.fire(element, bot.events.EventType.FOCUS);
        var range = element.createTextRange();
        range.collapse(true);
        range.moveEnd('character', position);
        range.moveStart('character', position);
        range.select();
    }
}

Selenium.prototype.getElementIndex = function(locator) {
    var element = this.browserbot.findElement(locator);
    var previousSibling;
    var index = 0;
    while ((previousSibling = element.previousSibling) != null) {
        if (!this._isCommentOrEmptyTextNode(previousSibling)) {
            index++;
        }
        element = previousSibling;
    }
    return index;
}

Selenium.prototype.isOrdered = function(locator1, locator2) {
    var element1 = this.browserbot.findElement(locator1);
    var element2 = this.browserbot.findElement(locator2);
    if (element1 === element2) return false;

    var previousSibling;
    while ((previousSibling = element2.previousSibling) != null) {
        if (previousSibling === element1) {
            return true;
        }
        element2 = previousSibling;
    }
    return false;
}

Selenium.prototype._isCommentOrEmptyTextNode = function(node) {
    return node.nodeType == 8 || ((node.nodeType == 3) && !(/[^\t\n\r ]/.test(node.data)));
}

Selenium.prototype.getElementPositionLeft = function(locator) {
    var element;
    if ("string" == typeof locator) {
        element = this.browserbot.findElement(locator);
    } else {
        element = locator;
    }
    var x = element.offsetLeft;
    var elementParent = element.offsetParent;

    while (elementParent != null) {
        if (document.all) {
            if ((elementParent.tagName != "TABLE") && (elementParent.tagName != "BODY")) {
                x += elementParent.clientLeft;
            }
        } else
        {
            if (elementParent.tagName == "TABLE") {
                var parentBorder = parseInt(elementParent.border);
                if (isNaN(parentBorder)) {
                    var parentFrame = elementParent.getAttribute('frame');
                    if (parentFrame != null) {
                        x += 1;
                    }
                } else if (parentBorder > 0) {
                    x += parentBorder;
                }
            }
        }
        x += elementParent.offsetLeft;
        elementParent = elementParent.offsetParent;
    }
    return x;
};

Selenium.prototype.getElementPositionTop = function(locator) {
    var element;
    if ("string" == typeof locator) {
        element = this.browserbot.findElement(locator);
    } else {
        element = locator;
    }

    var y = 0;

    while (element != null) {
        if (document.all) {
            if ((element.tagName != "TABLE") && (element.tagName != "BODY")) {
                y += element.clientTop;
            }
        } else
        {
            if (element.tagName == "TABLE") {
                var parentBorder = parseInt(element.border);
                if (isNaN(parentBorder)) {
                    var parentFrame = element.getAttribute('frame');
                    if (parentFrame != null) {
                        y += 1;
                    }
                } else if (parentBorder > 0) {
                    y += parentBorder;
                }
            }
        }
        y += element.offsetTop;

        if (element.offsetParent && element.offsetParent.offsetHeight && element.offsetParent.offsetHeight < element.offsetHeight) {
            element = element.offsetParent.offsetParent;
        } else {
            element = element.offsetParent;
        }
    }
    return y;
};

Selenium.prototype.getElementWidth = function(locator) {
    var element = this.browserbot.findElement(locator);
    return element.offsetWidth;
};

Selenium.prototype.getElementHeight = function(locator) {
    var element = this.browserbot.findElement(locator);
    return element.offsetHeight;
};

Selenium.prototype.getCursorPosition = function(locator) {
    var element = this.browserbot.findElement(locator);
    var doc = this.browserbot.getDocument();
    var win = this.browserbot.getCurrentWindow();
    if (doc.selection && !browserVersion.isOpera) {
        try {
            var selectRange = doc.selection.createRange().duplicate();
            var elementRange = element.createTextRange();
            selectRange.move("character", 0);
            elementRange.move("character", 0);
            var inRange1 = selectRange.inRange(elementRange);
            var inRange2 = elementRange.inRange(selectRange);
            elementRange.setEndPoint("EndToEnd", selectRange);
        } catch (e) {
            Assert.fail("There is no cursor on this page!");
        }
        var answer = String(elementRange.text).replace(/\r/g, "").length;
        return answer;
    } else {
        if (typeof(element.selectionStart) != "undefined") {
            if (win.getSelection && typeof(win.getSelection().rangeCount) != undefined && win.getSelection().rangeCount == 0) {
                Assert.fail("There is no cursor on this page!");
            }
            return element.selectionStart;
        }
    }
    throw new Error("Couldn't detect cursor position on this browser!");
}


Selenium.prototype.getExpression = function(expression) {
    return expression;
};

Selenium.prototype.getXpathCount = function(xpath) {
    var result = this.browserbot.evaluateXPathCount(xpath, this.browserbot.getDocument());
    return result;
};

Selenium.prototype.getCssCount = function(css) {
    var result = this.browserbot.evaluateCssCount(css, this.browserbot.getDocument());
    return result;
};

Selenium.prototype.doAssignId = function(locator, identifier) {
    var element = this.browserbot.findElement(locator);
    element.id = identifier;
};

Selenium.prototype.doAllowNativeXpath = function(allow) {
    if ("false" == allow || "0" == allow) { // The strings "false" and "0" are true values in JS
        allow = false;
    }
    this.browserbot.setAllowNativeXPath(allow);
}

Selenium.prototype.doIgnoreAttributesWithoutValue = function(ignore) {
    if ('false' == ignore || '0' == ignore) {
        ignore = false;
    }
    this.browserbot.setIgnoreAttributesWithoutValue(ignore);
}

Selenium.prototype.doWaitForCondition = function(script, timeout) {
    return Selenium.decorateFunctionWithTimeout(function() {
        var window = selenium.browserbot.getCurrentWindow();
        // The following code is untested!! just replaced Eval()
        // return eval(script);
    }, timeout);
};

Selenium.prototype.doWaitForCondition.dontCheckAlertsAndConfirms = true;

Selenium.prototype.doSetTimeout = function(timeout) {
    if (!timeout) {
        timeout = Selenium.DEFAULT_TIMEOUT;
    }
    this.defaultTimeout = timeout;
}

Selenium.prototype.doWaitForPageToLoad = function(timeout) {
    if (window["proxyInjectionMode"] == null || !window["proxyInjectionMode"]) {
        return this.makePageLoadCondition(timeout);
    }
};

Selenium.prototype.doWaitForFrameToLoad = function(frameAddress, timeout) {
    if (window["proxyInjectionMode"] == null || !window["proxyInjectionMode"]) {
        return this.makePageLoadCondition(timeout);
    }
};

Selenium.prototype._isNewPageLoaded = function() {
    return this.browserbot.isNewPageLoaded();
};

Selenium.prototype._abortXhrRequest = function() {
    return this.browserbot.abortXhrRequest();
};

Selenium.prototype.doWaitForPageToLoad.dontCheckAlertsAndConfirms = true;

// The following code is untested!! just replaced Eval()

// Selenium.prototype.preprocessParameter = function(value) {
//     var match = value.match(/^javascript\{((.|\r?\n)+)\}$/);
//     if (match && match[1]) {
//         var result = eval(match[1]);
//         return result == null ? null : result.toString();
//     }
//     return this.replaceVariables(value);
// };

Selenium.prototype.replaceVariables = function(str) {
    var stringResult = str;

    var match = stringResult.match(/\$\{\w+\}/g);
    if (!match) {

        return stringResult;
    }

    for (var i = 0; match && i < match.length; i++) {
        var variable = match[i];
        var name = variable.substring(2, variable.length - 1);
        var replacement = storedVars[name];
        if (replacement && typeof(replacement) === 'string' && replacement.indexOf('$') != -1) {
            replacement = replacement.replace(/\$/g, '$$$$');
        }
        if (replacement != undefined) {
            stringResult = stringResult.replace(variable, replacement);
        }
    }
    return stringResult;
};

Selenium.prototype.getCookie = function() {
    var doc = this.browserbot.getDocument();
    return doc.cookie;
};

Selenium.prototype.getCookieByName = function(name) {
    var v = this.browserbot.getCookieByName(name);
    if (v === null) {
        throw new SeleniumError("Cookie '" + name + "' was not found");
    }
    return v;
};

Selenium.prototype.isCookiePresent = function(name) {
    /**
     * Returns true if a cookie with the specified name is present, or false otherwise.
     * @param name the name of the cookie
     * @return boolean true if a cookie with the specified name is present, or false otherwise.
     */
    var v = this.browserbot.getCookieByName(name);
    var absent = (v === null);
    return !absent;
}

Selenium.prototype.doCreateCookie = function(nameValuePair, optionsString) {
    var results = /[^\s=\[\]\(\),"\/\?@:;]+=[^\s=\[\]\(\),"\/\?@:;]*/.test(nameValuePair);
    if (!results) {
        throw new SeleniumError("Invalid parameter.");
    }
    var cookie = nameValuePair.trim();
    results = /max_age=(\d+)/.exec(optionsString);
    if (results) {
        var expireDateInMilliseconds = (new Date()).getTime() + results[1] * 1000;
        cookie += "; expires=" + new Date(expireDateInMilliseconds).toGMTString();
    }
    results = /path=([^\s,]+)[,]?/.exec(optionsString);
    if (results) {
        var path = results[1];
        if (browserVersion.khtml) {
            if ("/" != path) {
                path = path.replace(/\/$/, "");
            }
        }
        cookie += "; path=" + path;
    }
    results = /domain=([^\s,]+)[,]?/.exec(optionsString);
    if (results) {
        var domain = results[1];
        cookie += "; domain=" + domain;
    }
    this.browserbot.getDocument().cookie = cookie;
};

Selenium.prototype.doDeleteCookie = function(name, optionsString) {
    var path = "";
    var domain = "";
    var recurse = false;
    var matched = false;
    results = /path=([^\s,]+)[,]?/.exec(optionsString);
    if (results) {
        matched = true;
        path = results[1];
    }
    results = /domain=([^\s,]+)[,]?/.exec(optionsString);
    if (results) {
        matched = true;
        domain = results[1];
    }
    results = /recurse=([^\s,]+)[,]?/.exec(optionsString);
    if (results) {
        matched = true;
        recurse = results[1];
        if ("false" == recurse) {
            recurse = false;
        }
    }
    if (optionsString && !matched) {
        path = optionsString;
    }
    if (browserVersion.khtml) {
        if ("/" != path) {
            path = path.replace(/\/$/, "");
        }
    }
    path = path.trim();
    domain = domain.trim();
    var cookieName = name.trim();
    if (recurse) {
        this.browserbot.recursivelyDeleteCookie(cookieName, domain, path);
    } else {
        this.browserbot.deleteCookie(cookieName, domain, path);
    }
}

Selenium.prototype.doDeleteAllVisibleCookies = function() {
    var win = this.browserbot.getCurrentWindow();
    var doc = win.document;
    var cookieNames = this.browserbot.getAllCookieNames(doc);
    var domain = doc.domain;
    var path = win.location.pathname;
    for (var i = 0; i < cookieNames.length; i++) {
        this.browserbot.recursivelyDeleteCookie(cookieNames[i], domain, path, win);
    }
}

Selenium.prototype.doRunScript = function (script, varName) {

    window.postMessage({
        direction: "from-content-runscript",
        script: script
    }, "*");
    return this.browserbot.getRunScriptMessage().then(function (actualMessage) {
        if (actualMessage.status !== undefined) {
            if (actualMessage.status) {
                if (varName) {
                    return browser.runtime.sendMessage({ "storeStr": actualMessage.result, "storeVar": varName }).then(function() {
                        return { result: 'success' };
                    }).catch(function() {
                        return { result: 'success' };
                    });
                } else {
                    return Promise.resolve(true);
                }
            } else {
                return Promise.reject(actualMessage.result);
            }
        } else if (actualMessage != "No error!!!!") {
            return Promise.reject(actualMessage);
        } else {
            return Promise.resolve(true);
        }
    });
}

Selenium.prototype.doAddLocationStrategy = function(strategyName, functionDefinition) {
    if (!/^[a-zA-Z]+$/.test(strategyName)) {
        throw new SeleniumError("Invalid strategy name: " + strategyName);
    }
    var strategyFunction;
    try {
        strategyFunction = new Function("locator", "inDocument", "inWindow", functionDefinition);
    } catch (ex) {
        throw new SeleniumError("Error evaluating function definition: " + extractExceptionMessage(ex));
    }
    var safeStrategyFunction = function() {
        try {
            return strategyFunction.apply(this, arguments);
        } catch (ex) {
            throw new SeleniumError("Error executing strategy function " + strategyName + ": " + extractExceptionMessage(ex));
        }
    }
    this.browserbot.locationStrategies[strategyName] = safeStrategyFunction;
}

Selenium.prototype.doCaptureEntirePageScreenshot = function(filename, kwargs) {
    return browser.runtime.sendMessage({ 
        captureEntirePageScreenshot: true
    }).then(function(captureResponse) {
        return { 
            result: 'success',
            capturedScreenshot: captureResponse.image,
            capturedScreenshotTitle: request.target
        };
    });

    if (!browserVersion.isChrome &&
        !(browserVersion.isIE && !browserVersion.isHTA)) {
        throw new SeleniumError('captureEntirePageScreenshot is only ' + 'implemented for Firefox ("firefox" or "chrome", NOT ' + '"firefoxproxy") and IE non-HTA ("iexploreproxy", NOT "iexplore" ' + 'or "iehta"). The current browser isn\'t one of them!');
    }

    if (browserVersion.isIE) {
        function getFailureMessage(exceptionMessage) {
            var msg = 'Snapsie failed: ';
            if (exceptionMessage) {
                if (exceptionMessage ==
                    "Automation server can't create object") {
                    msg += 'Is it installed? Does it have permission to run ' + 'as an add-on? See http://snapsie.sourceforge.net/';
                } else {
                    msg += exceptionMessage;
                }
            } else {
                msg += 'Undocumented error';
            }
            return msg;
        }

        if (typeof(runOptions) != 'undefined' &&
            runOptions.isMultiWindowMode() == false) {
            try {
                new Snapsie().saveSnapshot(filename, 'selenium_myiframe');
            } catch (e) {
                throw new SeleniumError(getFailureMessage(e.message));
            }
        } else {
            if (!this.snapsieSrc) {
                var snapsieUrl = (this.browserbot.buttonWindow.location.href)
                    .replace(/(Test|Remote)Runner\.html/, 'lib/snapsie.js');
                var self = this;
                new Ajax.Request(snapsieUrl, {
                    method: 'get',
                    onSuccess: function(transport) {
                        self.snapsieSrc = transport.responseText;
                        self.doCaptureEntirePageScreenshot(filename, kwargs);
                    }
                });
                return;
            }

            filename = filename.replace(/\\/g, '\\\\');

            var doc = selenium.browserbot.getDocument();
            var script = doc.createElement('script');
            var scriptContent = this.snapsieSrc + 'try {' + '    new Snapsie().saveSnapshot("' + filename + '");' + '}' + 'catch (e) {' + '    document.getElementById("takeScreenshot").failure =' + '        e.message;' + '}';
            script.id = 'takeScreenshot';
            script.language = 'javascript';
            script.text = scriptContent;
            doc.body.appendChild(script);
            script.parentNode.removeChild(script);
            if (script.failure) {
                throw new SeleniumError(getFailureMessage(script.failure));
            }
        }
        return;
    }

    var grabber = {
        prepareCanvas: function(width, height) {
            var styleWidth = width + 'px';
            var styleHeight = height + 'px';

            var grabCanvas = document.getElementById('screenshot_canvas');
            if (!grabCanvas) {
                var ns = 'http://www.w3.org/1999/xhtml';
                grabCanvas = document.createElementNS(ns, 'html:canvas');
                grabCanvas.id = 'screenshot_canvas';
                grabCanvas.style.display = 'none';
                document.documentElement.appendChild(grabCanvas);
            }

            grabCanvas.width = width;
            grabCanvas.style.width = styleWidth;
            grabCanvas.style.maxWidth = styleWidth;
            grabCanvas.height = height;
            grabCanvas.style.height = styleHeight;
            grabCanvas.style.maxHeight = styleHeight;

            return grabCanvas;
        },

        prepareContext: function(canvas, box) {
            var context = canvas.getContext('2d');
            context.clearRect(box.x, box.y, box.width, box.height);
            context.save();
            return context;
        }
    };

    var SGNsUtils = {
        dataUrlToBinaryInputStream: function(dataUrl) {
            var nsIoService = Components.classes["@mozilla.org/network/io-service;1"]
                .getService(Components.interfaces.nsIIOService);
            var channel = nsIoService
                .newChannelFromURI(nsIoService.newURI(dataUrl, null, null));
            var binaryInputStream = Components.classes["@mozilla.org/binaryinputstream;1"]
                .createInstance(Components.interfaces.nsIBinaryInputStream);

            binaryInputStream.setInputStream(channel.open());
            return binaryInputStream;
        },

        newFileOutputStream: function(nsFile) {
            var writeFlag = 0x02; 
            var createFlag = 0x08; 
            var truncateFlag = 0x20;
            var fileOutputStream = Components.classes["@mozilla.org/network/file-output-stream;1"]
                .createInstance(Components.interfaces.nsIFileOutputStream);

            
            fileOutputStream.init(nsFile,
                writeFlag | createFlag | truncateFlag,
                0664,
                null);
            return fileOutputStream;
        },

        writeBinaryInputStreamToFileOutputStream: function(binaryInputStream, fileOutputStream) {
            var numBytes = binaryInputStream.available();
            var bytes = binaryInputStream.readBytes(numBytes);
            fileOutputStream.write(bytes, numBytes);
        }
    };

    var window = this.browserbot.getCurrentWindow();
    var doc = window.document.documentElement;
    var body = window.document.body;
    var box = {
        x: 0,
        y: 0,
        width: Math.max(doc.scrollWidth, body.scrollWidth),
        height: Math.max(doc.scrollHeight, body.scrollHeight)
    };

    var limit = 32766;
    if (box.width > limit) {
        box.width = limit;
    }
    if (box.height > limit) {
        box.height = limit;
    }

    var originalBackground = doc.style.background;

    if (kwargs) {
        var args = parse_kwargs(kwargs);
        if (args.background) {
            doc.style.background = args.background;
        }
    }


    var format = 'png';
    var canvas = grabber.prepareCanvas(box.width, box.height);
    var context = grabber.prepareContext(canvas, box);
    context.drawWindow(window, box.x, box.y, box.width, box.height,
        'rgb(0, 0, 0)');
    context.restore();
    var dataUrl = canvas.toDataURL("image/" + format);
    doc.style.background = originalBackground;
    var nsFile = Components.classes["@mozilla.org/file/local;1"]
        .createInstance(Components.interfaces.nsILocalFile);
    try {
        nsFile.initWithPath(filename);
    } catch (e) {
        if (/NS_ERROR_FILE_UNRECOGNIZED_PATH/.test(e.message)) {
            if (filename.indexOf('/') != -1) {
                filename = filename.replace(/\//g, '\\');
            } else {
                filename = filename.replace(/\\/g, '/');
            }
            nsFile.initWithPath(filename);
        } else {
            throw e;
        }
    }
    var binaryInputStream = SGNsUtils.dataUrlToBinaryInputStream(dataUrl);
    var fileOutputStream = SGNsUtils.newFileOutputStream(nsFile);
    SGNsUtils.writeBinaryInputStreamToFileOutputStream(binaryInputStream,
        fileOutputStream);
    fileOutputStream.close();
};

Selenium.prototype.doRollup = function(rollupName, kwargs) {
    var loop = currentTest || htmlTestRunner.currentTest;
    var backupManager = {
        backup: function() {
            for (var item in this.data) {
                this.data[item] = loop[item];
            }
        },
        restore: function() {
            for (var item in this.data) {
                loop[item] = this.data[item];
            }
        },
        data: {
            requiresCallBack: null,
            commandStarted: null,
            nextCommand: null,
            commandComplete: null,
            commandError: null,
            pendingRollupCommands: null,
            rollupFailed: null,
            rollupFailedMessage: null
        }
    };

    var rule = RollupManager.getInstance().getRollupRule(rollupName);
    var expandedCommands = rule.getExpandedCommands(kwargs);

    try {
        backupManager.backup();
        loop.requiresCallBack = false;
        loop.commandStarted = function() {};
        loop.nextCommand = function() {
            if (this.pendingRollupCommands.length == 0) {
                return null;
            }
            var command = this.pendingRollupCommands.shift();
            return command;
        };
        loop.commandComplete = function(result) {
            if (result.failed) {
                this.rollupFailed = true;
                this.rollupFailureMessages.push(result.failureMessage);
            }

            if (this.pendingRollupCommands.length == 0) {
                result = {
                    failed: this.rollupFailed,
                    failureMessage: this.rollupFailureMessages.join('; ')
                };
                backupManager.restore();
                this.commandComplete(result);
            }
        };
        loop.commandError = function(errorMessage) {
            backupManager.restore();
            this.commandError(errorMessage);
        };

        loop.pendingRollupCommands = expandedCommands;
        loop.rollupFailed = false;
        loop.rollupFailureMessages = [];
    } catch (e) {
        backupManager.restore();
    }
};

Selenium.prototype.doAddScript = function(scriptContent, scriptTagId) {
    if (scriptTagId && document.getElementById(scriptTagId)) {
        var msg = "Element with id '" + scriptTagId + "' already exists!";
        throw new SeleniumError(msg);
    }

    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');

    script.type = 'text/javascript';

    if (scriptTagId) {
        script.id = scriptTagId;
    }
    scriptContent = scriptContent
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&');

    script.text = scriptContent;
    head.appendChild(script);
};

Selenium.prototype.doRemoveScript = function(scriptTagId) {
    var script = document.getElementById(scriptTagId);

    if (script && getTagName(script) == 'script') {
        script.parentNode.removeChild(script);
    }
};

Selenium.prototype.doUseXpathLibrary = function(libraryName) {
    if (!this.browserbot.getXPathEngine(libraryName)) {
        return;
    }

    this.browserbot.setXPathEngine(libraryName);
};

Selenium.prototype.doEditContent = function(locator, value) {
    var element = this.browserbot.findElement(locator);
    var editable = element.contentEditable;

    if (editable == "true") {
        element.innerHTML = escapeHTML(value);
    } else {
        throw new SeleniumError("The value of contentEditable attribute of this element is not true.");
    }
};
Selenium.prototype.doChooseCancelOnNextPrompt = function() {
    return this.browserbot.cancelNextPrompt();
};

Selenium.prototype.doAnswerOnNextPrompt = function (answer) {
    return this.browserbot.setNextPromptResult(answer);
};

Selenium.prototype.doAssertPrompt = function (message) {
    return this.browserbot.getPromptMessage().then(function(actualMessage) {
               if (message != actualMessage)
                    return Promise.reject("Prompt message doesn't match actual message");
               else
                    return Promise.resolve(true);
           });
};

Selenium.prototype.doAssertAlert = function(message) {
    return this.browserbot.getAlertMessage().then(function(actualMessage) {
               if (message != actualMessage)
                   return Promise.reject("Alert message doesn't match actual message");
               else
                   return Promise.resolve(true);
           });
};

Selenium.prototype.doChooseCancelOnNextConfirmation = function() {
    return this.browserbot.setNextConfirmationResult(false);
};

Selenium.prototype.doChooseOkOnNextConfirmation = function (answer) {
    return this.browserbot.setNextConfirmationResult(true);
};

Selenium.prototype.doAssertConfirmation = function(value) {
    return this.browserbot.getConfirmationMessage().then(function(actualMessage) {
               if (value != actualMessage)
                    return Promise.reject("Confirmation message doesn't match actual message");
               else
                    return Promise.resolve(true);
           });
};

Selenium.prototype.doShowElement = function(locator){
    try{
        var element = this.browserbot.findElement(locator, window);
        var div = document.createElement("div");
        var r = element.getBoundingClientRect();
        if (r.left >= 0 && r.top >= 0 && r.width > 0 && r.height > 0) {
            var style = "pointer-events: none; position: absolute; box-shadow: 0 0 0 1px black; outline: 1px dashed white; outline-offset: -1px; background-color: rgba(250,250,128,0.4); z-index: 100;";
            var pos = "top:" + (r.top + window.scrollY) + "px; left:" + (r.left + window.scrollX) + "px; width:" + r.width + "px; height:" + r.height + "px;";
            div.setAttribute("style", style + pos);
        }
        document.body.insertBefore(div, document.body.firstChild);
        setTimeout(function() {
            document.body.removeChild(div);
        }, 500);
        return true;
    } catch (e) {
        return false;
    }
};


/* Option factory */
function OptionLocatorFactory() {}

OptionLocatorFactory.prototype.fromLocatorString = function(locatorString) {
    var locatorType = 'label';
    var locatorValue = locatorString;
    var result = locatorString.match(/^([a-zA-Z]+)=(.*)/);
    if (result) {
        locatorType = result[1];
        locatorValue = result[2];
    }
    if (this.optionLocators == undefined) {
        this.registerOptionLocators();
    }
    if (this.optionLocators[locatorType]) {
        return new this.optionLocators[locatorType](locatorValue);
    }
    throw new SeleniumError("Unknown option locator type: " + locatorType);
};

OptionLocatorFactory.prototype.registerOptionLocators = function() {
    this.optionLocators = {};
    for (var functionName in this) {
        var result = /OptionLocatorBy([A-Z].+)$/.exec(functionName);
        if (result != null) {
            var locatorName = result[1].lcfirst();
            this.optionLocators[locatorName] = this[functionName];
        }
    }
};


OptionLocatorFactory.prototype.OptionLocatorByLabel = function(label) {
    this.label = label;
    this.labelMatcher = new PatternMatcher(this.label);
    this.findOption = function(element) {
        for (var i = 0; i < element.options.length; i++) {
            if (this.labelMatcher.matches(element.options[i].text)) {
                return element.options[i];
            }
        }
        throw new SeleniumError("Option with label '" + this.label + "' not found");
    };

    this.assertSelected = function(element) {
        var selectedLabel = element.options[element.selectedIndex].text;
        Assert.matches(this.label, selectedLabel)
    };
};

OptionLocatorFactory.prototype.OptionLocatorByValue = function(value) {
    this.value = value;
    this.valueMatcher = new PatternMatcher(this.value);
    this.findOption = function(element) {
        for (var i = 0; i < element.options.length; i++) {
            if (this.valueMatcher.matches(element.options[i].value)) {
                return element.options[i];
            }
        }
        throw new SeleniumError("Option with value '" + this.value + "' not found");
    };

    this.assertSelected = function(element) {
        var selectedValue = element.options[element.selectedIndex].value;
        Assert.matches(this.value, selectedValue)
    };
};

OptionLocatorFactory.prototype.OptionLocatorByIndex = function(index) {
    this.index = Number(index);
    if (isNaN(this.index) || this.index < 0) {
        throw new SeleniumError("Illegal Index: " + index);
    }

    this.findOption = function(element) {
        if (element.options.length <= this.index) {
            throw new SeleniumError("Index out of range.  Only " + element.options.length + " options available");
        }
        return element.options[this.index];
    };

    this.assertSelected = function(element) {
        Assert.equals(this.index, element.selectedIndex);
    };
};

OptionLocatorFactory.prototype.OptionLocatorById = function(id) {
    this.id = id;
    this.idMatcher = new PatternMatcher(this.id);
    this.findOption = function(element) {
        for (var i = 0; i < element.options.length; i++) {
            if (this.idMatcher.matches(element.options[i].id)) {
                return element.options[i];
            }
        }
        throw new SeleniumError("Option with id '" + this.id + "' not found");
    };

    this.assertSelected = function(element) {
        var selectedId = element.options[element.selectedIndex].id;
        Assert.matches(this.id, selectedId)
    };
};