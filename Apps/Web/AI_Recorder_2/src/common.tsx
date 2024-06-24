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
    stepId: number,
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
    stepId: number,
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

export const Processing_texts = [
    'Traversing the DOM tree...',
    'Evaluating element attributes...',
    'Analyzing text content...',
    'Filtering out non-alphanumeric characters...',
    'Identifying meaningful word patterns...',
    'Checking for unique element identifiers...',
    'Examining surrounding context...',
    // 'Validating XPath against target element...',
    // 'Optimizing XPath for performance...',
    'Parsing HTML structure...',
    'Extracting relevant data...',
    'Normalizing text values...',
    'Detecting element relationships...',
    'Generating unique locators...',
    // 'Cross-checking with existing XPaths...',
    // 'Refining XPath accuracy...',
    'Handling dynamic content...',
    // 'Ensuring XPath robustness...',
    'Inspecting element structure... ',
    'Traversing parent nodes...',
    'Evaluating sibling elements...',
    'Extracting word patterns...',
    'Identifying meaningful text fragments...',
    'Checking for meaningful text in element attributes...',
    'Extracting partial meaningful text from element content...',
    'Verifying spelling of text content for reliability...',
    'Examining surrounding elements for additional context...',
    'Comparing similar elements to ensure accuracy...',
    'Filtering out random characters from text content...',
    'Constructing optimized XPath expression...'
]
