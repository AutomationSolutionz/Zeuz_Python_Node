/* ZeuZ Start the recording function */
browserAppData = chrome || browser;
class Recorder {

    /* exq initial time */
    constructor(window) {
        this.window = window;
        this.attached = false;
        this.locatorBuilders = new LocatorBuilders(window);
        this.frameLocation = undefined;
        this.iframeDom = undefined;
        this.getFrameLocation();
        console.log("getFrameLocation() =",this.frameLocation);
        // console.log("document", document);
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

    createElementFromHTML(htmlString) {
        var div = document.createElement('div');
        div.innerHTML = htmlString.trim();
        // Change this to div.childNodes to support multiple top-level nodes.
        return div.firstElementChild;
      }
    getFrameLocation() {
        let currentWindow = window;
        let currentParentWindow;
        let frameLocation = "";
        let i_elem_list=[];
        let temp_i_elem_list = [];
        let add_flag_once = true;
        while (currentWindow !== window.top) {
            currentParentWindow = currentWindow.parent;
            let iframe_elements = currentParentWindow.document.getElementsByTagName('iframe');
            while(i_elem_list.length>0) temp_i_elem_list.push(i_elem_list.shift());
            i_elem_list = [];
            let i_elem;
            for (let idx = 0; idx < currentParentWindow.frames.length; idx++){
                i_elem = this.createElementFromHTML(iframe_elements[idx].outerHTML.replace('iframe', 'zframe'));
                if (currentParentWindow.frames[idx] === currentWindow) {
                    frameLocation = ":" + idx + frameLocation;
                    currentWindow = currentParentWindow;
                    if (add_flag_once) {
                        i_elem.setAttribute("zeuz", "iframe");
                        add_flag_once = false;
                    }
                    var temp = ''
                    while(temp_i_elem_list.length>0) temp += temp_i_elem_list.shift().outerHTML;
                    i_elem.innerHTML = temp;
                }
                i_elem_list.push(i_elem);
            }
        }
        let iframe_dom = document.createElement('zframes');
        var iframes = '';
        while(i_elem_list.length>0) iframes += i_elem_list.shift().outerHTML;
        iframe_dom.innerHTML = iframes;
        console.log("iframe_dom", iframe_dom);
        this.frameLocation = "root" + frameLocation;
        if(frameLocation) this.iframeDom = iframe_dom;
    }


    prepare_dom(target, command, value){
        for (let each of target) if (each[1] == 'xpath:position') {
            var xpath = each[0];
            break;
        }

        var html = document.createElement('html');
        html.innerHTML = document.documentElement.outerHTML;

        var xPathResult = document.evaluate(xpath, html);
        if(xPathResult) var main_elem = xPathResult.iterateNext();
        else return;

        if (main_elem.tagName === 'SELECT' && command === 'select'){
            xPathResult = document.evaluate(`./option[normalize-space(text())="${value.substr(6).trim()}"]`, main_elem);
            if(xPathResult) main_elem = xPathResult.iterateNext();
        }
        
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

        return html.outerHTML
    }

    record(command, target, value) {
        const dom = this.prepare_dom(target, command, value)
        let signal = {
            apiName: 'record_action',
            command: command,
            target: target,
            value: value,
            url: window.location.href,
            document: dom,
            iframeLoc: this.frameLocation,
            iframeDom: this.iframeDom,
        };
        browserAppData.runtime.sendMessage(signal);
        console.log(signal);
    }

    /* attach */
    attach() {
        console.log('attach2');
        if (this.attached) return;
        browserAppData.runtime.sendMessage({
            apiName: 'start_recording',
        })
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
        if (!this.attached) return;
        browserAppData.runtime.sendMessage({
            apiName: 'stop_recording',
        })
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
browser.runtime.onMessage.addListener(startShowElement);
