/* Zeuz start play back function */

var labels = {};
var expectingLabel = null;
var blockStack = [];

var currentPlayingFromHereCommandIndex = 0;
var currentPlayingCommandIndex = -1;

var currentTestCaseId = "";
var isPause = false;
var pauseValue = null;
var isSelecting = false;
var isPlayingSuite = false;
var isPlayingAll = false;
var selectTabId = null;

var pageCount = 0;
var pageTime = "";
var ajaxCount = 0;
var commandType = "";
var ajaxTime = "";
var domCount = 0;
var implicitTime = "";
var domTime = "";
var implicitCount = 0;

var caseFailed = false;
var extCommand = new ExtCommand();

window.onload = function() {
    var recordButton = document.getElementById("record");
    var recordStopButton = document.getElementById("record_stop");//custom
    var playButton = document.getElementById("playback");
    var replayButton = document.getElementById("replay");
    var stopButton = document.getElementById("stop");
    var pauseButton = document.getElementById("pause");
    var resumeButton = document.getElementById("resume");
    var playAll = document.getElementById('playAll');

    var playSuiteButton = document.getElementById("playSuite");
    var playSuitesButton = document.getElementById("playSuites");
    var showElementButton = document.getElementById("showElementButton")
    var selectElementButton = document.getElementById("selectElementButton");
    var suitePlus = document.getElementById("suite-plus");
    var suiteOpen = document.getElementById("suite-open");

    var referContainer=document.getElementById("refercontainer");
    var logContainer=document.getElementById("logcontainer");
    var saveLogButton=document.getElementById("save-log");


    saveLogButton.addEventListener("click",savelog);
    referContainer.style.display="none";
    $('#command-command').on('input change', function() {
        scrape(document.getElementById("command-command").value);
    });

    suitePlus.addEventListener("mouseover", mouseOnSuiteTitleIcon);
    suitePlus.addEventListener("mouseout", mouseOutSuiteTitleIcon);
    suiteOpen.addEventListener("mouseover", mouseOnSuiteTitleIcon);
    suiteOpen.addEventListener("mouseout", mouseOutSuiteTitleIcon);

    var logLi=document.getElementById("history-log");
    var referenceLi=document.getElementById("reference-log");
    var logState=true;
    var referenceState=false;

    setTimeout(()=>{    // Add listener after 2 sec
        recordButton.addEventListener("click", function(){
            clean_panel(); // clean the panel after one record is complate
            $('#records-grid').html('<input id="records-count" type="hidden" value="0">'); 
            isRecording = $('#record_label')[0].textContent == 'Record';
            if (isRecording) {
                recorder.attach();
                notificationCount = 0;
                if (contentWindowId) {
                    browser.windows.update(contentWindowId, {focused: true});
                }
                browser.tabs.query({windowId: extCommand.getContentWindowId(), url: "<all_urls>"})
                .then(function(tabs) {
                    for(let tab of tabs) {
                        browser.tabs.sendMessage(tab.id, {attachRecorder: true});
                    }
                });
                // recordButton.childNodes[1].textContent = " Stop";
                // switchRecordButton(false);
                $('#play_wrap,#pause_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').addClass('disable_action');
            }
            else {
                recorder.detach();
                saveData();
                browser.tabs.query({windowId: extCommand.getContentWindowId(), url: "<all_urls>"})
                .then(function(tabs) {
                    for(let tab of tabs) {
                        browser.tabs.sendMessage(tab.id, {detachRecorder: true});
                    }
                });
                // switchRecordButton(true);
                $('#play_wrap,#pause_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').removeClass('disable_action');
            }
        })
    
        /* Custom */
        // recordStopButton.addEventListener("click", function(){
        //     isRecording = !isRecording;
        //     if (!isRecording) {
        //         recorder.detach();
        //         saveData();
        //         browser.tabs.query({windowId: extCommand.getContentWindowId(), url: "<all_urls>"})
        //         .then(function(tabs) {
        //             for(let tab of tabs) {
        //                 browser.tabs.sendMessage(tab.id, {detachRecorder: true});
        //             }
        //         });
        //         switchRecordButton(true);
        //         $('#play_wrap,#pause_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').removeClass('disable_action');
        //         /* Custom Function */
        //         //clean_panel(); // clean the panel after one record is complate
        //         //$('#records-grid').html('<input id="records-count" type="hidden" value="0">'); 
        //         /* Custom Function */
    
        //     }
        // })
    
    },0)
    

    playButton.addEventListener("click", function() {
        if($('#records-count').val() == 0){
            return;
        }

        //saveData();
        emptyNode(document.getElementById("logcontainer"));
        document.getElementById("result-runs").textContent = "0";
        document.getElementById("result-failures").textContent = "0";
        recorder.detach();
        initAllSuite();
        setCaseScrollTop(getSelectedCase());

        if (contentWindowId) {
            browser.windows.update(contentWindowId, {focused: true});
        }
        declaredVars = {};
        clearScreenshotContainer();
        expectingLabel = null;

        var s_suite = getSelectedSuite();
        var s_case = getSelectedCase();
        $('#passed_record,#failed_record,#disable_record').html(0);
        //zeuz_log.info("Playing test case " + zeuz_testSuite[s_suite.id].title + " / " + zeuz_testCase[s_case.id].title);
        logStartTime();
        play();
        $('#record_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').addClass('disable_action');
    });

    replayButton.addEventListener("click", function() {
        /* Stop the exeqution and then replay */
        var setTimeout1 = 0;

        if (isPause){
            setTimeout1 = 700;
            stop();
        }

        setTimeout(function(){
            emptyNode(document.getElementById("logcontainer"));
            document.getElementById("result-runs").textContent = "0";
            document.getElementById("result-failures").textContent = "0";
            recorder.detach();
            initAllSuite();
            setCaseScrollTop(getSelectedCase());

            if (contentWindowId) {
                browser.windows.update(contentWindowId, {focused: true});
            }
            declaredVars = {};
            clearScreenshotContainer();
            expectingLabel = null;

            var s_suite = getSelectedSuite();
            var s_case = getSelectedCase();

            $('#passed_record,#failed_record,#disable_record').html(0);


            //zeuz_log.info("Playing test case " + zeuz_testSuite[s_suite.id].title + " / " + zeuz_testCase[s_case.id].title);
            logStartTime();
            play();

            $('#record_wrap,#resume_wrap,#play_all_wrap,#export_wrap,#import_wrap').addClass('disable_action');
        },setTimeout1);
    });

    
    stopButton.addEventListener("click", function() {
        //saveData();
        stop();
    });
    pauseButton.addEventListener("click", pause);
    resumeButton.addEventListener("click", resume);

    playAll.addEventListener('click',function(){
        var setTimeout1 = 0;
        var setTimeout2 = 500;
        if (isPause){
            setTimeout1 = 700;
            setTimeout2 = 1500;
            stop();
        }

        var selected_suite = -1;
        setTimeout(function(){
            /* fetch saved data */
            CustomFunction.FetchChromeCaseData();
            /* Fetch selected suite */
            $('.single-suite-tab').each(function(){
                if($(this).hasClass('current_selected_tab')){
                    selected_suite = $(this).data('suite');
                }
            });
        },setTimeout1);


        setTimeout(function(){
            console.log('selected_suite',selected_suite);
            if(selected_suite != -1){
                console.log('CustomFunction.caseDataArr[selected_suite]',CustomFunction.caseDataArr[selected_suite]);
                var caseDataValues = CustomFunction.caseDataArr[selected_suite].suite_value;
                if(caseDataValues.length > 0){
                    var count = 0;
                    var disableCount = 0;
                    var caseHtml = '';
                    $.each(caseDataValues,function(indx,val){
                        var caseValue = val.case_value;
                        if(caseValue.length > 0){
                            $.each(caseValue,function(singleCaseIndx,singleCaseVal){
                                if(singleCaseVal.is_disable == undefined || singleCaseVal.is_disable == 0){
                                    count++;
                                    caseHtml +=`<tr id="records-`+count+`" class="odd">
                                        <td>
                                            <div style="display: none;">`+singleCaseVal.action+`</div>
                                            <div style="overflow:hidden;height:15px;">`+val.action+`</div>
                                        </td>
                                        <td>
                                            <div style="display: none;">`+singleCaseVal.element+`</div>
                                            <div style="overflow:hidden;height:15px;">`+singleCaseVal.element+`</div>
                                            <datalist>
                                                <option>
                                                    `+singleCaseVal.element+`
                                                </option>
                                            </datalist>
                                        </td>
                                        <td>
                                            <div style="display: none;">`+singleCaseVal.value+`</div>
                                            <div style="overflow:hidden;height:15px;">`+singleCaseVal.value+`</div>
                                        </td>
                                    </tr>`;
                                }else{
                                    disableCount ++;
                                }
                            })
                        }
                    })

                    caseHtml += `<input id="records-count" value="`+count+`" type="hidden">`;
                    caseHtml += `<input id="disable-count" value="`+disableCount+`" type="hidden">`;

                    $('#records-grid').html(caseHtml);
                }

                emptyNode(document.getElementById("logcontainer"));
                document.getElementById("result-runs").textContent = "0";
                document.getElementById("result-failures").textContent = "0";
                recorder.detach();
                initAllSuite();
                setCaseScrollTop(getSelectedCase());

                if (contentWindowId) {
                    browser.windows.update(contentWindowId, {focused: true});
                }
                declaredVars = {};
                clearScreenshotContainer();
                expectingLabel = null;

                var s_suite = getSelectedSuite();
                var s_case = getSelectedCase();
                //zeuz_log.info("Playing test case " + zeuz_testSuite[s_suite.id].title + " / " + zeuz_testCase[s_case.id].title);
                $('#passed_record,#failed_record,#disable_record').html(0);
                logStartTime();
                play();
                $('#record_wrap,#resume_wrap,#replay_wrap,#export_wrap,#import_wrap').addClass('disable_action');
            }
        },setTimeout2);


    })


    playSuiteButton.addEventListener("click", function() {
        //saveData();
        emptyNode(document.getElementById("logcontainer"));
        document.getElementById("result-runs").textContent = "0";
        document.getElementById("result-failures").textContent = "0";
        recorder.detach();
        initAllSuite();

        if (contentWindowId) {
            browser.windows.update(contentWindowId, {focused: true});
        }
        declaredVars = {};
        clearScreenshotContainer();
        playSuite(0);
    });
    playSuitesButton.addEventListener("click", function() {
        //saveData();
        emptyNode(document.getElementById("logcontainer"));
        document.getElementById("result-runs").textContent = "0";
        document.getElementById("result-failures").textContent = "0";
        recorder.detach();
        initAllSuite();
        if (contentWindowId) {
            browser.windows.update(contentWindowId, {focused: true});
        }
        declaredVars = {};
        clearScreenshotContainer();
        playSuites(0);
    });
    selectElementButton.addEventListener("click",function(){
        var button = document.getElementById("selectElementButton");
        if (isSelecting) {
            isSelecting = false;
            button.classList.remove("active");
            browser.tabs.query({
                active: true,
                windowId: contentWindowId
            }).then(function(tabs) {
                browser.tabs.sendMessage(tabs[0].id, {selectMode: true, selecting: false});
            }).catch(function(reason) {
                console.log(reason);
            })
            return;
        }

        isSelecting = true;
        if (isRecording)
            recordButton.click();
        button.classList.add("active")
        browser.tabs.query({
            active: true,
            windowId: contentWindowId
        }).then(function(tabs) {
            if (tabs.length === 0) {
                console.log("No match tabs");
                isSelecting = false;
                button.classList.remove("active");
            } else
                browser.tabs.sendMessage(tabs[0].id, {selectMode: true, selecting: true});
        })
    });
    showElementButton.addEventListener("click", function(){
        try{
            var targetValue = document.getElementById("command-target").value;
            if (targetValue == "auto-located-by-tac") {
                targetValue = document.getElementById("command-target-list").options[0].text;
            }
            browser.tabs.query({
                active: true,
                windowId: contentWindowId
            }).then(function(tabs) {
                if (tabs.length === 0) {
                    console.log("No match tabs");
                } else {
                    browser.webNavigation.getAllFrames({tabId: tabs[0].id})
                        .then(function(framesInfo){
                            var frameIds = [];
                            for (let i = 0; i < framesInfo.length; i++) {
                                frameIds.push(framesInfo[i].frameId)
                            }
                            frameIds.sort();
                            var infos = {
                                "index": 0,
                                "tabId": tabs[0].id,
                                "frameIds": frameIds,
                                "targetValue": targetValue
                            };
                            sendShowElementMessage(infos);
                        });
                }
            });
        } catch (e) {
            console.error(e);
        }
    });
};

