import { useState, useEffect } from 'react'
import './App.css'
// import {Helmet} from "react-helmet";
import {Action, actionType} from './Action';
import $ from 'jquery';

const browserAppData = chrome;
type actionsInterface = actionType[]

interface stepZsvc{
    name: string,
    sequence: number,
    id: number,
}
function App() {
    // Contains previous and new actions
    const [actions, setActions] = useState<actionsInterface>([])
    // Test case name
    const [testTitle, setTestTitle] = useState<string>('Loading...')
    // The selected step number.. Used to fetch actions in that step
    const [selectedValue, setSelectedValue] = useState<string>('1');
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
    // Save button state
    const [saveState, setSaveState] = useState<string>('Save');


    // When selected step is changed fetch new actions
    const handleSelectChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newValue = event.target.value;
        let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
        let meta_data = localStorageMetadata.meta_data;
        meta_data['stepNo'] = parseInt(newValue) ;
        meta_data['stepId'] = stepNames.filter((step: stepZsvc)=>{if(step.sequence==parseInt(newValue)) return step.id})[0].id
        await browserAppData.storage.local.set({
            meta_data: meta_data,
        })
        setSelectedValue(newValue);
        fetchActionData()
    };

    // testId state change. does not fetch anything
    const handleTestIdChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        testIdChange(event.target.value);
    };

    // Fetch Test data of the testId 
    const fetchTestData = async (test_id: string = '', step_no: number=1) => {
        try {
            test_id = (test_id == '') ? testId : test_id
            let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
            let meta_data = localStorageMetadata.meta_data;
            let headers = {
                "X-Api-Key": meta_data.apiKey,
            };
            let r = await fetch(`${meta_data.url}/zsvc/tc/v1/TEST-${test_id}/json`, {
                method: "GET",
                headers: headers,
            });
            let response = await r.json();
            if (response.error){
                console.error("response.error", response.error)
                await alert(response.error);
                return Promise.reject("Invalid test-id");
            }
            meta_data['testNo'] = 'TEST-'+test_id;
            meta_data['stepNo'] = step_no
            meta_data['stepId'] = response.steps.filter((step: stepZsvc)=>{if(step.sequence==step_no) return step.id})[0].stepId;
            await browserAppData.storage.local.set({
                meta_data: meta_data,
            })

            setTestTitle(response.testCaseDetail.name);
            setStepNames(response.steps.map((step: stepZsvc) => {
                return {
                    name: step.name,
                    sequence: step.sequence,
                    id: step.id,
                }
            }));
            setSelectedValue(step_no.toString());
            setUnsavedActions(false)
            fetchActionData()

        } catch (error:any) {
            alert(error.message);
        }
    };

    // Fetch test data when search button is clicked
    const handleSearch = () => {
        fetchTestData();
    }

    // Fetch previous actions of a step from server
    const fetchActionData = async () =>{
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
            each['typeWrite'] = false;
            each['animateRomove'] = false;
            each['xpath'] = ''
        }
        setActions(()=>init_data);
        console.log('init_data', init_data);
    }
    
    // On initial mount, fetch test-data and actions from server of the testcase and step mentioned in data.json
    useEffect(
        ()=>{
            browserAppData.runtime.onMessage.addListener(handleRecordResponse);
            const initData = async () => {
                let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
                let meta_data = localStorageMetadata.meta_data;
                testIdChange(meta_data.testNo.substr(5));
                fetchTestData(meta_data.testNo.substr(5), meta_data.stepNo);
            }
            initData();
            setTimeout( 
                ()=>{setInitRecordState(true)}
            ,3000)
        },[]
    )

    // When new recorded actions come from background script, render new actions
    const handleRecordResponse = (request:any) => {
        if (request.action == 'recording') {
            setRecordState('Recording...')
            setTimeout(()=>{
                // If server does not respond in 30 sec change the Recording... state
                console.log('recordState',recordState)
                if(recordState == 'Record')
                    setRecordState('Stop')
            }, 30000)
        }
        if (request.action == 'record_finish') {
            const action: actionType = {
                is_disable: false,
                main: request.data.main,
                name: request.data.name,
                typeWrite: true,
                animateRomove: false,
                short:{
                    action: request.data.action,
                    element: '',
                    value: '',
                },
                xpath: request.data.xpath
            }
            setActions((prev_actions) => {
                const new_actions = [...prev_actions]
                if (request.index >= new_actions.length) {
                    new_actions.push(action);
                  }
                else {
                    new_actions.splice(request.index, 0, action);
                }
                console.log('new_actions',new_actions)
                return new_actions;
            });
            setUnsavedActions(true)
            console.log('actions',actions);
            setRecordState('Stop')
        }
    };

    // Hande Record button click.. Contacts with content script
    const handleRecording = async () =>{
        if (recordState == 'Record'){
            let tabs:any[] = await browserAppData.tabs.query({url: "<all_urls>"})
			try {
				for(let tab of tabs) {
					try {
						browserAppData.tabs.sendMessage(tab.id, { attachRecorder: true })
					} catch (error) {
						if (tab.url.startsWith("http://") || tab.url.startsWith("https://")){
							console.log('error in sendMessage from tab.url=', tab.url);
							console.error(error);
							let msg = (tabs.length == 1) ?
							`Recorder Disconnected!\n  1. Close the Recorder\n  2. Refresh the page (optional)\n  3. Open Recorder again` :
							`Recorder Disconnected!\n  1. Close the Recorder\n  2. Close all tabs except the main tab\n  3. Refresh the page (optional)\n  4. Open Recorder again` ;
							alert(msg)
						}
					}
					try {
						if(tab.title !== 'ZeuZ AI Recorder' && tab.active){
							browserAppData.windows.update(tab.windowId, {focused: true});
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
        else if(recordState == 'Stop'){
            let tabs:any[] = await browserAppData.tabs.query({url: "<all_urls>"})
            for(let tab of tabs) {
                browserAppData.tabs.sendMessage(tab.id, {detachRecorder: true});
            }
            setRecordState('Processing...');
            PostProcess();
            setTimeout(()=>{
                setRecordState('Record');
            }, 1000)
        }
    }

    // Saves new actions to server
    const handleSaveActions = async () =>{
        try{
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
						idx+1,
						!action.is_disable,
					]
				}))
			}

            try {
                setSaveState('Saving...')
                await $.ajax({
                    url: result.meta_data.url + '/Home/nothing/update_specific_test_case_step_data_only/',
                    method: 'POST',
                    data: save_data,
                    headers: {
                        // "Content-Type": "application/json",
                        "X-Api-Key": `${result.meta_data.apiKey}`,
                    },
                    success: function () {
                        setSaveState('Success')
                        setTimeout(()=>{
                            setSaveState('Save')
                        }, 1500)
                        setUnsavedActions(false);
                    },
                    error: function (xhr, status, error) {
                        xhr;status
                        console.error('Error:', error);
                        setSaveState('Error!!')
                        setTimeout(()=>{
                            setSaveState('Save')
                        }, 1500)
                        console.error(error);
                      }
                    }
                )
              } catch (error) {
                setSaveState('Error!!')
                setTimeout(()=>{
                    setSaveState('Save')
                }, 1500)
                console.error(error);
              }
		}
		catch(e){
            setSaveState('Error!!')
            setTimeout(()=>{
                setSaveState('Save')
            }, 1500)
            console.error(e)
		}
    }
    
    function PostProcess(){
        let indices: number[] = []
        for(let i = 0; i < actions.length; i++){
            let action = actions[i];

            if(
                action.short.action == 'click' && 
                i < actions.length - 1 && 
                ['click', 'text', 'double click', 'validate full text', 'validate full text by ai'].includes(actions[i+1].short.action)  &&
                action.xpath == actions[i+1].xpath && action.xpath != ''
            ) 
            indices.push(i);
        }
        return handeRemoveAction(indices, true);

	}

    // At the end of typeWriting Animation remove the typing-demo class
    const handleAnimationRemove = (idx:number) => {
        setActions((prev_actions) => {
            const new_actions = [...prev_actions]
            new_actions[idx].typeWrite = false;
            return new_actions;
        });
    }

    // Remove actions 2 ways: PostProcessing, click trash icon
    const handeRemoveAction = (index:number[], animate:Boolean) => {
        const remove =  ()=>{
            setActions((prev_actions) => {
                const new_actions = []
                for (let i=0; i < prev_actions.length; i++){
                    if (index.includes(i)) continue;
                    new_actions.push(prev_actions[i])
                }
                return new_actions;
            });
        }
        if(!animate){
            remove();
            return;
        }
        // animate removal then remove after 0.5 sec
        setActions((prev_actions) => {
            const new_actions = [...prev_actions]
            for (let i=0; i < prev_actions.length; i++){
                if (index.includes(i)){
                    new_actions[i].animateRomove = true
                }
            }
            return new_actions;
        });
        setTimeout(remove, 500)
    }

    return (
        <div className="wrapper d-flex align-items-stretch">
            <nav id="sidebar">
                <div className="nav_upper">
                    <div className="img bg-wrap text-center py-4" data-section="welcome_page" id="defaultOpen">
                        <img className="img-fluid" id="logo_dark" src="logo_ZeuZ_dark_background.png" />
                    </div>
                    <ul className="d-flex flex-column justify-content-center">
                        <li className="tablink d-flex flex-wrap justify-content-center" id="record_wrap" >
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu" onClick={handleRecording}
                                id="record" style={{ opacity: (!initRecordState || recordState == "Recording...") ? 0.5 : 1}} disabled={!initRecordState || recordState == "Recording..."}>
                                <span className="material-icons" id="record_icon">{recordState == 'Record' ? 'camera' : 'stop'}</span>
                                <span className="material-icons-label" id="record_label">{recordState}</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="save_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu" onClick={handleSaveActions}
                                id="save_button" style={{ opacity: recordState == "Record" && saveState == 'Save' ? 1 : 0.5}} disabled={recordState != 'Record' || saveState != 'Save'}>
                                <span className="material-icons">save</span>
                                <span className="material-icons-label" id='save_label'>{saveState}</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="run_this_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                id="run_this_button" style={{ opacity: recordState == "Record" && !unsavedActions ? 1 : 0.5}} disabled={recordState != 'Record' || unsavedActions}>
                                <span className="material-icons">play_circle</span>
                                <span className="material-icons-label" id='run_this_label'>Run this</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="run_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                id="run_button" style={{ opacity: recordState == "Record" && !unsavedActions ? 1 : 0.5}} disabled={recordState != 'Record' || unsavedActions}>
                                <span className="material-icons">play_circle</span>
                                <span className="material-icons-label" id='run_label'>Run all</span>
                            </button>
                        </li>
                        <li className="d-none tablink d-flex flex-wrap justify-content-center" id="login_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                data-toggle="modal" data-target="#exampleModal" style={{ opacity: recordState == "Record" && !unsavedActions ? 1 : 0.5}} disabled={recordState != 'Record' || unsavedActions}>
                                <span className="material-icons">login</span>
                                <span className="material-icons-label">Login</span>
                            </button>
                        </li>
                    </ul>
                </div>
            </nav>
            <div className="tabcontent scrollBar" id="content" style={{ display: 'block' }}>
                <div className="m-4 fs-6 font-weight-bold font-weight-bold text-dark">
                    <div>
                        <div>
                            <form>
                                <div className="input-group mb-3"  style={{ opacity: recordState == "Record" && !unsavedActions ? 1 : 0.5}}>
                                    <span className="input-group-text" id="basic-addon1">TEST-</span>
                                    <input id="test_id" value={testId} onChange={handleTestIdChange} className="form-control"
                                        placeholder="0000" aria-label="Test case ID" disabled={recordState != 'Record'} />
                                    <button id="fetch" className="btn btn-secondary" type="button" onClick={handleSearch} disabled={recordState != 'Record' || unsavedActions}>
                                        <span className="material-symbols-outlined" style={{ color: 'white !important' }}>
                                            search
                                        </span>
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                    <div className="modal fade" id="exampleModal" tabIndex={-1} role="dialog"
                        aria-labelledby="exampleModalLabel" aria-hidden="true">
                        <div className="modal-dialog" role="document">
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h5 className="modal-title" id="exampleModalLabel">Login to ZeuZ server</h5>
                                    <button type="button" className="close" data-dismiss="modal" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                    </button>
                                </div>
                                <div className="modal-body">
                                    <label htmlFor="server_address" className="col-form-label">Server Address:</label>
                                    <input type="text" className="form-control border border-1" id="server_address"
                                        placeholder="https://apollo.zeuz.ai" />
                                    <label htmlFor="api_key" className="col-form-label">API-key:</label>
                                    <input type="text" className="form-control border border-1" id="api_key"
                                        placeholder="32 digit api-key" />
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                                    <button type="button" className="btn btn-primary" id="authenticate">Authenticate</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <h5 id="test_title">{testTitle}</h5>
                </div>
                <select value={selectedValue} onChange={handleSelectChange} className="form-select form-select-sm m-4 w-50" id="step_select" style={{ height: '42px', padding: '8px', opacity: recordState == "Record" && !unsavedActions ? 1 : 0.5}} disabled={recordState != 'Record' || unsavedActions}>
                    {stepNames.map((step: stepZsvc)=>(
                        <option value={step.sequence}>Step-{step.sequence} : {step.name}</option>
                    )
                    )}
                </select>
                <div className="clearfix mx-2" id="recorder_step">
                    {actions.length === 0 && <h5>No actions</h5>}
                    {actions.map((action, idx)=>(
                        <Action action={action} idx={idx} removeAction={handeRemoveAction} animationRemove={handleAnimationRemove}/>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default App
