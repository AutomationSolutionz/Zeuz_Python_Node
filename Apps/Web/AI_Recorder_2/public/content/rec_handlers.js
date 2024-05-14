/* Recorder handlers functions start */
browserAppData = chrome || browser;

var typeLock = 0;
var typeTarget;

var focusTarget = null;
var focusValue = null;
var tempValue = null;
var preventType = false;

var preventClick = false;
var enterTarget = null;
var enterValue = null;
var tabCheck = null;

function isRangeInput(node) {
    if (!node || node.nodeName !== 'INPUT')
        return false;
    return node.type.toLowerCase() === 'range';
}
function asCheckbox(node) {
    if (!node || node.nodeName !== 'INPUT')
        return null;
    return ['checkbox', 'radio'].includes(node.type) ? inputElement : null;
}
class RecordActionTool {
    onClick(event) {
        // in webkit, sliding a range element may trigger a click event with a different target if the mouse is released outside the element bounding box.
        // So we check the hovered element instead, and if it is a range input, we skip click handling
        if (isRangeInput(event.target))
            return;
        if (this._shouldIgnoreMouseEvent(event))
            return;

        const checkbox = asCheckbox(event.target);
        if (checkbox) {
            // Interestingly, inputElement.checked is reversed inside this event handler.
            this._performAction({
                name: checkbox.checked ? 'check' : 'uncheck',
                selector: selector,
                signals: [],
            });
            return;
        }

        this._performAction({
            name: 'click',
            selector: selector,
            position: positionForEvent(event),
            signals: [],
            button: buttonForEvent(event),
            modifiers: modifiersForEvent(event),
            clickCount: event.detail
        });
    }

    onFocus(event) {
        this._onFocus(true);
    }

    onInput(event) {
        const target = event.target;

        if (target.nodeName === 'INPUT' && target.type.toLowerCase() === 'file') {
            this.delegate.recordAction?.({
                name: 'setInputFiles',
                selector: selector,
                signals: [],
                files: [...(target.files || [])].map(file => file.name),
            });
            return;
        }

        if (isRangeInput(target)) {
            this.delegate.recordAction?.({
                name: 'fill',
                // must use hoveredModel instead of activeModel for it to work in webkit
                selector: selector,
                signals: [],
                text: target.value,
            });
            return;
        }

        if (['INPUT', 'TEXTAREA'].includes(target.nodeName) || target.isContentEditable) {
            if (target.nodeName === 'INPUT' && ['checkbox', 'radio'].includes(target.type.toLowerCase())) {
                // Checkbox is handled in click, we can't let input trigger on checkbox - that would mean we dispatched click events while recording.
                return;
            }
            this.delegate.recordAction?.({
                name: 'fill',
                selector: selector,
                signals: [],
                text: target.isContentEditable ? target.innerText : target.value,
            });
        }

        if (target.nodeName === 'SELECT') {
            const selectElement = target;
            this._performAction({
                name: 'select',
                selector: selector,
                options: [...selectElement.selectedOptions].map(option => option.value),
                signals: []
            });
        }
    }

    onKeyDown(event) {
        if (!this._shouldGenerateKeyPressFor(event))
            return;
        // Similarly to click, trigger checkbox on key event, not input.
        if (event.key === ' ') {
            const checkbox = asCheckbox(event.target);
            if (checkbox) {
                this._performAction({
                    name: checkbox.checked ? 'uncheck' : 'check',
                    selector: selector,
                    signals: [],
                });
                return;
            }
        }

        this._performAction({
            name: 'press',
            selector: selector,
            signals: [],
            key: event.key,
            modifiers: modifiersForEvent(event),
        });
    }

    onKeyUp(event) {
        if (!this._shouldGenerateKeyPressFor(event))
            return;
    }

    _shouldIgnoreMouseEvent(event) {
        const target = event.target;
        const nodeName = target.nodeName;
        if (nodeName === 'SELECT' || nodeName === 'OPTION')
            return true;
        if (nodeName === 'INPUT' && ['date', 'range'].includes(target.type))
            return true;
        return false;
    }