function prepareSendNextFrame(infos) {
    if (infos.index == infos.frameIds.length) {
        zeuz_log.error("Element is not found.");
    } else {
        infos.index++;
        sendShowElementMessage(infos);
    }
}

function sendShowElementMessage(infos) {
    browser.tabs.sendMessage(infos.tabId, {
        showElement: true,
        targetValue: infos.targetValue
    }, {
        frameId: infos.frameIds[infos.index]
    }).then(function(response) {
        if (response){
            if (!response.result) {
                prepareSendNextFrame(infos);
            } else {
                let text = infos.index == 0 ? "top" : index.toString() + "(id)";
                zeuz_log.info("Element is found in " + text + " frame.");
            }
        }
    }).catch(function(error) {
        if(error.message == "Could not establish connection. Receiving end does not exist.") {
            prepareSendNextFrame(infos);
        } else {
            zeuz_log.error("Unknown error");
        }
    });
}

function enableClick() {
    document.getElementById("pause").disabled = true;
    document.getElementById('testCase-grid').style.pointerEvents = 'auto';
    document.getElementById('command-container').style.pointerEvents = 'auto';
}

function cleanCommandToolBar() {
    $("#command-command").val("");
    $("#command-target").val("");
    $("#command-value").val("");
}

function disableClick() {
    document.getElementById("pause").disabled = false;
    document.getElementById('testCase-grid').style.pointerEvents = 'none';
    document.getElementById('command-container').style.pointerEvents = 'none';
}


