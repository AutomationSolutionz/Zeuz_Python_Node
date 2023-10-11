/* Start Zuez functions */
var tempCommand = [];
var isOnCommandContainer = false;


document.getElementById("grid-add").addEventListener("click", function() {
    addCommandManu("", [
        [""]
    ], "");
}, false);

document.getElementById("grid-deleteAll").addEventListener("click", function() {
    if (window.confirm('Are you sure you want to delete all test steps?')) {
        var selectedNode = document.getElementById("records-grid").getElementsByTagName("TR");
        for(var i=selectedNode.length;i>0;i--){
            deleteCommand("records-" + i);
        }
    }
}, false);

document.getElementById("grid-delete").addEventListener("click", function() {
    deleteCommand(getSelectedRecord());
}, false);

document.getElementById("grid-copy").addEventListener("click", function(event) {
    copyCommand();
}, false);

document.getElementById("grid-paste").addEventListener("click", function() {
    pasteCommand();
}, false);

document.getElementById("grid-breakpoint").addEventListener("click",function() {
    setBreakpoint(getSelectedRecord());
}, false);

document.getElementById("command-container").addEventListener("click", function(event) {
    document.getElementById("command-command").blur();
    document.getElementById("command-target").blur();
    document.getElementById("command-value").blur();
});

document.getElementById("command-container").addEventListener("click", function(event) {
    event.stopPropagation();
    isOnCommandContainer = true;
})

document.addEventListener("click", function(event) {
    isOnCommandContainer = false;
});

$(document).on("contextmenu", function(event) {

    $(".menu").css("left", event.pageX);
    $(".menu").css("top", event.pageY);

    if (event.target.id == "testCase-container") {
        event.preventDefault();
        $("#suite-grid-menu").show();
        return;
    }
    $('.tempChild').remove();
    var temp = event.target;
    var inCommandGrid = false;
    while (temp.tagName.toLowerCase() != "body") {
        if (/records-(\d)+/.test(temp.id)) {
            var exe = document.createElement("li");
            exe.classList.add("tempChild");
            var a = document.createElement("a");
            a.setAttribute("href", "#");
            a.textContent = "Play This Command";
            exe.appendChild(a);
            var index = temp.id.split("-")[1];
            exe.addEventListener("click", function(event) {
                executeCommand(index);
            }, true);

            document.getElementById("command-grid-menu").childNodes[1].appendChild(exe);

            exe = document.createElement("li");
            exe.classList.add("tempChild");
            a = document.createElement("a");
            a.setAttribute("href", "#");
            a.textContent = "Play From Here";
            exe.appendChild(a);
            index = temp.id.split("-")[1];
            exe.addEventListener("click", function(event) {
                currentPlayingFromHereCommandIndex = parseInt(index) - 1;
                $('#playback').click();
            }, true);

            document.getElementById("command-grid-menu").childNodes[1].appendChild(exe);
        }
        if (temp.id == "command-grid" || temp.className.search("record-bottom") >= 0) {
            inCommandGrid = true;
            break;
        } else {
            temp = temp.parentElement;
        }
    }
    if (inCommandGrid) {
        event.preventDefault();
        $("#command-grid-menu").show();
    };
});



$(document).on("mousedown", function(e) {
    if (!$(e.target).parents(".menu").length > 0) $(".menu").hide();
    else setTimeout(function() { $(".menu").hide(); }, 500);
});


function stopNativeEvent(event) {
    event.preventDefault();
    event.stopPropagation();
}

document.addEventListener("keydown", function(event) {
    var keyNum;
    if(window.event) {
        keyNum = event.keyCode;
    } else if(event.which) {
        keyNum = event.which;
    }

    if (keyNum == 123) {
        return;
    } else if (event.target.tagName.toLowerCase() == "input") {
        return;
    }

    switch (keyNum) {
        case 38:
            selectForeRecord();
            break;
        case 40:
            selectNextRecord();
            break;
        default:
            break;
    }

    if (event.ctrlKey) {
        if (!isOnCommandContainer && (keyNum == 67 || keyNum == 86)) {
            return;
        }
        stopNativeEvent(event);
        switch (keyNum) {
            case 65:
                var recordNode = document.getElementById("records-grid").getElementsByTagName("TR");
                for (let i=0 ; i<recordNode.length ; i++) {
                    recordNode[i].classList.add("selectedRecord");
                }
                break;
            case 66: // Ctrl + T
                setBreakpoint(getSelectedRecord());
                break;
            case 67: // Ctrl + C
                copyCommand();
                break;
            case 73: // Ctrl + I
                $("#grid-add").click();
                break;
            case 79: // Ctrl + O
                $('#load-testSuite-hidden').click();
                break;
            case 80: // Ctrl + P
                $("#playback").click();
                break;
            case 83: // Ctrl + S
                $("#save-testSuite").click();
                break;
            case 86: // Ctrl + V
                pasteCommand();
                break;
            case 88: // Ctrl + X
                copyCommand();
                let selectedRecords = getSelectedRecords();
                for(let i=selectedRecords.length-1 ; i>=0 ; i--){
                    deleteCommand(selectedRecords[i].id);
                }
                break;
            default:
                break;
        }
    }
}, false);

