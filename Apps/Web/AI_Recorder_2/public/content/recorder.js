// First recording file
print = console.log
browserAppData = chrome || browser;
function generateId(){
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let id = '';
    for (let i = 0; i < 8; i++) {
      id += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return id;
  }
class Recorder {

    /* exq initial time */
    constructor(window) {
        this.window = window;
        this.attached = false;
        this.locatorBuilders = new LocatorBuilders(window);
        this.frameLocation = this.getFrameLocation();
        // console.log("getFrameLocation() =",this.frameLocation);
        // console.log("document", document)
        browserAppData.runtime.sendMessage({
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
    getXpath(target){
        for (let each of this.locatorBuilders.buildAll(target)) 
            if (each[1] == 'xpath:position')
                return each[0];
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

    prepare_dom(xpath, command, value){
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
        // console.log(main_elem.hasAttribute('zeuz'), main_elem);

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

    record({name, xpath, value, tagName, stack={do:false}}) {
        // console.log("getFrameLocation() =",this.frameLocation);
        const dom = this.prepare_dom(xpath, name, value)
        browserAppData.runtime.sendMessage({
            id: generateId(),
            action: 'record_action',
            command: name,
            xpath: xpath,
            value: value,
            url: window.location.href,
            tagName: tagName,
            document: dom,
            stack: stack,
        })
    }

    /* attach */
    attach() {
        if (this.attached) return;
        console.log('attach2', this.newEventListeners);
        this.attached = true;
        for (let each of this.newEventListeners) {
            print('each', each)
            this.window.document.addEventListener(each.name, each.handler, each.capture)
        }

        // this.eventListeners = {};
        // var self = this;
        // for (let event_key in Recorder.eventHandlers) {
        //     var event_info = this.parse_the_event_key(event_key);
        //     var event_name = event_info.event_name;
        //     var capture = event_info.capture;
        //     function register() {
        //         var handlers = Recorder.eventHandlers[event_key];
        //         var listener = function(event) {
        //             for (var i = 0; i < handlers.length; i++) {
        //                 handlers[i].call(self, event);
        //             }
        //         }
        //         this.window.document.addEventListener(event_name, listener, capture);
        //         this.eventListeners[event_key] = listener;
        //     }
        //     register.call(this);
        // }
    }
    /*detach */
    detach() {
        console.log('detach2');
        if (!this.attached) return;
        this.attached = false;
        for (let each of this.newEventListeners) {
            this.window.document.removeEventListener(each.name, each.handler, each.capture)
        }
        // for (let event_key in this.eventListeners) {
        //     var event_info = this.parse_the_event_key(event_key);
        //     var event_name = event_info.event_name;
        //     var capture = event_info.capture;
        //     this.window.document.removeEventListener(event_name, this.eventListeners[event_key], capture);
        // }
        // delete this.eventListeners;
    }


}

var recorder = new Recorder(window);

browserAppData.runtime.sendMessage({
    attachRequest: true
})

browserAppData.runtime.onMessage.addListener(function (request, sender, sendResponse, type) {
    if (request.attachRecorder) {
        recorder.attach();
    } else if (request.detachRecorder) {
        recorder.detach();
    }
});