function play() {

    addSampleDataToScreenshot();
    initializePlayingProgress()
        .then(executionLoop)
        .then(finalizePlayingProgress)
        .catch(catchPlayingError);
}

function stop() {

    if (isPause){
        isPause = false;
        switchPR();
    }

    isPlaying = false;
    isPlayingSuite = false;
    isPlayingAll = false;
    switchPS();
    zeuz_log.info("Stop executing");
    initAllSuite();
    document.getElementById("result-runs").textContent = "0";
    document.getElementById("result-failures").textContent = "0";
    finalizePlayingProgress();
}

function pause() {
    if (isPlaying) {
        zeuz_log.info("Pausing");
        isPause = true;
        isPlaying = false;
        switchPR();
    }
}

function resume() {
    if(currentTestCaseId!=getSelectedCase().id)
        setSelectedCase(currentTestCaseId);
    if (isPause) {

        /* Custom */
        if (contentWindowId) {
            browser.windows.update(contentWindowId, {focused: true});
        }
         /* Custom */

        zeuz_log.info("Resuming");
        isPlaying = true;
        isPause = false;
        extCommand.attach();
        switchPR();
        disableClick();
        executionLoop()
            .then(finalizePlayingProgress)
            .catch(catchPlayingError);
    }
}

function playAfterConnectionFailed() {
    if (isPlaying) {
        initializeAfterConnectionFailed()
            .then(executionLoop)
            .then(finalizePlayingProgress)
            .catch(catchPlayingError);
    }
}

