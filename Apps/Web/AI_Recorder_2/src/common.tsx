export type actionType ={
    id: string,
    stillRecording: Boolean,
    is_disable: boolean,
    main: string[][],
    name: string,
    typeWrite: boolean,
    animateRomove: boolean,
    short:{
        action: string,
        element: string,
        value: string,
    },
    xpath: string
}

export type actionsInterface = actionType[]

export interface stepZsvc{
    name: string,
    sequence: number,
    id: number,
}
export interface RequestType {
    action: string;
    data: {
        id: string,
        main: string[][];
        name: string;
        action: string;
        xpath: string;
    };
    index: number;
}

export interface metaDataInterface {
    testNo: string,
    testName: string,
    stepNo : number,
    stepName: string,
    url: string,
    apiKey: string,
    jwtKey: string,
}


export const browserAppData = chrome;

// Fetch previous actions of a step from server
export const fetchActionData = async (setActions:(f:()=>actionsInterface)=>void) =>{
    let result = await browserAppData.storage.local.get('meta_data');
    let meta_data = result.meta_data
    const resp = await fetch(`${meta_data.url}/ai_recorder_init?test_id=${meta_data.testNo}&step_seq=${meta_data.stepNo}`, {
        headers: {
            // "Content-Type": "application/json",
            "X-Api-Key": `${meta_data.apiKey}`,
        },
    })
    const init_data: actionsInterface = (await resp.json()).step.actions;
    for (const each of init_data) {
        each['id'] = ''
        each['stillRecording'] = false
        each['typeWrite'] = false;
        each['animateRomove'] = false;
        each['xpath'] = ''
    }
    setActions(()=>init_data);
    console.log('init_data', init_data);
}