    _shouldGenerateKeyPressFor(event) {
        // Enter aka. new line is handled in input event.
        if (event.key === 'Enter' && (event.target.nodeName === 'TEXTAREA' || event.target.isContentEditable))
            return false;
        // Backspace, Delete, AltGraph are changing input, will handle it there.
        if (['Backspace', 'Delete', 'AltGraph'].includes(event.key))
            return false;
        // Ignore the QWERTZ shortcut for creating a at sign on MacOS
        if (event.key === '@' && event.code === 'KeyL')
            return false;
        // Allow and ignore common used shortcut for pasting.
        if (navigator.platform.includes('Mac')) {
            if (event.key === 'v' && event.metaKey)
                return false;
        } else {
            if (event.key === 'v' && event.ctrlKey)
                return false;
            if (event.key === 'Insert' && event.shiftKey)
                return false;
        }
        if (['Shift', 'Control', 'Meta', 'Alt', 'Process'].includes(event.key))
            return false;
        const hasModifier = event.ctrlKey || event.altKey || event.metaKey;
        if (event.key.length === 1 && !hasModifier)
            return !!asCheckbox(event.target);
        return true;
    }

}


function print_event(event) {
    var print = true;
    let ignore = ['mouseover', 'mouseout', 'focus', 'focusout', 'blur', 'DOMNodeInserted', 'scroll']
    if (print && !ignore.includes(event.type))
        console.log(event.type, 'event', event)
}

Recorder.eventHandlers = {};
Recorder.addEventHandler = function (handlerName, event_name, handler, options) {
    handler.handlerName = handlerName;
    if (!options) options = false;
    let key = options ? ('C_' + event_name) : event_name;
    if (!this.eventHandlers[key]) {
        this.eventHandlers[key] = [];
    }
    this.eventHandlers[key].push(handler);
}

/* Set recorder input type */
Recorder.inputTypes = ["text", "password", "datetime", "time", "datetime-local", "date", "month", "week", "file", "number", "range", "email", "url", "search", "tel", "color"];


Recorder.addEventHandler('type', 'input', function (event) {
    print_event(event)
    typeTarget = event.target;
});

/* Recorder on change event */
Recorder.addEventHandler('type', 'change', function (event) {
    print_event(event)
    if (event.target.tagName && !preventType && typeLock == 0 && (typeLock = 1)) {
        var tagName = event.target.tagName.toLowerCase();
        var type = event.target.type;
        if ('input' == tagName && Recorder.inputTypes.indexOf(type) >= 0) {
            if (event.target.value.length > 0) {
                this.record("type", this.locatorBuilders.buildAll(event.target), event.target.value);
                if (enterTarget != null) {
                    var tempTarget = event.target.parentElement;
                    var formChk = tempTarget.tagName.toLowerCase();
                    while (formChk != 'form' && formChk != 'body') {
                        tempTarget = tempTarget.parentElement;
                        formChk = tempTarget.tagName.toLowerCase();
                    }
                    if (formChk == 'form' && (tempTarget.hasAttribute("id") || tempTarget.hasAttribute("name")) && (!tempTarget.hasAttribute("onsubmit"))) {
                        if (tempTarget.hasAttribute("id"))
                            this.record("submit", [
                                ["id=" + tempTarget.id, "id"]
                            ], "");
                        else if (tempTarget.hasAttribute("name"))
                            this.record("submit", [
                                ["name=" + tempTarget.name, "name"]
                            ], "");
                    } else
                        this.record("sendKeys", this.locatorBuilders.buildAll(enterTarget), "${KEY_ENTER}");
                    enterTarget = null;
                }
            } else {
                this.record("type", this.locatorBuilders.buildAll(event.target), event.target.value);
            }
        } else if ('textarea' == tagName) {
            this.record("type", this.locatorBuilders.buildAll(event.target), event.target.value);
        }
    }
    typeLock = 0;
});

/* Recorder Click event */
var preventClickTwice = false;
var select_xpath
Recorder.addEventHandler('clickAt', 'click', function (event) {
    print_event(event)
    var xpaths = this.locatorBuilders.buildAll(event.target);
    if ('select' == event.target.nodeName.toLowerCase()) select_xpath = xpaths
    // console.log("xpaths", xpaths);
    if (event.button == 0 && !preventClick && event.isTrusted) {
        if (!preventClickTwice) {
            var top = event.pageY,
                left = event.pageX;
            var element = event.target;
            do {
                top -= element.offsetTop;
                left -= element.offsetLeft;
                element = element.offsetParent;
            } while (element);
            this.record("click", xpaths, '');
            preventClickTwice = true;
        }
        setTimeout(function () { preventClickTwice = false; }, 30);
    }
}, true);