function initializeAfterConnectionFailed() {
    disableClick();

    isRecording = false;
    isPlaying = true;

    commandType = "preparation";
    pageCount = ajaxCount = domCount = implicitCount = 0;
    pageTime = ajaxTime = domTime = implicitTime = "";

    caseFailed = false;

    currentTestCaseId = getSelectedCase().id;
    var commands = getRecordsArray();

    return Promise.resolve(true);
}

function initAllSuite() {
    cleanCommandToolBar();
    var suites = document.getElementById("testCase-grid").getElementsByClassName("message");
    var length = suites.length;
    for (var k = 0; k < suites.length; ++k) {
        var cases = suites[k].getElementsByTagName("p");
        for (var u = 0; u < cases.length; ++u) {
            $("#" + cases[u].id).removeClass('fail success');
        }
    }
}

function playSuite(i) {
    isPlayingSuite = true;
    var cases = getSelectedSuite().getElementsByTagName("p");
    var length = cases.length;
    if (i < length) {
        setSelectedCase(cases[i].id);
        setCaseScrollTop(getSelectedCase());
        $('#passed_record,#failed_record,#disable_record').html(0);
        //zeuz_log.info("Playing test case " + zeuz_testSuite[getSelectedSuite().id].title + " / " + zeuz_testCase[cases[i].id].title);
        logStartTime();
        play();
        nextCase(i);
    } else {
        isPlayingSuite = false;
        switchPS();
    }
}

function nextCase(i) {
    if (isPlaying || isPause) setTimeout(function() {
        nextCase(i);
    }, 500);
    else if(isPlayingSuite) playSuite(i + 1);
}

function nextSuite(i) {
    if (isPlayingSuite) setTimeout(function() {
        nextSuite(i);
    }, 2000);
    else if(isPlayingAll) playSuites(i + 1);
}

function executeCommand(index) {
    var id = parseInt(index) - 1;
    var commands = getRecordsArray();
    var commandName = getCommandName(commands[id]);
    var commandTarget = getCommandTarget(commands[id]);
    var commandValue = getCommandValue(commands[id]);

    if (commandTarget.includes("d-XPath")) {
        zeuz_log.info("Executing: | " + commandName + " | " + getCommandTarget(commands[id], true) + " | " + commandValue + " |");
    } else {
        if (commandName !== '#') {
            zeuz_log.info("Executing: | " + commandName + " | " + commandTarget + " | " + commandValue + " |");
        }
    }

    initializePlayingProgress(true);

    setColor(id + 1, "executing");

    browser.tabs.query({
            windowId: extCommand.getContentWindowId(),
            active: true
        })
        .then(function(tabs) {
            return browser.tabs.sendMessage(tabs[0].id, {
                commands: commandName,
                target: commandTarget,
                value: commandValue
            }, {
                frameId: extCommand.getFrameId(tabs[0].id)
            })
        })
        .then(function(result) {
            if (result.result != "success") {
                zeuz_log.error(result.result);
                setColor(id + 1, "fail");
                if (!result.result.includes("did not match")) {
                    return true;
                }
            } else {
                setColor(id + 1, "success");
            }
        })

    finalizePlayingProgress();
}

function playSuites(i) {
    isPlayingAll = true;
    var suites = document.getElementById("testCase-grid").getElementsByClassName("message");
    var length = suites.length;
    if (i < length) {
        if (suites[i].id.includes("suite")) {
            setSelectedSuite(suites[i].id);
            playSuite(0);
        }
        nextSuite(i);
    } else {
        isPlayingAll = false;
        switchPS();
    }
}

function cleanStatus() {
    var commands = getRecordsArray();
    for (var i = 0; i < commands.length; ++i) {
        commands[i].setAttribute("class", "");
        commands[i].getElementsByTagName("td")[0].classList.remove("stopping");
    }
    classifyRecords(1, commands.length);
}

function initializePlayingProgress(isDbclick) {

    blockStack = [];

    disableClick();

    isRecording = false;
    isPlaying = true;

    switchPS();

    currentPlayingCommandIndex = currentPlayingFromHereCommandIndex - 1;
    currentPlayingFromHereCommandIndex = 0;

    pageCount = ajaxCount = domCount = implicitCount = 0;
    pageTime = ajaxTime = domTime = implicitTime = "";

    caseFailed = false;

    currentTestCaseId = getSelectedCase().id;

    if (!isDbclick) {
        $("#" + currentTestCaseId).removeClass('fail success');
    }
    var commands = getRecordsArray();

    cleanStatus();

    return extCommand.init();
}

