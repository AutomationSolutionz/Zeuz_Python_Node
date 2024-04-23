// import { useState } from 'react'
import './App.css'
// import {Helmet} from "react-helmet";

function App() {
  // const [count, setCount] = useState(0)

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
                            id="record" style={{opacity: 0.5}} disabled>
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
        <div className="tabcontent scrollBar" id="content" style={{display: 'block'}}>
            <div className="m-4 fs-6 font-weight-bold font-weight-bold text-dark">
                <div>
                    <div>
                        <form>
                            <div className="input-group mb-3">
                                <span className="input-group-text" id="basic-addon1">TEST-</span>
                                <input id="test_id" value="0000" type="number" maxLength={5} className="form-control"
                                    placeholder="0000" aria-label="Test case ID"/>
                                <button id="fetch" className="btn btn-secondary" type="button">
                                    <span className="material-symbols-outlined" style={{color: 'white !important'}}>
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
                                    placeholder="https://apollo.zeuz.ai"/>
                                <label htmlFor="api_key" className="col-form-label">API-key:</label>
                                <input type="text" className="form-control border border-1" id="api_key"
                                    placeholder="32 digit api-key"/>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" data-dismiss="modal">Close</button>
                                <button type="button" className="btn btn-primary" id="authenticate">Authenticate</button>
                            </div>
                        </div>
                    </div>
                </div>

                <h5 id="test_title">My test name</h5>
            </div>
            <select className="form-select form-select-sm m-4 w-50" id="step_select" style={{height: '42px', padding: '8px'}}>
               {/* <option selected>Step-1 : Loading ...</option> */}
            </select>
            <div className="clearfix mx-2" id="recorder_step">
                <div className="second_table table-responsive" id="main_table">
                    <table className="table table-borderless border_separate table-fixed" id="sortable">
                        <tbody className="table_body" id="case_data_wrap" style={{minHeight: '600px'}}>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

            {/* <script src="assets/js/windowController.js"></script>
            <script src="assets/js/panel_recorder.js"></script>
            <script src="assets/js/panel.js"></script> */}

    </div>
  )
  
}

export default App