/* Recorder Double click event */
Recorder.addEventHandler('doubleClickAt', 'dblclick', function (event) {
    print_event(event)
    var top = event.pageY,
        left = event.pageX;
    var element = event.target;
    do {
        top -= element.offsetTop;
        left -= element.offsetLeft;
        element = element.offsetParent;
    } while (element);
    this.record("double click", this.locatorBuilders.buildAll(event.target), '');
}, true);


var inp = document.getElementsByTagName("input");
for (var i = 0; i < inp.length; i++) {
    if (Recorder.inputTypes.indexOf(inp[i].type) >= 0) {
        inp[i].addEventListener("focus", function (event) {
            focusTarget = event.target;
            focusValue = focusTarget.value;
            tempValue = focusValue;
            preventType = false;
        });
        inp[i].addEventListener("blur", function (event) {
            focusTarget = null;
            focusValue = null;
            tempValue = null;
        });
    }
}

/* Recorder key down event */
Recorder.addEventHandler('sendKeys', 'keydown', function (event) {
    print_event(event)
    if (event.target.tagName) {
        var key = event.keyCode;
        var tagName = event.target.tagName.toLowerCase();
        var type = event.target.type;
        if (tagName == 'input' && Recorder.inputTypes.indexOf(type) >= 0) {
            if (key == 13) { // 13 means Enter button
                enterTarget = event.target;
                enterValue = enterTarget.value;
                var tempTarget = event.target.parentElement;
                var formChk = tempTarget.tagName.toLowerCase();
                if (tempValue == enterTarget.value && tabCheck == enterTarget) {
                    this.record("sendKeys", this.locatorBuilders.buildAll(enterTarget), "${KEY_ENTER}");
                    enterTarget = null;
                    preventType = true;
                } else if (focusValue == enterTarget.value) {
                    while (formChk != 'form' && formChk != 'body') {
                        tempTarget = tempTarget.parentElement;
                        formChk = tempTarget.tagName.toLowerCase();
                    }
                    if (formChk == 'form' && (tempTarget.hasAttribute("id") || tempTarget.hasAttribute("name")) && (!tempTarget.hasAttribute("onsubmit"))) {
                        if (tempTarget.hasAttribute("id"))
                            this.record("submit", [["id=" + tempTarget.id]], "");
                        else if (tempTarget.hasAttribute("name"))
                            this.record("submit", [["name=" + tempTarget.name]], "");
                    } else
                        this.record("sendKeys", this.locatorBuilders.buildAll(enterTarget), "${KEY_ENTER}");
                    enterTarget = null;
                }
                if (typeTarget.tagName && !preventType && (typeLock = 1)) {
                    var tagName = typeTarget.tagName.toLowerCase();
                    var type = typeTarget.type;
                    if ('input' == tagName && Recorder.inputTypes.indexOf(type) >= 0) {
                        if (typeTarget.value.length > 0) {
                            this.record("type", this.locatorBuilders.buildAll(typeTarget), typeTarget.value);
                            if (enterTarget != null) {
                                var tempTarget = typeTarget.parentElement;
                                var formChk = tempTarget.tagName.toLowerCase();
                                while (formChk != 'form' && formChk != 'body') {
                                    tempTarget = tempTarget.parentElement;
                                    formChk = tempTarget.tagName.toLowerCase();
                                }
                                if (formChk == 'form' && (tempTarget.hasAttribute("id") || tempTarget.hasAttribute("name")) && (!tempTarget.hasAttribute("onsubmit"))) {
                                    if (tempTarget.hasAttribute("id"))
                                        this.record("submit", [
                                            ["id=" + tempTarget.id, "id"]
                                        ], "");
                                    else if (tempTarget.hasAttribute("name"))
                                        this.record("submit", [
                                            ["name=" + tempTarget.name, "name"]
                                        ], "");
                                } else
                                    this.record("sendKeys", this.locatorBuilders.buildAll(enterTarget), "${KEY_ENTER}");
                                enterTarget = null;
                            }
                        } else {
                            this.record("type", this.locatorBuilders.buildAll(typeTarget), typeTarget.value);
                        }
                    } else if ('textarea' == tagName) {
                        this.record("type", this.locatorBuilders.buildAll(typeTarget), typeTarget.value);
                    }
                }
                preventClick = true;
                setTimeout(function () {
                    preventClick = false;
                }, 500);
                setTimeout(function () {
                    if (enterValue != event.target.value) enterTarget = null;
                }, 50);
            }

            var tempbool = false;
            if ((key == 38 || key == 40) && event.target.value != '') {
                if (focusTarget != null && focusTarget.value != tempValue) {
                    tempbool = true;
                    tempValue = focusTarget.value;
                }
                if (tempbool) {
                    this.record("type", this.locatorBuilders.buildAll(event.target), tempValue);
                }

                setTimeout(function () {
                    tempValue = focusTarget.value;
                }, 250);

                if (key == 38) this.record("sendKeys", this.locatorBuilders.buildAll(event.target), "${KEY_UP}");
                else this.record("sendKeys", this.locatorBuilders.buildAll(event.target), "${KEY_DOWN}");
                tabCheck = event.target;
            }
            if (key == 9) {
                if (tabCheck == event.target) {
                    this.record("sendKeys", this.locatorBuilders.buildAll(event.target), "${KEY_TAB}");
                    preventType = true;
                }
            }
        }
    }
}, true);