function executionLoop() {
    let commands = getRecordsArray();
    handleDisplayVariables();

    if (currentPlayingCommandIndex + 1 >= commands.length) {
        if (!caseFailed) {
             setColor(currentTestCaseId, "success");
            logEndTime();
            zeuz_log.info("Test case passed");
        } else {
            caseFailed = false;
        }
        return true;
    }

    if (commands[currentPlayingCommandIndex + 1].getElementsByTagName("td")[0].classList.contains("break")
        && !commands[currentPlayingCommandIndex + 1].getElementsByTagName("td")[0].classList.contains("stopping")) {
        commands[currentPlayingCommandIndex + 1].getElementsByTagName("td")[0].classList.add("stopping");
        zeuz_log.info("Breakpoint: Stop.");
        pause();
        return Promise.reject("shutdown");
    }

    if (!isPlaying) {
        cleanStatus();
        return Promise.reject("shutdown");
    }

    if (isPause) {
        return Promise.reject("shutdown");
    }

    currentPlayingCommandIndex++;

    if (commands[currentPlayingCommandIndex].getElementsByTagName("td")[0].classList.contains("stopping")) {
        commands[currentPlayingCommandIndex].getElementsByTagName("td")[0].classList.remove("stopping");
    }

    let commandName = getCommandName(commands[currentPlayingCommandIndex]);
    let commandTarget = getCommandTarget(commands[currentPlayingCommandIndex]);
    let commandValue = getCommandValue(commands[currentPlayingCommandIndex]);

    if (commandName == "") {
        return Promise.reject("no command name");
    }

    setColor(currentPlayingCommandIndex + 1, "executing");

    //return delay($('#slider').slider("option", "value")).then(function () {
    return delay(parseInt($('#playback_select').val())).then(function () {
        if (isExtCommand(commandName)) {
            zeuz_log.info("Executing: | " + commandName + " | " + commandTarget + " | " + commandValue + " |");
            commandName = formalCommands[commandName.toLowerCase()];
            let upperCase = commandName.charAt(0).toUpperCase() + commandName.slice(1);
            commandTarget = convertVariableToString(commandTarget);
            return (extCommand["do" + upperCase](commandTarget, commandValue))
               .then(function() {
                    setColor(currentPlayingCommandIndex + 1, "success");
               }).then(executionLoop);
        } else {
            return doPreparation()
               .then(doPrePageWait)
               .then(doPageWait)
               .then(doAjaxWait)
               .then(doDomWait)
               .then(doCommand)
               .then(executionLoop)
        }
    });
}

function delay(t) {
    return new Promise(function(resolve) {
        setTimeout(resolve, t)
    });
 }

function finalizePlayingProgress() {
    if (!isPause) {
        enableClick();
        extCommand.clear();
    }
    setTimeout(function() {
        isPlaying = false;
        switchPS();
    }, 500);
}

document.addEventListener("dblclick", function(event) {
    var temp = event.target;
    cleanCommandToolBar();
    while (temp.tagName.toLowerCase() != "body") {
        if (/records-(\d)+/.test(temp.id)) {
            var index = temp.id.split("-")[1];
            recorder.detach();
            executeCommand(index);
        }
        if (temp.id == "command-grid") {
            break;
        } else temp = temp.parentElement;
    }
});

function playDisable(setting) {
    document.getElementById("record").disabled = setting;
    document.getElementById("playback").disabled = setting;
    document.getElementById("playSuite").disabled = setting;
    document.getElementById("playSuites").disabled = setting;
    document.getElementById("new").disabled = setting;
    document.getElementById("export").disabled = setting;
}

function switchPS() {
    if ((isPlaying||isPause)||isPlayingSuite||isPlayingAll) {
        playDisable(true);
        //document.getElementById("playback").style.display = "none";
        //document.getElementById("stop").style.display = "";

        $('#play_wrap').hide();
        $('#pause_wrap').show();
        $('#record_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').removeClass('disable_action');
    } else {
        playDisable(false);
        //document.getElementById("playback").style.display = "";
        //document.getElementById("stop").style.display = "none";

        $('#play_wrap').show();
        $('#pause_wrap').hide();

        $('#record_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').removeClass('disable_action');
        /* Reload the hidden selected html */
        CustomFunction.LoadTheRecordDataHtml();

    }
}

function switchPR() {
    if (isPause) {
        //document.getElementById("pause").style.display = "none";
        //document.getElementById("resume").style.display = "";

        $('#pause_wrap').hide();
        $('#resume_wrap').show();
        $('#record_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').removeClass('disable_action');
    } else {
        //document.getElementById("pause").style.display = "";
        //document.getElementById("resume").style.display = "none";

        $('#pause_wrap').show();
        $('#resume_wrap').hide();
        $('#record_wrap,#resume_wrap,#replay_wrap,#play_all_wrap,#export_wrap,#import_wrap').addClass('disable_action');
    }
}

