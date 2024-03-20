var extCommand = new ExtCommand();

window.onload = function() {
    var recordButton = document.getElementById("record");
    setTimeout(()=>{    // Add listener after 2 sec
        recordButton.addEventListener("click", function(){
            $('#records-grid').html('<input id="records-count" type="hidden" value="0">'); 
            isRecording = $('#record_label')[0].textContent == 'Record';
            $('#save_wrap, #run_this_button, #run_wrap, #login_wrap').attr('disabled', true).css('opacity',0.5);
            if (isRecording) {
                recorder.attach();
                notificationCount = 0;
                if (contentWindowId) {
                    browserAppData.windows.update(contentWindowId, {focused: true});
                }
                browserAppData.tabs.query({windowId: extCommand.getContentWindowId(), url: "<all_urls>"})
                .then(function(tabs) {
                    try {
                        console.log("attachRecorder=true sendMessage() call");
                        for(let tab of tabs) {
                            browserAppData.tabs.sendMessage(tab.id, {attachRecorder: true})
                            .catch((error)=>{
                                console.log('error in sendMessage from tab.url=', tab.url);
                                console.error(error);
                                if (tab.url.startsWith("http://") || tab.url.startsWith("https://")){
                                    msg = (tabs.length == 1) ?
                                    `Recorder Disconnected!\n  1. Close the Recorder\n  2. Refresh the page (optional)\n  3. Open Recorder again` :
                                    `Recorder Disconnected!\n  1. Close the Recorder\n  2. Close all tabs except the main tab\n  3. Refresh the page (optional)\n  4. Open Recorder again` ;
                                    alert(msg)
                                }
                            });
                        }
                    } catch (error) {
                        console.error(error);
                    }
                    
                });
            }
            else {
                $('#save_wrap, #run_this_button, #run_wrap, #login_wrap').removeAttr('disabled').css('opacity',1);
                recorder.detach();
                // CustomFunction.SaveCaseDataAsJson();
                browserAppData.tabs.query({windowId: extCommand.getContentWindowId(), url: "<all_urls>"})
                .then(function(tabs) {
                    for(let tab of tabs) {
                        browserAppData.tabs.sendMessage(tab.id, {detachRecorder: true});
                    }
                });
            }
        })
    },0)
};
