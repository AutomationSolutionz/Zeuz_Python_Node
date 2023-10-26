/* ZeuZ Start the recording function */
browserAppData = chrome || browser;
class Recorder {

    /* exq initial time */
    constructor(window) {
        this.window = window;
        this.attached = false;
        this.locatorBuilders = new LocatorBuilders(window);
        this.frameLocation = this.getFrameLocation();
        browser.runtime.sendMessage({
            frameLocation: this.frameLocation
        }).catch(function(reason) {
        });
        this.recorded_actions = [];
        this.idx = 0;
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
    async fetchAIData(target, idx, command, value){
        var html = document.createElement('html');
        html.innerHTML = document.documentElement.outerHTML;

        for (let each of target) if (each[1] == 'xpath:position') {var xpath = each[0];break;}
        var xPathResult = document.evaluate(xpath, html);
        if(xPathResult) var main_elem = xPathResult.iterateNext();
        else return;

        main_elem.setAttribute('zeuz', 'aiplugin');
        console.log(main_elem.hasAttribute('zeuz'), main_elem);

        // get all <head> elements from html
        var elements = html.getElementsByTagName('head');
        while (elements[0])
            elements[0].parentNode.removeChild(elements[0])

        // get all <script> elements from html
        var elements = html.getElementsByTagName('script');
        while (elements[0])
            elements[0].parentNode.removeChild(elements[0])

        // get all <style> elements from html
        var elements = html.getElementsByTagName('style');
        while (elements[0])
            elements[0].parentNode.removeChild(elements[0])

        var xPathResult = document.evaluate(xpath, document);
        if(xPathResult) console.log('doc true')
        else console.log('doc false');

        var xPathResult = document.evaluate(xpath, html);
        if(xPathResult) console.log('html true')
        else console.log('html false');

        var dataj = {
            "page_src": html.outerHTML,
            "action_name": command,
            "action_type": "selenium",
            "action_value": value,
            "source": "web",
        };
        var data = JSON.stringify(dataj);

        browserAppData.runtime.sendMessage({
            apiName: 'ai_single_action',
            data: data,
            dataj: dataj,
        },
        response => {
            console.log(response);
            response[0].short.value = value;
            this.recorded_actions[idx] = {
                long: response[0].data_set,
                short: response[0].short,
                xpath: response[0].xpath,
            };
            console.log(idx);
            console.log(this.recorded_actions);
        }
        );
    }
    record(command, target, value, insertBeforeLastCommand, actualFrameLocation) {
        let self = this;
        if (command == 'doubleClick')
            console.log('doubleClick')
        console.log("... Action recorder start");
        let signal = {
            command: command,
            target: target,
            value: value,
            insertBeforeLastCommand: insertBeforeLastCommand,
            frameLocation: (actualFrameLocation != undefined ) ? actualFrameLocation : this.frameLocation,
        };
        this.idx += 1;
        this.fetchAIData(target, this.idx-1, command, value)
        console.log(signal);
        browser.runtime.sendMessage(signal).catch (function(reason) {
            console.log(reason);
        });
    }

    /* attach */
    attach() {
        
        console.log('attach2');
        if (this.attached) return;
        browserAppData.storage.local.get('recorded_actions')
        .then(res=>{
            if(res.recorded_actions){
                console.log(res);
                this.idx = res.recorded_actions.length;
                this.recorded_actions = res.recorded_actions;
            }
        });
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
        browserAppData.storage.local.set({
            recorded_actions: this.recorded_actions,
        });
        this.idx = 0;
        this.recorded_actions = [];
        
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
browser.runtime.onMessage.addListener(startShowElement);