function catchPlayingError(reason) {
    console.log('Playing error', reason);
    if (isReceivingEndError(reason)) {
        commandType = "preparation";
        setTimeout(function() {
            currentPlayingCommandIndex--;
            playAfterConnectionFailed();
        }, 100);
    } else if (reason == "shutdown") {
        return;
    } else {
        extCommand.clear();
        enableClick();
        zeuz_log.error(reason);

        if (currentPlayingCommandIndex >= 0) {
            setColor(currentPlayingCommandIndex + 1, "fail");
        }
        setColor(currentTestCaseId, "fail");
        logEndTime();
        zeuz_log.info("Test case failed");
        setTimeout(function() {
            isPlaying = false;
            switchPS();
        }, 500);
    }
}

function doPreparation() {
    if (!isPlaying) {
        currentPlayingCommandIndex--;
        return Promise.reject("shutdown");
    }
    return extCommand.sendCommand("waitPreparation", "", "")
        .then(function() {
            return true;
        })
}


function doPrePageWait() {
    if (!isPlaying) {
        currentPlayingCommandIndex--;
        return Promise.reject("shutdown");
    }
    return extCommand.sendCommand("prePageWait", "", "")
       .then(function(response) {
           if (response && response.new_page) {
               return doPrePageWait();
           } else {
               return true;
           }
       })
}

function doPageWait() {
    if (!isPlaying) {
        currentPlayingCommandIndex--;
        return Promise.reject("shutdown");
    }

    return extCommand.sendCommand("pageWait", "", "")
        .then(function(response) {
            if (pageTime && (Date.now() - pageTime) > 30000) {
                zeuz_log.error("Page Wait timed out after 30000ms");
                pageCount = 0;
                pageTime = "";
                return true;
            } else if (response && response.page_done) {
                pageCount = 0;
                pageTime = "";
                return true;
            } else {
                pageCount++;
                if (pageCount == 1) {
                    pageTime = Date.now();
                    zeuz_log.info("Wait for the new page to be fully loaded");
                }
                return doPageWait();
            }
        })
}

function doAjaxWait() {
    if (!isPlaying) {
        currentPlayingCommandIndex--;
        return Promise.reject("shutdown");
    }
    return extCommand.sendCommand("ajaxWait", "", "")
        .then(function(response) {
            if (ajaxTime && (Date.now() - ajaxTime) > 30000) {
                zeuz_log.error("Ajax Wait timed out after 30000ms");
                ajaxCount = 0;
                ajaxTime = "";
                return true;
            } else if (response && response.ajax_done) {
                ajaxCount = 0;
                ajaxTime = "";
                return true;
            } else {
                ajaxCount++;
                if (ajaxCount == 1) {
                    ajaxTime = Date.now();
                    zeuz_log.info("Wait for all ajax requests to be done");
                }
                return doAjaxWait();
            }
        })
}

function doDomWait() {
    if (!isPlaying) {
        currentPlayingCommandIndex--;
        return Promise.reject("shutdown");
    }
    return extCommand.sendCommand("domWait", "", "")
        .then(function(response) {
            if (domTime && (Date.now() - domTime) > 30000) {
                zeuz_log.error("DOM Wait timed out after 30000ms");
                domCount = 0;
                domTime = "";
                return true;
            } else if (response && (Date.now() - response.dom_time) < 400) {
                domCount++;
                if (domCount == 1) {
                    domTime = Date.now();
                    zeuz_log.info("Wait for the DOM tree modification");
                }
                return doDomWait();
            } else {
                domCount = 0;
                domTime = "";
                return true;
            }
        })
}