function setBreakpoint(selected_ID) {
    if (selected_ID) {
        var current_node = document.getElementById(selected_ID).getElementsByTagName("td")[0];
        if (!current_node.classList.contains("break")) {
            current_node.classList.add("break");
        } else {
            current_node.classList.remove("break");
        }
    }
}
function copyCommand() {
    tempCommand = [];
    let ref = getSelectedRecords();
    let targetOptions;
    let showTarget;
    for (let i=0 ; i<ref.length ; i++) {
        showTarget = ref[i].getElementsByTagName("td")[1].getElementsByTagName("div")[1].textContent;
        targetOptions = ref[i].getElementsByTagName("td")[1]
            .getElementsByTagName("datalist")[0]
            .getElementsByTagName("option");
        let targetElements = [];
        let tempTarget;
        for (let j=0 ; j<targetOptions.length ; j++) {
            tempTarget = targetOptions[j].text;
            if (showTarget == tempTarget) {
                targetElements.splice(0, 0, [tempTarget]);
            } else {
                targetElements.push([tempTarget]);
            }
        }
        tempCommand[i] = {
            "command": getCommandName(ref[i]),
            "test": getCommandTarget(ref[i]),
            "target": targetElements,
            "value": getCommandValue(ref[i])
        };
    }
}

function pasteCommand() {
    if (tempCommand.length > 0) {
        if (getSelectedRecords().length == 0) {
            for (let i=0 ; i<tempCommand.length ; i++) {
                addCommandManu(tempCommand[i]["command"], tempCommand[i]["target"], tempCommand[i]["value"]);
            }
            return;
        }
        for (let i=tempCommand.length-1 ; i>=0 ; i--) {
            addCommandManu(tempCommand[i]["command"], tempCommand[i]["target"], tempCommand[i]["value"]);
        }
    }
}

function selectForeRecord() {
    pressArrowKey(38);
}

function selectNextRecord() {
    pressArrowKey(40);
}

function pressArrowKey(direction) {
    let selectedRecords = getSelectedRecords();
    if (selectedRecords.length == 0) {
        return;
    }
    let lastRecordId = selectedRecords[selectedRecords.length - 1].id;
    let recordNum = parseInt(lastRecordId.substring(lastRecordId.indexOf("-") + 1));
    $("#records-grid .selectedRecord").removeClass("selectedRecord");
    if (direction == 38) { // press up arrow
        if (recordNum == 1) {
            $("#records-1").addClass("selectedRecord");
            $("#records-1").click();
        } else {
            $("#records-" + (recordNum - 1)).addClass("selectedRecord");
            $("#records-" + (recordNum - 1)).click();
        }
    } else if (direction == 40) { // press down arrow
        if (recordNum == getRecordsNum()) {
            $("#records-" + recordNum).addClass("selectedRecord");
            $("#records-" + recordNum).click();
        } else {
            $("#records-" + (recordNum + 1)).addClass("selectedRecord");
            $("#records-" + (recordNum + 1)).click();
        }
    }
}

function deleteCommand(selected_ID) {
    if (selected_ID) {
    
        modifyCaseSuite();
    
        var delete_node = document.getElementById(selected_ID);
        if (delete_node.previousSibling.nodeType == 3) {
            delete_node.parentNode.removeChild(delete_node.previousSibling);
        }
        delete_node.parentNode.removeChild(delete_node);

        var count = parseInt(getRecordsNum()) - 1;
        document.getElementById("records-count").value = count;
        selected_ID = parseInt(selected_ID.split("-")[1]);

        if (selected_ID - 1 != count) {
            reAssignIdForDelete(selected_ID, count);
        } else {
        }

        var s_case = getSelectedCase();
        if (s_case) {
            zeuz_testCase[s_case.id].records = document.getElementById("records-grid").innerHTML;
        }
    }
}