/* Recorder mouse up event */
Recorder.addEventHandler('dragAndDrop', 'mouseup', function (event) {
    print_event(event)
    clearTimeout(this.selectMouseup);
    if (this.selectMousedown) {
        var x = event.clientX - this.selectMousedown.clientX;
        var y = event.clientY - this.selectMousedown.clientY;

        function getSelectionText() {
            var text = "";
            var activeEl = window.document.activeElement;
            var activeElTagName = activeEl ? activeEl.tagName.toLowerCase() : null;
            if (activeElTagName == "textarea" || activeElTagName == "input") {
                text = activeEl.value.slice(activeEl.selectionStart, activeEl.selectionEnd);
            } else if (window.getSelection) {
                text = window.getSelection().toString();
            }
            return text.trim();
        }

        if (this.selectMousedown && event.button === 0 && (x + y) && (event.clientX < window.document.documentElement.clientWidth && event.clientY < window.document.documentElement.clientHeight) && getSelectionText() === '') {
            var sourceRelateX = this.selectMousedown.pageX - this.selectMousedown.target.getBoundingClientRect().left - window.scrollX;
            var sourceRelateY = this.selectMousedown.pageY - this.selectMousedown.target.getBoundingClientRect().top - window.scrollY;
            var targetRelateX, targetRelateY;
            if (!!this.mouseoverQ.length && this.mouseoverQ[1].relatedTarget == this.mouseoverQ[0].target && this.mouseoverQ[0].target == event.target) {
                targetRelateX = event.pageX - this.mouseoverQ[1].target.getBoundingClientRect().left - window.scrollX;
                targetRelateY = event.pageY - this.mouseoverQ[1].target.getBoundingClientRect().top - window.scrollY;
            } else {
                targetRelateX = event.pageX - event.target.getBoundingClientRect().left - window.scrollX;
                targetRelateY = event.pageY - event.target.getBoundingClientRect().top - window.scrollY;
            }
        }
    } else {
        if (this.mousedown) {
            delete this.clickLocator;
            delete this.mouseup;
            var x = event.clientX - this.mousedown.clientX;
            var y = event.clientY - this.mousedown.clientY;

            if (this.mousedown && this.mousedown.target !== event.target && !(x + y)) {
            } else if (this.mousedown && this.mousedown.target === event.target) {
                var self = this;
                var target = this.locatorBuilders.buildAll(this.mousedown.target);
            }
        }
    }
    delete this.mousedown;
    delete this.selectMousedown;
    delete this.mouseoverQ;
}, true);

/* Recorder mouse down event */
Recorder.addEventHandler('dragAndDrop', 'mousedown', function (event) {
    print_event(event)
    var self = this;
    if (event.clientX < window.document.documentElement.clientWidth && event.clientY < window.document.documentElement.clientHeight) {
        this.mousedown = event;
        this.mouseup = setTimeout(function () {
            delete self.mousedown;
        }.bind(this), 200);

        this.selectMouseup = setTimeout(function () {
            self.selectMousedown = event;
        }.bind(this), 200);
    }
    this.mouseoverQ = [];

    if (event.target.nodeName) {
        var tagName = event.target.nodeName.toLowerCase();
        if ('option' == tagName) {
            var parent = event.target.parentNode;
            if (parent.multiple) {
                var options = parent.options;
                for (var i = 0; i < options.length; i++) {
                    options[i]._wasSelected = options[i].selected;
                }
            }
        }
    }
}, true);