function doCommand() {
    let commands = getRecordsArray();
    let commandName = getCommandName(commands[currentPlayingCommandIndex]);
	if(commandName.indexOf("${") !== -1){
		commandName = convertVariableToString(commandName);
	}
    var formalCommandName = formalCommands[commandName.trim().toLowerCase()];
    if (formalCommandName) {
        commandName = formalCommandName;
    }
    let commandTarget = getCommandTarget(commands[currentPlayingCommandIndex]);
    let commandValue = getCommandValue(commands[currentPlayingCommandIndex]);

    if (implicitCount == 0) {
        if (commandTarget.includes("d-XPath")) {
            zeuz_log.info("Executing: | " + commandName + " | " + getCommandTarget(commands[currentPlayingCommandIndex], true) + " | " + commandValue + " |");
        } else {
            if (commandName !== '#') {
                zeuz_log.info("Executing: | " + commandName + " | " + commandTarget + " | " + commandValue + " |");
            }
        }
    }

    if (!isPlaying) {
        currentPlayingCommandIndex--;
        return Promise.reject("shutdown");
    }

    let p = new Promise(function(resolve, reject) {
        let count = 0;
        let interval = setInterval(function() {
            if (!isPlaying) {
                currentPlayingCommandIndex--;
                reject("shutdown");
                clearInterval(interval);
            }
            var limit = 30000/10;
            if (count > limit) {
                zeuz_log.error("Timed out after 30000ms");
                reject("Window not Found");
                clearInterval(interval);
            }
            if (!extCommand.getPageStatus()) {
                if (count == 0) {
                    zeuz_log.info("Wait for the new page to be fully loaded");
                }
                count++;
            } else {
                resolve();
                clearInterval(interval);
            }
        }, 10);
    });
    return p.then(function() {
            if (commandName === '#') {
                return {
                    result: 'success'
                };
            }
            if (expectingLabel !== null && commandName !== 'label') {
                return {
                    result: 'success'
                };
            }
            var originalCommandTarget = commandTarget;
            if (!blockStack) {
                blockStack = [];
            }
            var lastBlock;
            if (blockStack.length == 0) {
                lastBlock = undefined;
            } else {
                lastBlock = blockStack[blockStack.length - 1];
            }
            var skipped = lastBlock &&
                    (lastBlock.dummy ||
                    (lastBlock.isLoadVars && lastBlock.done) ||
                    (lastBlock.isIf && !lastBlock.condition) ||
                    (lastBlock.isWhile && !lastBlock.condition));
            if (skipped && (['loadVars', 'endLoadVars', 'if', 'else', 'elseIf', 'endIf', 'while', 'endWhile'].indexOf(commandName) < 0)) {
                return {
                    result: 'success'
                };
            } else if (skipped && (['loadVars', 'if', 'while'].indexOf(commandName) >= 0)) {
                blockStack.push({
                    dummy: true
                });
                return {
                    result: 'success'
                };
            } else if (skipped && (['endLoadVars', 'endIf', 'endWhile'].indexOf(commandName) >= 0)) {
                if (lastBlock.dummy) {
                    blockStack.pop();
                    return {
                        result: 'success'
                    };
                }
            } else if (skipped && (['else', 'elseIf'].indexOf(commandName) >= 0)) {
                if (lastBlock.dummy) {
                    return {
                        result: 'success'
                    };
                }
            }
            if(commandValue.indexOf("${") !== -1){
                commandValue = convertVariableToString(commandValue);
            }
            if(commandTarget.indexOf("${") !== -1){
                commandTarget = convertVariableToString(commandTarget);
            }
            if ((commandName === 'storeEval') || (commandName === 'storeEvalAndWait')) {
                commandTarget = expandForStoreEval(commandTarget);
            }
            if (commandName === 'if') {
                var condition = evalIfCondition(commandTarget);
                blockStack.push({
                    isIf: true,
                    condition: condition,
                    met: condition
                });
                return {
                    result: 'success'
                };
            }
            if (commandName === 'else') {
                if (lastBlock.met) {
                    lastBlock.condition = false;
                } else {
                    lastBlock.condition = !lastBlock.condition;
                    lastBlock.met = lastBlock.condition;
                }
                return {
                    result: 'success'
                };
            }
            if (commandName === 'elseIf') {
                if (lastBlock.met) {
                    lastBlock.condition = false;
                } else {
                    lastBlock.condition = evalIfCondition(commandTarget);
                    lastBlock.met = lastBlock.condition;
                }
                return {
                    result: 'success'
                };
            }
            if (commandName === 'endIf') {
                // end block
                blockStack.pop();
                return {
                    result: 'success'
                };
            }
            if (commandName === 'while') {
                blockStack.push({
                    isWhile: true,
                    index: currentPlayingCommandIndex,
                    condition: evalIfCondition(commandTarget),
                    originalCommandTarget: originalCommandTarget
                });
                return {
                    result: 'success'
                };
            }
            if (commandName === 'endWhile') {
                var lastBlockCommandTarget = lastBlock.originalCommandTarget;
                if(lastBlockCommandTarget.indexOf("${") !== -1){
                    lastBlockCommandTarget = convertVariableToString(lastBlockCommandTarget);
                }
                lastBlock.condition = evalIfCondition(lastBlockCommandTarget);
                if (lastBlock.condition) {
                    currentPlayingCommandIndex = lastBlock.index;
                    return {
                        result: 'success'
                    };
                } else {
                    blockStack.pop();
                    return {
                        result: 'success'
                    };
                }
            }
            if (commandName === 'loadVars') {
                var parsedData = parseData(commandTarget);
                var data = parsedData.data;
                var block = {
                    isLoadVars: true,
                    index: currentPlayingCommandIndex,
                    currentLine: 0, // line of data
                    data: data,
                    type: parsedData.type,
                    done: data.length == 0 // done if empty file
                };
                blockStack.push(block);
                if (!block.done) { // if not done get next line
                    var line = block.data[block.currentLine];
                    $.each(line, function(key, value) {
                        declaredVars[key] = value;
                    });
                }
                return {
                    result: 'success'
                };
            }
            if (commandName === 'endLoadVars') {
                lastBlock.currentLine++;
                lastBlock.done = lastBlock.currentLine >= lastBlock.data.length; // out of data
                if (lastBlock.done) {
                    blockStack.pop(); // quit block
                } else {
                    currentPlayingCommandIndex = lastBlock.index; // back to command after while
                    var line = lastBlock.data[lastBlock.currentLine] // next data
                    $.each(line, function(key, value) {
                        declaredVars[key] = value;
                    });
                }
                return {
                    result: 'success'
                };
            }
            if (commandName === 'label') {
                var label = currentTestCaseId + '-' + commandTarget;
                labels[label] = currentPlayingCommandIndex;
                if (expectingLabel === label) {
                    expectingLabel = null;
                }
                return {
                    result: 'success'
                };
            }
            if (commandName === 'gotoIf') {
                if (evalIfCondition(commandTarget)) {
                    var label = currentTestCaseId + '-' + commandValue;
                    var jumpTo = labels[label];
                    if (jumpTo === undefined) {
                        expectingLabel = label;
                    } else {
                        currentPlayingCommandIndex = jumpTo;
                    }
                    return {
                        result: 'success'
                    };
                } else {
                    return {
                        result: 'success'
                    };
                }
            }
            if (commandName === 'gotoLabel') {
                var label = currentTestCaseId + '-' + commandTarget;
                var jumpTo = labels[label];
                if (jumpTo === undefined) {
                    expectingLabel = label;
                } else {
                    currentPlayingCommandIndex = jumpTo;
                }
                return {
                    result: 'success'
                };
            }
            if (commandName === 'storeCsv') {
                var tokens = commandTarget.split(',');
                var csvValue = parseData(tokens[0]).data[parseInt(tokens[1])][tokens[2]];
                zeuz_log.info("Store '" + csvValue + "' into '" + commandValue + "'");
                declaredVars[commandValue] = csvValue;
                return {
                    result: 'success'
                };
            }
            if (isWindowMethodCommand(commandName))
            {
                return extCommand.sendCommand(commandName, commandTarget, commandValue, true);
            }
            return extCommand.sendCommand(commandName, commandTarget, commandValue);
        })
        .then(function(result) {
            if (result.result != "success") {

                var originalCurrentPlayingCommandIndex = currentPlayingCommandIndex;

                // implicit
                if (result.result.match(/Element[\s\S]*?not found/)) {
                    if (implicitTime && (Date.now() - implicitTime > 10000)) {
                        zeuz_log.error("Implicit Wait timed out after 10000ms");
                        implicitCount = 0;
                        implicitTime = "";
                    } else {
                        implicitCount++;
                        if (implicitCount == 1) {
                            zeuz_log.info("Wait until the element is found");
                            implicitTime = Date.now();
                        }
                        return doCommand();
                    }
                }

                implicitCount = 0;
                implicitTime = "";
                zeuz_log.error(result.result);
                setColor(currentPlayingCommandIndex + 1, "fail");
                setColor(currentTestCaseId, "fail");
                if (commandName.includes("verify") && result.result.includes("did not match")) {
                    setColor(currentPlayingCommandIndex + 1, "fail");
                } else {
                    logEndTime();
                    zeuz_log.info("Test case failed");
                    caseFailed = true;
                    currentPlayingCommandIndex = commands.length;
                }
                return browser.runtime.sendMessage({
                    captureEntirePageScreenshot: true,
                    captureWindowId: extCommand.getContentWindowId()
                }).then(function(captureResponse) {
                    addToScreenshot(captureResponse.image, 'fail-' + zeuz_testCase[currentTestCaseId].title + '-' + originalCurrentPlayingCommandIndex);
                });
            } else {
                setColor(currentPlayingCommandIndex + 1, "success");
                if (result.capturedScreenshot) {
                    addToScreenshot(result.capturedScreenshot, result.capturedScreenshotTitle);
                }
            }
        })
}

