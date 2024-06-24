import { useState, useEffect, useRef } from 'react'
import './App.css'
// import {Helmet} from "react-helmet";
import { Action } from './Action'
import type { actionType } from './common'
import Dropdown from './dropdown'
import Overlay from './overlay'
import $ from 'jquery';
import Typewriter from 'typewriter-effect/dist/core'
import { actionsInterface, stepZsvc, RequestType, browserAppData, metaDataInterface, Processing_texts } from './common';

// import { Input, InputRef } from 'antd'
// const { Search } = Input;


const print = console.log
function App() {
    // Contains previous and new actions
    const [actions, setActions] = useState<actionsInterface>([])
    // Test case name
    const [testTitle, setTestTitle] = useState<string>('Loading...')
    // Test case id.. Used to fetch steps in that test case
    const [testId, testIdChange] = useState<string>('0000')
    // Step names showed in select options
    const [stepNames, setStepNames] = useState<stepZsvc[]>([]);
    // Record button state.. Used to start and stop action recording
    const [recordState, setRecordState] = useState<string>('Record');
    // Record button is disabled for first 3 seconds to ensure the scripts are loaded
    const [initRecordState, setInitRecordState] = useState<boolean>(false);
    // Used to disable step selection, test case search, save, run when there are unsaved actions
    const [unsavedActions, setUnsavedActions] = useState<boolean>(false);
    const [showOverlay, setShowOverlay] = useState<boolean>(false);
    // Save button state
    const [saveState, setSaveState] = useState<string>('Save');
    const [runThis, setRunThis] = useState<string>('Run this');
    const [runAll, setRunAll] = useState<string>('Run all');
    const [logText, setLogText] = useState<string>('');

    const containerRef = useRef<HTMLDivElement>(null);
    const actionRef = useRef<HTMLDivElement>(null);
    // const inputRef = useRef<InputRef>(null);

    // Fetch test data when search button is clicked
    // const handleSearch = () => {
    //     if (inputRef.current) {
    //         fetchTestData(testId);
    //     }
    // }

    // Set the value of testId onChange event
    // const handleTestIdChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    //     testIdChange(event.target.value);
    // }

    // Fetch Test data of the testId 

    const saveDisableCondition = !initRecordState || recordState != 'Record' || saveState != 'Save'
    const fetchTestData = async (test_id: string = '', step_no: number = 1) => {
        try {
            let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
            let meta_data: metaDataInterface = localStorageMetadata.meta_data;
            let headers = {
                "X-Api-Key": meta_data.apiKey,
            };
            let r = await fetch(`${meta_data.url}/zsvc/tc/v1/TEST-${test_id}/json`, {
                method: "GET",
                headers: headers,
            });
            let response = await r.json();
            if (response.error) {
                console.error("response.error", response.error)
                await alert(response.error);
                return Promise.reject("Invalid test-id");
            }
            meta_data['testNo'] = 'TEST-' + test_id;
            meta_data['stepNo'] = step_no
            print('response.steps', response.steps)
            print('response filter', response.steps.filter((step: stepZsvc) => { if (step.sequence == step_no) return step }))
            meta_data['stepId'] = response.steps.filter((step: stepZsvc) => { if (step.sequence == step_no) return step })[0].stepId;
            await browserAppData.storage.local.set({
                meta_data: meta_data,
            })

            setTestTitle(response.testCaseDetail.name);
            setStepNames(response.steps.map((step: stepZsvc) => {
                return {
                    name: step.name,
                    sequence: step.sequence,
                    stepId: step.stepId,
                }
            }));
            setUnsavedActions(false)

        } catch (error: any) {
            alert(error.message);
        }
    };

    function attachRecorder(request: { attachRequest: Boolean }, sender: chrome.runtime.MessageSender) {
        sender
        if (request.attachRequest)
            print('attachRequest got')
        setRecordState((prevRecordState) => {
            if (prevRecordState != 'Record')
                browserAppData.tabs.sendMessage(sender.tab?.id || 0, { attachRecorder: true })
            return prevRecordState
        })
    }
    // On initial mount, fetch test-data and actions from server of the testcase and step mentioned in data.json
    useEffect(
        () => {
            browserAppData.runtime.onMessage.addListener(handleRecordResponse);
            browserAppData.runtime.onMessage.addListener(attachRecorder);
            const initData = async () => {
                let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
                let meta_data = localStorageMetadata.meta_data;
                testIdChange(meta_data.testNo.substr(5));
                let prom = fetchTestData(meta_data.testNo.substr(5), meta_data.stepNo);
                const typewriter = new Typewriter(document.getElementById('recorderTitle'), {
                    cursor: '',
                })
                if (recordState == 'Record') {
                    let tabs: any[] = await browserAppData.tabs.query({ url: "<all_urls>" })
                    for (let tab of tabs) {
                        browserAppData.tabs.sendMessage(tab.id, { detachRecorder: true });
                    }
                }
                typewriter
                    .changeDelay(70)
                    .typeString('<div>ZeuZ Co-Pilot</div>')
                    .start()
                    .callFunction(async () => {
                        await prom
                        setInitRecordState(true)
                    });
            }
            initData();
        }, []
    )
    let timeOuts: number[] = []
    useEffect(
        () => {
            setRecordState((prevRecordState) => {
                if (prevRecordState == 'Record')
                    return prevRecordState
                else if (actions.map((item) => { if (!item.stillRecording) return item }).includes(undefined)) {
                    while (timeOuts.length > 0) {
                        clearTimeout(timeOuts.shift())
                    }
                    const timeOut = setTimeout(() => {
                        setRecordState((prevRecordState) => {
                            return prevRecordState == 'Recording...' ? 'Stop' : prevRecordState
                        })
                    }, 30000)
                    timeOuts.push(timeOut)
                    return 'Recording...'
                }

                else
                    return 'Stop'
            })
        }, [actions]
    )
    let logTimeOuts: number[] = []
    // When new recorded actions come from background script, render new actions
    const handleRecordResponse = (request: RequestType) => {
        setRecordState((prevRecordState) => {
            if (prevRecordState == 'Record')
                return prevRecordState;
            if (request.action == 'record-start') {
                if (actionRef.current && containerRef.current) {
                    actionRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }
                const action: actionType = {
                    id: request.data.id,
                    stillRecording: true,
                    is_disable: false,
                    main: [['']],
                    name: '',
                    typeWrite: true,
                    animateRomove: false,
                    short: {
                        action: '',
                        element: '',
                        value: '',
                    },
                    xpath: ''
                }
                setActions((prev_actions) => {
                    const new_actions = [...prev_actions]
                    new_actions.push(action);
                    return new_actions;
                });
                while (logTimeOuts.length > 0) {
                    clearTimeout(logTimeOuts.shift())
                }
                let time = 0
                if (!['keystroke keys', 'go to link'].includes(request.data.action)) {
                    const logsChosen = Processing_texts.sort(() => Math.random() - 0.5).slice(0, Math.floor(Math.random() * 3) + 2)
                    logsChosen.push('')
                    for (let i = 0; i < logsChosen.length; i++) {
                        logTimeOuts.push(setTimeout(() => {
                            setRecordState((prev_rec) => {
                                if (prev_rec == 'Record')
                                    return prev_rec
                                else {
                                    setLogText((prevLog) => {
                                        return logsChosen[i]
                                    })
                                }
                                return prev_rec
                            })
                        }, time))
                        time += Math.random() * 1500 + 1500
                    }
                    return 'Recording...'
                }
            }
            if (request.action == 'record-finish') {
                // Reserve a place with unique hash before api-request to maintain sequence
                const action: actionType = {
                    id: request.data.id,
                    stillRecording: false,
                    is_disable: false,
                    main: request.data.main,
                    name: request.data.name,
                    typeWrite: true,
                    animateRomove: false,
                    short: {
                        action: request.data.action,
                        element: '',
                        value: '',
                    },
                    xpath: request.data.xpath
                }
                setActions((prev_actions) => {
                    const new_actions = [...prev_actions]
                    for (let i = 0; i < new_actions.length; i++) {
                        if (new_actions[i].id == request.data.id /* && new_actions[i].stillRecording */) {
                            new_actions[i] = action;
                            break
                        }
                    }
                    console.log('new_actions', new_actions)
                    return new_actions;
                });
                setUnsavedActions(true)
                console.log('actions', actions);
                return 'Stop'
            }
            return prevRecordState;
        })

    };

    // Hande Record button click.. Contacts with content script
    const handleRecording = async () => {
        if (recordState == 'Record') {
            setLogText('Record started')
            let tabs: any[] = await browserAppData.tabs.query({ url: "<all_urls>" })
            try {
                for (let tab of tabs) {
                    try {
                        browserAppData.tabs.sendMessage(tab.id, { attachRecorder: true })
                    } catch (error) {
                        if (tab.url.startsWith("http://") || tab.url.startsWith("https://")) {
                            console.log('error in sendMessage from tab.url=', tab.url);
                            console.error(error);
                            let msg = (tabs.length == 1) ?
                                `Recorder Disconnected!\n  1. Close the Recorder\n  2. Refresh the page (optional)\n  3. Open Recorder again` :
                                `Recorder Disconnected!\n  1. Close the Recorder\n  2. Close all tabs except the main tab\n  3. Refresh the page (optional)\n  4. Open Recorder again`;
                            alert(msg)
                        }
                    }
                    try {
                        if (tab.title !== 'ZeuZ AI Recorder' && tab.active) {
                            browserAppData.windows.update(tab.windowId, { focused: true });
                        }

                    } catch (error) {
                        console.error(error);
                    }
                }
            } catch (error) {
                console.error(error);
            }
            browserAppData.runtime.sendMessage({
                action: 'start_recording',
                idx: actions.length,
            })
            setRecordState('Stop')
        }
        else if (recordState == 'Stop') {
            let tabs: any[] = await browserAppData.tabs.query({ url: "<all_urls>" })
            for (let tab of tabs) {
                browserAppData.tabs.sendMessage(tab.id, { detachRecorder: true });
            }
            setRecordState('Record');
            setLogText('Removing redundant actions...')
            PostProcess();
            setTimeout(() => {
                setLogText('');
            }, 2000)
        }
    }

    // Saves new actions to server
    const handleSaveActions = async (e: React.MouseEvent<HTMLButtonElement>) => {
        unsavedActions && 
        setShowOverlay(true)
        try {
            let result = await browserAppData.storage.local.get(["meta_data"]);
            var save_data = {
                TC_Id: result.meta_data.testNo,
                step_sequence: result.meta_data.stepNo,
                step_data: JSON.stringify(actions.map(action => {
                    return action.main;
                })),
                step_id: result.meta_data.stepId,
                dataset_name: JSON.stringify(actions.map((action, idx) => {
                    return [
                        action.name,
                        idx + 1,
                        !action.is_disable,
                    ]
                }))
            }
            console.log('save_data', save_data)
            try {
                setSaveState('Saving...')
                setLogText('Saving...')
                await $.ajax({
                    url: result.meta_data.url + '/Home/nothing/update_specific_test_case_step_data_only/',
                    method: 'POST',
                    data: save_data,
                    headers: {
                        // "Content-Type": "application/json",
                        "X-Api-Key": `${result.meta_data.apiKey}`,
                    },
                    success: function (resp) {
                        print('resp', resp)
                        if (resp) {
                            setSaveState('Success!')
                            setLogText('Saved!')
                            setTimeout(() => {
                                setSaveState('Save')
                                setLogText('')
                            }, 1500)
                            setUnsavedActions(false);
                            return
                        }
                        setSaveState('Error!!')
                        setLogText('Error in saving!!')
                        setTimeout(() => {
                            setSaveState('Save')
                            setSaveState('')
                        }, 1500)
                    },
                    error: function (xhr, status, error) {
                        console.error('Error:', error);
                        setSaveState('Error!!')
                        setTimeout(() => {
                            setSaveState('Save')
                        }, 1500)
                        console.error(error);
                    }
                }
                )
            } catch (error) {
                setSaveState('Error!!')
                setTimeout(() => {
                    setSaveState('Save')
                }, 1500)
                console.error(error);
            }
        }
        catch (e) {
            setSaveState('Error!!')
            setTimeout(() => {
                setSaveState('Save')
            }, 1500)
            console.error(e)
        }
    }

    // Remove redundant actions and still-recording actions
    function PostProcess() {
        let indices: number[] = []
        for (let i = 0; i < actions.length; i++) {
            let action = actions[i];
            if (
                action.stillRecording ||
                action.short.action == 'click' &&
                i < actions.length - 1 &&
                ['click', 'text', 'double click', 'validate full text', 'validate full text by ai'].includes(actions[i + 1].short.action) &&
                action.xpath == actions[i + 1].xpath && action.xpath != ''
            )
                indices.push(i);
        }
        return handeRemoveAction(indices, true);
    }

    // At the end of typeWriting Animation remove the typing-demo class
    const handleAnimationRemove = (idx: number) => {
        setActions((prev_actions) => {
            const new_actions = [...prev_actions]
            new_actions[idx].typeWrite = false;
            return new_actions;
        });
    }

    // Remove actions 2 ways: PostProcessing, click trash icon
    const handeRemoveAction = (index: number[], animate: Boolean) => {
        const remove = () => {
            setActions((prev_actions) => {
                const new_actions = []
                for (let i = 0; i < prev_actions.length; i++) {
                    if (index.includes(i)) continue;
                    new_actions.push(prev_actions[i])
                }
                return new_actions;
            });
        }
        if (!animate) {
            remove();
            return;
        }
        // animate removal then remove after 0.5 sec
        setActions((prev_actions) => {
            const new_actions = [...prev_actions]
            for (let i = 0; i < prev_actions.length; i++) {
                if (index.includes(i)) {
                    new_actions[i].animateRomove = true
                }
            }
            return new_actions;
        });
        setTimeout(remove, 1000)
    }

    function handleRunThis() {
        debugTC(true)
    }
    function handleRunAll() {
        debugTC(false)
    }
    async function debugTC(run_this = true) {
        const stateChangeFunc = run_this ? setRunThis : setRunAll
        const stateText = run_this ? 'Run this' : 'Run all'

        try {
            stateChangeFunc("Running...")
            setLogText("Running...")
            var result = await browserAppData.storage.local.get(["meta_data"]);
            const input = {
                method: "POST",
                headers: {
                    // "Content-Type": "application/json",
                    "X-Api-Key": result.meta_data.apiKey,
                }
            }
            var r = await fetch(result.meta_data.url + '/run_config_ai_recorder/', input)
            var response = await r.json();
            console.log("response_1", response);

            const machine = response["machine"];
            const project_id = response["project_id"];
            const team_id = response["team_id"];
            const user_id = response["user_id"];

            let browser = ''
            if (navigator.userAgent.indexOf("Edg") != -1)
                browser = 'Microsoft Edge Chromium'
            else if (navigator.userAgent.indexOf("Chrome") != -1)
                browser = 'Chrome'
            let dependency = { "Browser": browser, "Mobile": "Android" }

            const run_data = {
                "test_case_list": JSON.stringify([result.meta_data.testNo]),
                "dependency_list": JSON.stringify(dependency),
                "all_machine": JSON.stringify([machine]),
                "debug": 'yes',
                "debug_clean": run_this ? "no" : "yes",
                "debug_steps": JSON.stringify(run_this ? [result.meta_data.stepNo.toString()] : []),
                "RunTestQuery": JSON.stringify([result.meta_data.testNo, machine]),
                "dataAttr": JSON.stringify(["Test Case"]),
                "project_id": project_id,
                "team_id": team_id,
                "user_id": user_id,
                "filterArray": JSON.stringify(["AND"])
            }
            print('run_data', run_data)
            var url = `${result.meta_data.url}/Home/nothing/Run_Test/`;

            $.ajax({
                url: url,
                method: 'GET',
                data: run_data,
                headers: {
                    "Content-Type": "application/json",
                    "X-Api-Key": result.meta_data.apiKey,
                },
                success: function (response) {
                    print('respinse_2', response);
                    stateChangeFunc('Queued!')
                    setLogText('Queued!')
                    setTimeout(() => {
                        stateChangeFunc(stateText)
                        setLogText('')
                    }, 1500)
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    jqXHR; textStatus;
                    console.error(errorThrown);
                    stateChangeFunc('Error!!')
                    setLogText('Error playing!!')
                    setTimeout(() => {
                        stateChangeFunc(stateText)
                        setLogText('')
                    }, 1500)
                }
            })
        } catch (error) {
            console.error(error);
            stateChangeFunc('Error!!')
            setLogText('Error playing!!')
            setTimeout(() => {
                stateChangeFunc(stateText)
                setLogText('')
            }, 1500)
        }
    }


    const buttonClass = 'control-button d-flex flex-column align-items-center p-0 bg-transparent my-2"'
    const iconClass = 'material-icons-outlined'
    const labelClass = 'material-icons-label'
    const ops = 1
    return (
        <>
            <div className={"d-flex flex-column root" + (showOverlay ? ' blurred' : '')}>
                <div className="upper-nav d-flex align-items-center">
                    <img className="mx-2" src="logo_ZeuZ.png" alt="" id="logo_dark" />
                    <div className="mx-2 title" id="recorderTitle"></div>
                </div>
                <div id="content" style={{ display: 'block' }}>
                    <div className="m-3">
                        <div id="original_title">
                            <div><span id="test_case_id" style={{ "opacity": 0.6 }}>TEST-{testId}</span> : <span id="test_case_title" className="tc_title_rename">{testTitle}</span>&nbsp;&nbsp;&nbsp;<a className="tc_title_rename hint--left hint--bounce hint--rounded" data-hint="Rename test case title"><i className="fa fa-edit"></i></a></div>
                        </div>
                        <div className="mt-5">
                            <Dropdown stepNames={stepNames} setActions={setActions} />
                        </div>
                    </div>
                    <div className="clearfix" id="recorder_step" ref={containerRef}>
                        {actions.length === 0 && <h5 className="ml-2">No actions</h5>}
                        {actions.map((action, idx) => (
                            <Action action={action} idx={idx} removeAction={handeRemoveAction} animationRemove={handleAnimationRemove} />
                        ))}
                        <div className='my-5 py-5'></div>
                        <div ref={actionRef} className='py-1'></div>
                    </div>
                </div>
                <div className="bottom-nav fixed-bottom py-1">
                    <div className="d-flex flex-row justify-content-around mt-1">
                        {
                            [
                                {
                                    eventHandler: handleRecording,
                                    style: { opacity: (!initRecordState || recordState == "Recording...") ? 0.5 : ops },
                                    disabled: !initRecordState || recordState == "Recording...",
                                    icon: recordState == 'Record' ? 'camera' : 'stop',
                                    label: recordState
                                },
                                {
                                    eventHandler: handleSaveActions,
                                    style: { opacity: initRecordState && recordState == "Record" && saveState == 'Save' ? ops : 0.5 },
                                    disabled: saveDisableCondition,
                                    icon: 'save',
                                    label: saveState,
                                },
                                {
                                    eventHandler: handleRunThis,
                                    style: { opacity: initRecordState && recordState == "Record" && !unsavedActions && runThis == "Run this" ? ops : 0.5 },
                                    disabled: !initRecordState || recordState != 'Record' || unsavedActions || runThis != "Run this",
                                    icon: 'play_circle',
                                    label: runThis
                                },
                                {
                                    eventHandler: handleRunAll,
                                    style: { opacity: initRecordState && recordState == "Record" && !unsavedActions && runAll == "Run all" ? ops : 0.5 },
                                    disabled: !initRecordState || recordState != 'Record' || unsavedActions || runAll != "Run all",
                                    icon: 'play_circle',
                                    label: runAll
                                },
                            ].map((item) => (
                                <button className={buttonClass} onClick={item.eventHandler} disabled={item.disabled}>
                                    <div className={iconClass} style={item.style}>{item.icon}</div>
                                    <div className={labelClass}>{item.label}</div>
                                </button>
                            ))
                        }
                    </div>
                    <div className="mb-2" id="logs">{logText}</div>
                </div>
            </div>

            {showOverlay && <Overlay setShowOverlay={setShowOverlay}/>}
        </>
    )
}

export default App
