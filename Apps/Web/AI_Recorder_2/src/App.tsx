import { useState, useEffect } from 'react'
import './App.css'
// import {Helmet} from "react-helmet";
import Action from './Action';

const browserAppData = chrome;
interface actionInterface {
    is_disable: boolean,
    main: string[][],
    name: string,
    short:{
        action: string,
        element: string,
        value: string,
    }
}
type actionsInterface = actionInterface[]

interface stepZsvc{
    name: string,
    sequence: number,
    id: number,
}
function App() {
    const [actions, setActions] = useState<actionsInterface>([])
    const [testTitle, setTestTitle] = useState<string>('Loading...')
    const [selectedValue, setSelectedValue] = useState<string>('1');
    const [testId, testIdChange] = useState<string>('0000')
    const [stepNames, setStepNames] = useState<stepZsvc[]>([]);

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

    const handleTestIdChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        testIdChange(event.target.value);
    };

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
            fetchActionData()

        } catch (error:any) {
            alert(error.message);
        }
    };

    const handleSearch = () => {
        fetchTestData();
    }

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
        setActions(()=>init_data);
        console.log('init_data', init_data);
    }
    
    useEffect(
        ()=>{
            browserAppData.runtime.onMessage.addListener(handleMessage);
            const initData = async () => {
                let localStorageMetadata = await browserAppData.storage.local.get('meta_data');
                let meta_data = localStorageMetadata.meta_data;
                testIdChange(meta_data.testNo.substr(5));
                fetchTestData(meta_data.testNo.substr(5), meta_data.stepNo);
            }
            initData();
        },[]
    )

    
    const handleMessage = (request:any) => {
        // Update the count based on the received message
        if (request.action == 'record_finish') {
            const action: actionInterface = {
                is_disable: request.data.is_disabled,
                main: request.data.main,
                name: request.data.name,
                short:{
                    action: '',
                    element: '',
                    value: '',
                }
            }
            setActions((prev_actions) => {
                const new_actions = [...prev_actions]
                new_actions[request.index] = action
                return new_actions;
            });
            console.log('actions',actions);
        }
      };


    return (
        <div className="wrapper d-flex align-items-stretch">
            <nav id="sidebar">
                <div className="nav_upper">
                    <div className="img bg-wrap text-center py-4" data-section="welcome_page" id="defaultOpen">
                        <img className="img-fluid" id="logo_dark" src="logo_ZeuZ_dark_background.png" />
                    </div>
                    <ul className="d-flex flex-column justify-content-center">
                        <li className="tablink d-flex flex-wrap justify-content-center" id="record_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                id="record" style={{ opacity: 0.5 }} disabled>
                                <span className="material-icons" id="record_icon">camera</span>
                                <span className="material-icons-label" id="record_label">Record</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="save_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                id="save_button">
                                <span className="material-icons">save</span>
                                <span className="material-icons-label" id='save_label'>Save</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="run_this_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                id="run_this_button">
                                <span className="material-icons">play_circle</span>
                                <span className="material-icons-label" id='run_this_label'>Run this</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="run_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                id="run_button">
                                <span className="material-icons">play_circle</span>
                                <span className="material-icons-label" id='run_label'>Run all</span>
                            </button>
                        </li>
                        <li className="tablink d-flex flex-wrap justify-content-center" id="login_wrap">
                            <button className="d-flex justify-content-start bg-transparent border-0 my-2 sidebar_menu"
                                data-toggle="modal" data-target="#exampleModal">
                                <span className="material-icons">login</span>
                                <span className="material-icons-label">Login</span>
                            </button>
                        </li>
                    </ul>
                </div>
                <ul className="d-flex flex-column justify-content-center" id="bottom_section">
                    {/* <li className="tablink d-flex justify-content-center opensection my-2" data-section="settings">
                        <button className="d-flex justify-content-start bg-transparent border-0 sidebar_menu" href="#">
                            <span className="material-icons" id="settings_icon">settings</span>
                            <span className="material-icons-label" id="settings _label">Settings</span>
                        </button>
                    </li> */}
                </ul>
            </nav>
            <div className="tabcontent scrollBar" id="content" style={{ display: 'block' }}>
                <div className="m-4 fs-6 font-weight-bold font-weight-bold text-dark">
                    <div>
                        <div>
                            <form>
                                <div className="input-group mb-3">
                                    <span className="input-group-text" id="basic-addon1">TEST-</span>
                                    <input id="test_id" value={testId} onChange={handleTestIdChange} className="form-control"
                                        placeholder="0000" aria-label="Test case ID" />
                                    <button id="fetch" className="btn btn-secondary" type="button" onClick={handleSearch}>
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
                <select value={selectedValue} onChange={handleSelectChange} className="form-select form-select-sm m-4 w-50" id="step_select" style={{ height: '42px', padding: '8px' }}>
                    {/* <option selected>Step-1 : Loading ...</option> */}
                    {stepNames.map((step: stepZsvc)=>(
                        <option value={step.sequence}>Step-{step.sequence} : {step.name}</option>
                    )
                    )}
                </select>
                <div className="clearfix mx-2" id="recorder_step">
                    {actions.length === 0 && <h5>No actions</h5>}
                    {actions.map((action, idx)=>(
                        <Action action={action} idx={idx}/>
                    ))}
                    {/* <div className="second_table table-responsive" id="main_table">
                    <div className="table table-borderless border_separate table-fixed" id="sortable">
                        <tbody className="table_body" id="case_data_wrap" style={{minHeight: '600px'}}>
                        </tbody>
                    </div>
                </div> */}
                </div>
            </div>

            {/* <script src="assets/js/windowController.js"></script>
            <script src="assets/js/panel_recorder.js"></script>
            <script src="assets/js/panel.js"></script> */}

        </div>
    )

}

export default App