/* Recorder Drag start event */
Recorder.addEventHandler('dragAndDropToObject', 'dragstart', function (event) {
    print_event(event)
    var self = this;
    this.dropLocator = setTimeout(function () {
        self.dragstartLocator = event;
    }.bind(this), 200);
}, true);

/* Recorder Drop event */
Recorder.addEventHandler('dragAndDropToObject', 'drop', function (event) {
    clearTimeout(this.dropLocator);
    if (this.dragstartLocator && event.button == 0 && this.dragstartLocator.target !== event.target) {
        // this.record("dragAndDropToObject", this.locatorBuilders.buildAll(this.dragstartLocator.target), this.locatorBuilders.build(event.target));
    }
    delete this.dragstartLocator;
    delete this.selectMousedown;
}, true);

/* Recorder Scroll event */
var prevTimeOut = null;
Recorder.addEventHandler('runScript', 'scroll', function (event) {
    print_event(event)
    if (pageLoaded === true) {
        var self = this;
        this.scrollDetector = event.target;
        clearTimeout(prevTimeOut);
        prevTimeOut = setTimeout(function () {
            delete self.scrollDetector;
        }.bind(self), 500);
    }
}, true);

/* Recorder mouse out event */
Recorder.addEventHandler('mouseOut', 'mouseout', function (event) {
    print_event(event)
    if (this.mouseoutLocator !== null && event.target === this.mouseoutLocator) {
    }
    delete this.mouseoutLocator;
}, true);


/* Recorder Mouse over event */
var nowNode = 0;
Recorder.addEventHandler('mouseOver', 'mouseover', function (event) {
    print_event(event)
    if (window.document.documentElement)
        nowNode = window.document.documentElement.getElementsByTagName('*').length;
    var self = this;
    if (pageLoaded === true) {
        var clickable = this.findClickableElement(event.target);
        if (clickable) {
            this.nodeInsertedLocator = event.target;
            setTimeout(function () {
                delete self.nodeInsertedLocator;
            }.bind(self), 500);

            this.nodeAttrChange = this.locatorBuilders.buildAll(event.target);
            this.nodeAttrChangeTimeout = setTimeout(function () {
                delete self.nodeAttrChange;
            }.bind(self), 10);
        }
        if (this.mouseoverQ) {
            if (this.mouseoverQ.length >= 3)
                this.mouseoverQ.shift();
            this.mouseoverQ.push(event);
        }
    }
}, true);

Recorder.addEventHandler('mouseOver', 'DOMNodeInserted', function (event) {
    print_event(event)
    if (pageLoaded === true && window.document.documentElement.getElementsByTagName('*').length > nowNode) {
        var self = this;
        if (this.scrollDetector) {
            pageLoaded = false;
            setTimeout(function () {
                pageLoaded = true;
            }.bind(self), 550);
            delete this.scrollDetector;
            delete this.nodeInsertedLocator;
        }
        if (this.nodeInsertedLocator) {
            this.mouseoutLocator = this.nodeInsertedLocator;
            delete this.nodeInsertedLocator;
            delete this.mouseoverLocator;
        }
    }
}, true);

var readyTimeOut = null;
var pageLoaded = true;
Recorder.addEventHandler('checkPageLoaded', 'readystatechange', function (event) {
    print_event(event)
    var self = this;
    if (window.document.readyState === 'loading') {
        pageLoaded = false;
    } else {
        pageLoaded = false;
        clearTimeout(readyTimeOut);
        readyTimeOut = setTimeout(function () {
            pageLoaded = true;
        }.bind(self), 1500);
    }
}, true);

Recorder.addEventHandler('contextMenu', 'contextmenu', function (event) {
    print_event(event)
    var myPort = browserAppData.runtime.connect();
    var tmpText = this.locatorBuilders.buildAll(event.target);
    var tmpVal = getText(event.target);
    var tmpTitle = normalizeSpaces(event.target.ownerDocument.title);
    var self = this;
    myPort.onMessage.addListener(function portListener(m) {
        if (m.cmd.includes("Text")) {
            self.record(m.cmd, tmpText, tmpVal);
        } else if (m.cmd.includes("Title")) {
            self.record(m.cmd, [[tmpTitle]], '');
        } else if (m.cmd.includes("Value")) {
            self.record(m.cmd, tmpText, getInputValue(event.target));
        }
        else {
            self.record(m.cmd, tmpText, tmpVal);
        }
        myPort.onMessage.removeListener(portListener);
    });
}, true);

