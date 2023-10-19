/* start the zeuz editor function */
var contentWindowId;
var selfWindowId = -1;
var notificationCount = 0;
var recorder = new BackgroundRecorder();
var isPlaying = false;
var isRecording = false;

class Editor {

}

function handleMessage(message, sender, sendResponse) {
    if (message.selectTarget) {

        var target = message.target;
        var locatorString = target[0][0];
        if (locatorString.includes("d-XPath")) locatorString = "auto-located-by-tac";

        document.getElementById("command-target").value = locatorString;
        var target_dropdown = document.getElementById("target-dropdown");
        var command_target_list = document.getElementById("command-target-list");
        emptyNode(target_dropdown);
        emptyNode(command_target_list);

        var locatorList = document.createElement("datalist");
        for (var m = 0; m < message.target.length; ++m) {
            var option = document.createElement("option");
            option.textContent = message.target[m][0];
            target_dropdown.appendChild(option.cloneNode(true));
            command_target_list.appendChild(option);
        }

        var selectedRecordId = getSelectedRecord();

        if (selectedRecordId != "") {
            var selectedRecord = document.getElementById(selectedRecordId);
            var datalist = selectedRecord.getElementsByTagName("td")[1].getElementsByTagName("datalist")[0];

            emptyNode(datalist);
            for (var m = 0; m < message.target.length; ++m) {
                var option = document.createElement("option");
                option.textContent = message.target[m][0];
                datalist.appendChild(option);
            }

            var node = getTdShowValueNode(selectedRecord, 1);
            if (node.childNodes && node.childNodes[0])
                node.removeChild(node.childNodes[0]);
            node.appendChild(document.createTextNode(locatorString));

            node = getTdRealValueNode(selectedRecord, 1);
            if (node.childNodes && node.childNodes[0])
                node.removeChild(node.childNodes[0]);
            node.appendChild(document.createTextNode(locatorString));

        } else if (document.getElementsByClassName("record-bottom active").length > 0) {

            addCommandAuto("", target, "");
        }

        return;
    }
    if (message.cancelSelectTarget) {
        var button = document.getElementById("selectElementButton");
        isSelecting = false;

        button.classList.remove("active");

        browser.tabs.sendMessage(sender.tab.id, {selectMode: true, selecting: false});
        return;
    }

    if (message.attachRecorderRequest) {
        if (isRecording && !isPlaying) {
            browser.tabs.sendMessage(sender.tab.id, {attachRecorder: true});
        }
        return;
    }
}

function notification(command, target, value) {
    let tempCount = String(notificationCount);
    notificationCount++;

    browser.notifications.create(tempCount, {
        "type": "basic",
        "iconUrl": "assets/images/small_logo.png",
        "title": "Command Recorded",
        "message": "command: " + String(command) + "\ntarget: " + tacPreprocess(String(target[0][0])) + "\nvalue: " + String(value)
    });

    setTimeout(function() {
        browser.notifications.clear(tempCount);
    }, 15000);
}

function tacPreprocess(target) {
    if (target.includes("d-XPath")) return "auto-located-by-tac";
    return target;
}


browser.runtime.onMessage.addListener(handleMessage);

browser.runtime.onMessage.addListener(function contentWindowIdListener(message) {
    if (message.selfWindowId != undefined && message.commWindowId != undefined) {
        selfWindowId = message.selfWindowId;
        contentWindowId = message.commWindowId;
        extCommand.setContentWindowId(contentWindowId);
        recorder.setOpenedWindow(contentWindowId);
        recorder.setSelfWindowId(selfWindowId);
        browser.runtime.onMessage.removeListener(contentWindowIdListener);
    }
})
