var metaData = {};

fetch("./data.json")
    .then(Response => Response.json())
    .then(data => {
        metaData = data;
    });

const browserAppData = chrome || browser;

var idx = 0;
var recorded_actions = [];
var action_name_convert = {
    select: "click",
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

async function start_recording(){
    let res = await browserAppData.storage.local.get('recorded_actions');    
    recorded_actions = res.recorded_actions;
    idx = recorded_actions.length;

}
async function stop_recording(){
    // When there are 2 iframes. it saves 3 times. this is a temporary fix. Should be fixed properly
    if (recorded_actions.length > 0)
    browserAppData.storage.local.set({
        recorded_actions: recorded_actions,
    }).then(()=>{
        idx = 0;
        recorded_actions = [];
    }); 
}
async function fetchAIData(idx, command, value, url, document){
    if (command === 'go to link'){
        let go_to_link = {
            action: 'go to link',
            data_list: [url],
            element: "",
            is_disable: false,
            name: `Open ${(url.length>25) ? url.slice(0,20) + '...' : url}`,
            value: url,
            main: [['go to link', 'selenium action', url]],
            xpath: "",
        };
        recorded_actions[idx] = go_to_link;
        console.log(recorded_actions);
        browserAppData.storage.local.set({
            recorded_actions: recorded_actions,
        })
        return;
    }
    recorded_actions[idx] = 'empty';
    browserAppData.storage.local.set({
        recorded_actions: recorded_actions,
    })
    if (['select', 'click'].includes(command)) value = ""
    let validate_full_text_by_ai = false
    if (command === 'validate full text by ai'){
        command = 'validate full text';
        validate_full_text_by_ai = true;
    }

    var dataj = {
        "page_src": document,
        "action_name": command,
        "action_type": "selenium",
        "action_value": value,
        "source": "web",
    };
    console.log(document);
    var data = JSON.stringify(dataj);

    const url_ = `${metaData.url}/ai_record_single_action/`
    const input = {
        method: "POST",
        headers: {
            // "Content-Type": "application/json",
            "X-Api-Key": metaData.apiKey,
        },
        body: data,
    }
    try {
        var r = await fetch(url_, input)
        var resp = await r.json();
        if(!resp.ai_choices && resp.info){
            browserAppData.runtime.sendMessage({
                action: 'ai_engine_error',
                text: resp.info,
                command:command,
            })
            console.error(resp.info);
            var response = resp.ai_choices;
            recorded_actions[idx] = 'error';
            console.log(recorded_actions);
            browserAppData.storage.local.set({
                recorded_actions: recorded_actions,
            })
            return;
        }
    } catch (error) {
        console.error(error.message);
        browserAppData.runtime.sendMessage({
            action: 'ai_engine_error',
            text: error.message,
            command:command,
        })
        recorded_actions[idx] = 'error';
        console.log(recorded_actions);
        browserAppData.storage.local.set({
            recorded_actions: recorded_actions,
        })
        return;
    }

    if (validate_full_text_by_ai){
        let text_classifier = await browserAppData.runtime.sendMessage({
            action: 'content_classify',
            text: value,
        });

        console.log("text_classifier", text_classifier);
        let label = text_classifier[0].label;
        label = label.charAt(0).toUpperCase() + label.slice(1).toLowerCase();
        let offset = Number((text_classifier[0].score * 0.9).toFixed(2));
        // offset = Math.max(0.8, offset);
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
    if (command === 'text') response[0].data_set[response[0].data_set.length-1][response[0].data_set[0].length-1] = value;
    else if (value) response[0].data_set[response[0].data_set.length-1][response[0].data_set[0].length-1] = value;
    recorded_actions[idx] = {
        action: response[0].short.action,
        data_list: [response[0].short.value],
        element: response[0].short.element,
        is_disable: false,
        name: response[0].name,
        value: response[0].short.value,
        main: response[0].data_set,
        xpath: response[0].xpath,
    };
    console.log(recorded_actions);
    browserAppData.storage.local.set({
        recorded_actions: recorded_actions,
    })
}

async function record_action(command, value, url, document){
    if (Object.keys(action_name_convert).includes(command)) command = action_name_convert[command]
    console.log("... Action recorder start");
    idx += 1;
    if (recorded_actions.length === 0 || 
        recorded_actions.length > 0 && typeof recorded_actions[0] == 'object' && recorded_actions[0].action != 'go to link'){
        let go_to_link = {
            action: 'go to link',
            data_list: [url],
            element: "",
            is_disable: false,
            name: `Open ${(url.length>25) ? url.slice(0,20) + '...' : url}`,
            value: url,
            main: [['go to link', 'selenium action', url]],
            xpath: "",
        };
        if (recorded_actions.length === 0) recorded_actions[0] = go_to_link;
        else recorded_actions.unshift(go_to_link);
        idx += 1;
    }
    fetchAIData(idx-1, command, value, url, document);  
}
browserAppData.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.apiName == 'start_recording') {
            start_recording();
        }
        else if (request.apiName == 'record_action') {
            record_action(
                request.command,
                // request.target,
                request.value,
                request.url,
                request.document,
            );
        }
        else if (request.apiName == 'stop_recording') {
            stop_recording();
        }
    }
);