/* Recorder focus event */
var getEle;
var checkFocus = 0;
Recorder.addEventHandler('editContent', 'focus', function (event) {
    print_event(event)
    var editable = event.target.contentEditable;
    if (editable == 'true') {
        getEle = event.target;
        contentTest = getEle.innerHTML;
        checkFocus = 1;
    }
}, true);

/* Recorder blur event */
Recorder.addEventHandler('editContent', 'blur', function (event) {
    print_event(event)
    if (checkFocus == 1) {
        if (event.target == getEle) {
            if (getEle.innerHTML != contentTest) {  // Understand this before calling record()
                // this.record("editContent", this.locatorBuilders.buildAll(event.target), getEle.innerHTML);
            }
            checkFocus = 0;
        }
    }
}, true);

browserAppData.runtime.sendMessage({
    attachRecorderRequest: true
}).catch(function (reason) {
});

/* on focus */
Recorder.addEventHandler('select', 'focus', function (event) {
    print_event(event)
    if (event.target.nodeName) {
        var tagName = event.target.nodeName.toLowerCase();
        if ('select' == tagName && event.target.multiple) {
            var options = event.target.options;
            for (var i = 0; i < options.length; i++) {
                if (options[i]._wasSelected == null) {
                    options[i]._wasSelected = options[i].selected;
                }
            }
        }
    }
}, true);

/* on focusout */
var change_event_invoked = false;
Recorder.addEventHandler('select_focusout', 'focusout', function (event) {
    print_event(event)
    // if (event.target.tagName.toLowerCase() == 'select') console.log('select focusout', event);
    if (event.target.tagName.toLowerCase() !== 'select') return;
    setTimeout(() => {
        if (change_event_invoked) return;
        var option = event.target.options[event.target.selectedIndex];
        // console.log("event.target", event.target);
        var xpaths = this.locatorBuilders.buildAll(event.target);
        if (xpaths.length == 0) xpaths = select_xpath;
        // console.log("xpaths", xpaths);
        this.record("select", xpaths, this.getOptionLocator(option));
        // console.log("option from select focusout event", option);
        change_event_invoked = false;
    }, 250)
}, true);

/* change */
Recorder.addEventHandler('select_change', 'change', function (event) {
    print_event(event)
    if (event.target.tagName) {
        var tagName = event.target.tagName.toLowerCase();
        if ('select' == tagName) {
            console.log("select change event", event);
            if (!event.target.multiple) {
                var option = event.target.options[event.target.selectedIndex];
                this.record("select", this.locatorBuilders.buildAll(event.target), this.getOptionLocator(option));
                change_event_invoked = true;
                setTimeout(() => {
                    change_event_invoked = false;
                }, 500)
            } else {    // Understand this else block, what is its purpose, then call record() function
                var options = event.target.options;
                for (var i = 0; i < options.length; i++) {
                    if (options[i]._wasSelected == null) { }
                    if (options[i]._wasSelected != options[i].selected) {
                        var value = this.getOptionLocator(options[i]);
                        if (options[i].selected) {
                            // this.record("addSelection", this.locatorBuilders.buildAll(event.target), value);
                        } else {
                            // this.record("removeSelection", this.locatorBuilders.buildAll(event.target), value);
                        }
                        options[i]._wasSelected = options[i].selected;
                    }
                }
            }
        }
    }
});


// This function wont be needed, if Click action isused instead of select-action
Recorder.prototype.getOptionLocator = function (option) {
    var label = option.text.replace(/^ *(.*?) *$/, "$1");
    if (label.match(/\xA0/)) {
        return "label=regexp:" + label.replace(/[\(\)\[\]\\\^\$\*\+\?\.\|\{\}]/g, function (str) {
            return '\\' + str
        })
            .replace(/\s+/g, function (str) {
                if (str.match(/\xA0/)) {
                    if (str.length > 1) {
                        return "\\s+";
                    } else {
                        return "\\s";
                    }
                } else {
                    return str;
                }
            });
    } else {
        return "label=" + label;
    }
};

Recorder.prototype.findClickableElement = function (e) {
    if (!e.tagName) return null;
    var tagName = e.tagName.toLowerCase();
    var type = e.type;
    if (e.hasAttribute("onclick") || e.hasAttribute("href") || tagName == "button" ||
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
