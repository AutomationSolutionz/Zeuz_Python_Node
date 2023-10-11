/* ZeuZ Start the recording function */
class Recorder {

    /* exq initial time */
    constructor(window) {
        this.window = window;
        this.attached = false;
        this.locatorBuilders = new LocatorBuilders(window);
        this.frameLocation = this.getFrameLocation();
        BrowserAppData.runtime.sendMessage({
            frameLocation: this.frameLocation
        }).catch(function(reason) {
        });
    }

    /* Parse the key */
    parse_the_event_key(event_key) {
        if (event_key.match(/^C_/)) {
            return { event_name: event_key.substring(2), capture: true };
        } else {
            return { event_name: event_key, capture: false };
        }
    }

    /* get location */
    getFrameLocation() {
        let currentWindow = window;
        let currentParentWindow;
        let frameLocation = ""
        while (currentWindow !== window.top) {
            currentParentWindow = currentWindow.parent;
            for (let idx = 0; idx < currentParentWindow.frames.length; idx++)
                if (currentParentWindow.frames[idx] === currentWindow) {
                    frameLocation = ":" + idx + frameLocation;
                    currentWindow = currentParentWindow;
                    break;
                }
        }
        return frameLocation = "root" + frameLocation;
    }

    /* Recorder */
    record(command, target, value, insertBeforeLastCommand, actualFrameLocation) {
        let self = this;
        console.log("... Action recorder start");
        let signal = {
            command: command,
            target: target,
            value: value,
            insertBeforeLastCommand: insertBeforeLastCommand,
            frameLocation: (actualFrameLocation != undefined ) ? actualFrameLocation : this.frameLocation,
        };
        console.log(signal);
        BrowserAppData.runtime.sendMessage(signal).catch (function(reason) {
            console.log(reason);
        });
    }

    /* attach */
    attach() {
        console.log('attach2');
        if (this.attached) {
            return;
        }
        this.attached = true;
        this.eventListeners = {};
        var self = this;
        for (let event_key in Recorder.eventHandlers) {
            var event_info = this.parse_the_event_key(event_key);
            var event_name = event_info.event_name;
            var capture = event_info.capture;
            function register() {
                var handlers = Recorder.eventHandlers[event_key];
                var listener = function(event) {
                    for (var i = 0; i < handlers.length; i++) {
                        handlers[i].call(self, event);
                    }
                }
                this.window.document.addEventListener(event_name, listener, capture);
                this.eventListeners[event_key] = listener;
            }
            register.call(this);
        }
    }
    /*detach */
    detach() {
        if (!this.attached) {
            return;
        }
        this.attached = false;
        for (let event_key in this.eventListeners) {
            var event_info = this.parse_the_event_key(event_key);
            var event_name = event_info.event_name;
            var capture = event_info.capture;
            this.window.document.removeEventListener(event_name, this.eventListeners[event_key], capture);
        }
        delete this.eventListeners;
    }


} // end the recorder class 

Recorder.eventHandlers = {};
Recorder.addEventHandler = function(handlerName, event_name, handler, options) {
    handler.handlerName = handlerName;
    if (!options) options = false;
    let key = options ? ('C_' + event_name) : event_name;
    if (!this.eventHandlers[key]) {
        this.eventHandlers[key] = [];
    }
    this.eventHandlers[key].push(handler);
}

var recorder = new Recorder(window);
function startShowElement(message, sender, sendResponse){
    if (message.showElement) {
        result = selenium["doShowElement"](message.targetValue);
        return Promise.resolve({result: result});
    }
}
BrowserAppData.runtime.onMessage.addListener(startShowElement);
