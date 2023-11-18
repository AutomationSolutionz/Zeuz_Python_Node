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
        // Convert to the zeuz defined action names
        this.action_name_convert = {
            type: "text",
            open: "go to link",
            Go_to_link: "go to link",
            doubleClick: "double click",
            Validate_Text: "validate full text",
            Validate_Text_By_AI: "validate full text by ai",
            Save_Text: "save attribute",
            Wait_For_Element_To_Appear: "wait",
            Wait_For_Element_To_Disappear: "wait disable",
        }
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
        if (command === 'go to link'){
            var go_to_link = {
                action: 'go to link',
                data_list: [window.location.href],
                element: "",
                is_disable: false,
                name: `Open ${(window.location.href.length>25) ? window.location.href.slice(0,20) + '...' : window.location.href}`,
                value: window.location.href,
                main: [['go to link', 'selenium action', window.location.href]],
                xpath: "",
            };
            this.recorded_actions[idx] = go_to_link;
            console.log(this.recorded_actions);
            browserAppData.storage.local.set({
                recorded_actions: this.recorded_actions,
            })
            return;
        }
        let validate_full_text_by_ai = false
        if (command === 'validate full text by ai'){
            command = 'validate full text';
            validate_full_text_by_ai = true;
        }

        var html = document.createElement('html');
        html.innerHTML = document.documentElement.outerHTML;

        for (let each of target) if (each[1] == 'xpath:position') {
            var xpath = each[0];
            break;
        }
        var xPathResult = document.evaluate(xpath, html);
        if(xPathResult) var main_elem = xPathResult.iterateNext();
        else return;

        main_elem.setAttribute('zeuz', 'aiplugin');
        console.log(main_elem.hasAttribute('zeuz'), main_elem);

        // Recorder already changed the value which should not be sent to ai-engine
        if (command === 'text')
            main_elem.removeAttribute('value');
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

        // get all <link> elements from html
        var elements = html.getElementsByTagName('link');
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

        let resp = await browserAppData.runtime.sendMessage({
            apiName: 'ai_single_action',
            data: data,
            dataj: dataj,
        })
        if (resp === 'error') {
            console.error("Error happened pls check back.js devtool message");
            return;
        }
        let response = resp.ai_choices;

        if (validate_full_text_by_ai){
            let text_classifier = await chrome.runtime.sendMessage({
                action: 'classify',
                text: value,
            });
            console.log("text_classifier", text_classifier);
            let label = text_classifier[0].label;
            label = label.charAt(0).toUpperCase() + label.slice(1).toLowerCase();
            let offset = Number((text_classifier[0].score * 0.9).toFixed(2));
            offset = Math.max(0.8, offset);
            response[0].data_set = response[0].data_set.slice(0,-1)
            .concat([[label, "text classifier offset", offset]])
            .concat(response[0].data_set.slice(-1))
            value = '';
        }
        else if (command === 'save attribute'){
            response[0].data_set = response[0].data_set.slice(0,-1)
            .concat([
                ["text", "save parameter", "var_name"],
                ["save attribute", "selenium action", "save attribute"],
            ])
            value = '';
        }
        else if (['wait', 'wait disable'].includes(command)){
            value = 10;
        }
        response[0].short.value = value;
        if (value) response[0].data_set[response[0].data_set.length-1][response[0].data_set[0].length-1] = value;
        this.recorded_actions[idx] = {
            action: response[0].short.action,
            data_list: [response[0].short.value],
            element: response[0].short.element,
            is_disable: false,
            name: response[0].name,
            value: response[0].short.value,
            main: response[0].data_set,
            xpath: response[0].xpath,
        };
        console.log(this.recorded_actions);
        browserAppData.storage.local.set({
            recorded_actions: this.recorded_actions,
        })
        
        
    }
    record(command, target, value, insertBeforeLastCommand, actualFrameLocation) {
        if (Object.keys(this.action_name_convert).includes(command)) command = this.action_name_convert[command]
        console.log("... Action recorder start");
        this.idx += 1;
        if (this.recorded_actions.length === 0 || this.recorded_actions.length > 0 && this.recorded_actions[0].action != 'go to link'){
            var go_to_link = {
                action: 'go to link',
                data_list: [window.location.href],
                element: "",
                is_disable: false,
                name: `Open ${(window.location.href.length>25) ? window.location.href.slice(0,20) + '...' : window.location.href}`,
                value: window.location.href,
                main: [['go to link', 'selenium action', window.location.href]],
                xpath: "",
            };
            if (this.recorded_actions.length === 0) this.recorded_actions[0] = go_to_link;
            else this.recorded_actions.unshift(go_to_link);
            this.idx += 1;
        }
        this.fetchAIData(target, this.idx-1, command, value)
        let signal = {
            command: command,
            target: target,
            value: value,
            insertBeforeLastCommand: insertBeforeLastCommand,
            frameLocation: (actualFrameLocation != undefined ) ? actualFrameLocation : this.frameLocation,
        };
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
            else{
                this.idx = 0;
                this.recorded_actions = [];
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
        console.log('detach2');
        if (!this.attached) {
            return;
        }
        this.attached = false;
        console.log('saving recorded_actions from content file');
        // When there are 2 iframes. it saves 3 times. this is a temporary fix. Should be fixed properly
        if (this.recorded_actions.length > 0)
            browserAppData.storage.local.set({
                recorded_actions: this.recorded_actions,
            }).then(()=>{
                this.idx = 0;
                this.recorded_actions = [];
            });
        
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