function isReceivingEndError(reason) {
    if (reason == "TypeError: response is undefined" ||
        reason == "Error: Could not establish connection. Receiving end does not exist." ||
        reason.message == "Could not establish connection. Receiving end does not exist." ||
        reason.message == "The message port closed before a reponse was received." ||
        reason.message == "The message port closed before a response was received." )
        return true;
    return false;
}

function isWindowMethodCommand(command) {
    if (command == "answerOnNextPrompt"
        || command == "chooseCancelOnNextPrompt"
        || command == "assertPrompt"
        || command == "chooseOkOnNextConfirmation"
        || command == "chooseCancelOnNextConfirmation"
        || command == "assertConfirmation"
        || command == "assertAlert")
        return true;
    return false;
}

function enableButton(buttonId) {
    document.getElementById(buttonId).disabled = false;
}

function disableButton(buttonId) {
    document.getElementById(buttonId).disabled = true;
}

function convertVariableToString(variable){
    var originalVariable = variable;
    let frontIndex = variable.indexOf("${");
    let newStr = "";
    while(frontIndex !== -1){
        let prefix = variable.substring(0,frontIndex);
        let suffix = variable.substring(frontIndex);
        let tailIndex = suffix.indexOf("}");
        if (tailIndex >= 0) {
            let suffix_front = suffix.substring(0,tailIndex + 1);
            let suffix_tail = suffix.substring(tailIndex + 1);
            newStr += prefix + xlateArgument(suffix_front);
            variable = suffix_tail;
            frontIndex = variable.indexOf("${");
        } else {
            frontIndex = -1;
        }
    }
    var expanded = newStr + variable;
    zeuz_log.info("Expand variable '" + originalVariable + "' into '" + expanded + "'");
    return expanded;
}
