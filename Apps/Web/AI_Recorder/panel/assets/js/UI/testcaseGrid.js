/* Start zeuz function */
var isClosingAll = true;
function getSelectedCase() {
    if (document.getElementById("testCase-grid").getElementsByClassName("selectedCase")) {
        return document.getElementById("testCase-grid").getElementsByClassName("selectedCase")[0];
    } else {
        return null;
    }
}

function setSelectedCase(id) {
    saveOldCase();
    var suite_id = document.getElementById(id).parentNode.id;
    setSelectedSuite(suite_id);
    $("#" + id).addClass('selectedCase');
    clean_panel();
    document.getElementById("records-grid").innerHTML = escapeHTML(zeuz_testCase[id].records);
    attachEvent(1, getRecordsNum());
}

function getSelectedSuite() {
    if (document.getElementById("testCase-grid").getElementsByClassName("selectedSuite")) {
        return document.getElementById("testCase-grid").getElementsByClassName("selectedSuite")[0];
    } else {
        return null;
    }
}

function cleanSelected() {
    $('#testCase-grid .selectedCase').removeClass('selectedCase');
    $('#testCase-grid .selectedSuite').removeClass('selectedSuite');
}

function setSelectedSuite(id) {
    saveOldCase();
    cleanSelected();
    $("#" + id).addClass('selectedSuite');
    clean_panel();
}

function getSuiteNum() {
    return document.getElementById("testCase-grid").getElementsByTagName("DIV").length;
}

function getCaseNumInSuite() {
    let selectedSuite = getSelectedSuite();
    if (selectedSuite != null) {
        return selectedSuite.getElementsByTagName("P").length;
    }
    return 0;
}

function saveOldCase() {
    var old_case = getSelectedCase();
    if (old_case) {
        zeuz_testCase[old_case.id].records = document.getElementById("records-grid").innerHTML;
    }
}

function appendContextMenu(node, isCase) {
    var ul = document.createElement("ul");
    var a;

    if (isCase) {
        var add_case = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Add New Test Case";
        add_case.appendChild(a);
        add_case.addEventListener("click", function(event) {
            event.stopPropagation();
            document.getElementById('add-testCase').click();
        }, false);
        ul.appendChild(add_case);

        var remove_case = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Remove Test Case";
        remove_case.appendChild(a);
        remove_case.addEventListener("click", function(event) {
            event.stopPropagation();
            document.getElementById('delete-testCase').click();
        }, false);
        ul.appendChild(remove_case);

        var rename_case = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Rename Test Case";
        rename_case.appendChild(a);
        rename_case.addEventListener("click", function(event) {
            event.stopPropagation();
            var s_case = getSelectedCase();
            var n_title = prompt("Please enter the Test Case's name", zeuz_testCase[s_case.id].title);
            if (n_title) {
                s_case.childNodes[0].textContent = n_title;
                zeuz_testCase[s_case.id].title = n_title;
            }
        }, false);
        ul.appendChild(rename_case);

        var play_case_from_here = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Play From Here";
        play_case_from_here.appendChild(a);
        play_case_from_here.addEventListener("click", function(event) {
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
            var cases = getSelectedSuite().getElementsByTagName("p");
            var i = 0;
            while (i < cases.length) {
                var s_case = getSelectedCase();
                if (cases[i].id === s_case.id) {
                    break;
                }
                i++;
            }
            playSuite(i);
        }, false);
        ul.appendChild(play_case_from_here);
    } else {
        var save_suite = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Save Test Suite As...";
        save_suite.appendChild(a);
        save_suite.addEventListener("click", function(event) {
            event.stopPropagation();
            document.getElementById('save-testSuite').click();
        }, false);
        ul.appendChild(save_suite);

        var close_suite = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Close Test Suite";
        close_suite.appendChild(a);
        close_suite.addEventListener("click", function(event) {
            event.stopPropagation();
            document.getElementById('close-testSuite').click();
        }, false);
        ul.appendChild(close_suite);

        var close_all_suite = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Close All Test Suites";
        close_all_suite.appendChild(a);
        close_all_suite.addEventListener("click", function(event) {
            event.stopPropagation();
            document.getElementById('close-all-testSuites').click();
        }, false);
        ul.appendChild(close_all_suite);

        var add_case = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Add New Test Case";
        add_case.appendChild(a);
        add_case.addEventListener("click", function(event) {
            event.stopPropagation();
            document.getElementById('add-testCase').click();
        }, false);
        ul.appendChild(add_case);

        var rename_suite = document.createElement("li");
        a = document.createElement("a");
        a.setAttribute("href", "#");
        a.textContent = "Rename Test Suite";
        rename_suite.appendChild(a);
        rename_suite.addEventListener("click", function(event) {
            event.stopPropagation();
            var s_suite = getSelectedSuite();
            var n_title = prompt("Please enter the Test Suite's name", zeuz_testSuite[s_suite.id].title);
            if (n_title) {
                s_suite.getElementsByTagName("STRONG")[0].textContent = n_title;
                zeuz_testSuite[s_suite.id].title = n_title;
                zeuz_testSuite[s_suite.id].file_name = n_title + ".html";
                $(s_suite).find("strong").addClass("modified");
                closeConfirm(true);
            }
        }, false);
        ul.appendChild(rename_suite);
    }

    node.appendChild(ul);
}

function addTestSuite(title, id) {
    var textDiv = document.createElement("div");
    textDiv.classList.add("test-suite-title");
    var saveIcon = document.createElement("i");
    saveIcon.classList.add("fa");
    saveIcon.classList.add("fa-download");
    saveIcon.setAttribute("aria-hidden", "true");
    saveIcon.addEventListener("click", clickSaveIcon);
    textDiv.appendChild(saveIcon);
    $(saveIcon).hide();
    var text = document.createElement("strong");
    text.classList.add("test-suite-title");
    text.innerHTML = escapeHTML(title);
    textDiv.appendChild(text);

    var plusIcon = document.createElement("i");
    plusIcon.classList.add("fa");
    plusIcon.classList.add("fa-plus");
    plusIcon.classList.add("case-plus");
    plusIcon.setAttribute("aria-hidden", "true");
    plusIcon.addEventListener("click", clickCasePlusIcon);
    textDiv.appendChild(plusIcon);
    $(plusIcon).hide();
    var div = document.createElement("div");
    div.setAttribute("id", id);
    div.setAttribute("contextmenu", "menu" + id);
    div.setAttribute("class", "message");
    div.addEventListener("mouseover", mouseOnAndOutTestSuite);
    div.addEventListener("mouseout", mouseOnAndOutTestSuite);
    div.appendChild(textDiv);

    var s_suite = getSelectedSuite();
    if (s_suite) {
        s_suite.parentNode.insertBefore(div, s_suite.nextSibling);
    } else {
        document.getElementById("testCase-grid").appendChild(div);
    }

    cleanSelected();
    div.classList.add("selectedSuite");
    div.addEventListener("click", function(event) {
        if (this.getElementsByTagName("p").length != 0) {
            this.getElementsByTagName("p")[0].click();
        } else {
            event.stopPropagation();
            saveOldCase();
            cleanSelected();
            this.classList.add("selectedSuite");
            clean_panel();
        }
    }, false);

    var menu = document.createElement("div");
    menu.setAttribute("class", "menu");
    menu.setAttribute("id", "menu" + id);
    appendContextMenu(menu, false);
    div.appendChild(menu);

    div.addEventListener("contextmenu", function(event) {
        event.preventDefault();
        event.stopPropagation();
        saveOldCase();
        setSelectedSuite(this.id);
        var mid = "#" + "menu" + id;
        $(".menu").css("left", event.pageX);
        $(".menu").css("top", event.pageY);
        $(mid).show();
    }, false);

    makeCaseSortable(div);

    addContextMenuButton(id, textDiv, menu, false);

    enableButton("playSuites");
    enableButton("playSuite");
}

function modifyCaseSuite() {
    getSelectedCase().classList.add("modified");
    getSelectedSuite().getElementsByTagName("strong")[0].classList.add("modified");
}

function addTestCase(title, id) {
    if (!getSelectedSuite()) {
        var suite_id = "suite" + zeuz_testSuite.count;
        zeuz_testSuite.count++;
        zeuz_testSuite[suite_id] = {
            file_name: "Untitled Test Suite.html",
            title: "Untitled Test Suite"
        };
        addTestSuite("Untitled Test Suite", suite_id);
    }

    var p = document.createElement("p");
    var text = document.createElement("span");
    text.innerHTML = escapeHTML(title);
    p.appendChild(text);
    p.setAttribute("id", id);
    p.setAttribute("contextmenu", "menu" + id);

    var s_case = getSelectedCase();
    if (s_case) {
        s_case.parentNode.insertBefore(p, s_case.nextSibling);
    } else {
        getSelectedSuite().appendChild(p);
    }

    cleanSelected();
    p.classList.add("selectedCase");
    p.classList.add("test-case-title");
    p.parentNode.classList.add("selectedSuite");

    if (zeuz_testCase[id]) {
        clean_panel();
        document.getElementById("records-grid").innerHTML = escapeHTML(zeuz_testCase[id].records);
        if (getRecordsNum() !== '0') {
            reAssignId("records-1", "records-" + getRecordsNum());
            attachEvent(1, getRecordsNum());
        }
    } else {
        clean_panel();
        document.getElementById("records-grid").innerHTML = escapeHTML('<input id="records-count" type=hidden value=0></input>');
        zeuz_testCase[id] = {
            records: "",
            title: title
        };
        p.classList.add("modified");
        p.parentNode.getElementsByTagName("strong")[0].classList.add("modified");
    }

    p.addEventListener("click", function(event) {
        event.stopPropagation();
        saveOldCase();
        //saveData();
        cleanSelected();
        this.classList.add("selectedCase");
        this.parentNode.classList.add("selectedSuite");
        if (zeuz_testCase[this.id].records) {
            clean_panel();
            document.getElementById("records-grid").innerHTML = escapeHTML(zeuz_testCase[this.id].records);
            if (getRecordsNum() !== '0') {
                reAssignId("records-1", "records-" + getRecordsNum());
                attachEvent(1, getRecordsNum());
            }
        } else {
            clean_panel();
            document.getElementById("records-grid").innerHTML = escapeHTML('<input id="records-count" type=hidden value=0></input>');
        }
        event.stopPropagation();
    }, false);

    var menu = document.createElement("div");
    menu.setAttribute("class", "menu");
    menu.setAttribute("id", "menu" + id);
    appendContextMenu(menu, true);
    p.appendChild(menu);

    p.addEventListener("contextmenu", function(event) {
        event.preventDefault();
        event.stopPropagation();
        saveOldCase();
        setSelectedCase(this.id);
        var mid = "#" + "menu" + id;
        $(".menu").css("left", event.pageX);
        $(".menu").css("top", event.pageY);
        $(mid).show();
    }, false);


    addContextMenuButton(id, p, menu, true);
    closeConfirm(true);
    enableButton("playback");
}

document.getElementById("add-testSuite").addEventListener("click", function(event) {
    event.stopPropagation();
    var title = prompt("Please enter the Test Suite's name", "Untitled Test Suite");
    if (title) {
        var id = "suite" + zeuz_testSuite.count;
        zeuz_testSuite.count++;
        zeuz_testSuite[id] = {
            file_name: title + ".html",
            title: title
        };
        addTestSuite(title, id);
    }
}, false);

document.getElementById("add-testSuite-menu").addEventListener("click", function(event) {
    event.stopPropagation();
    document.getElementById('add-testSuite').click();
}, false);

var confirmCloseSuite = function(question) {
    var defer = $.Deferred();
    $('<div></div>')
        .html(question)
        .dialog({
            title: "Save?",
            resizable: false,
            height: "auto",
            width: 400,
            modal: true,
            buttons: {
                "Yes": function() {
                    defer.resolve("true");
                    $(this).dialog("close");
                },
                "No": function() {
                    defer.resolve("false");
                    $(this).dialog("close");
                },
                Cancel: function() {
                    $(this).dialog("close");
                }
            },
            close: function() {
                $(this).remove();
            }
        });
    return defer.promise();
};

var remove_testSuite = function() {
    var s_suite = getSelectedSuite();
    zeuz_testSuite[s_suite.id] = null;
    s_suite.parentNode.removeChild(s_suite);
    clean_panel();
    //saveData();

    if (getSuiteNum() == 0) {
        disableButton("playback");
        disableButton("playSuite");
        disableButton("playSuites");
    }
    
    if(isClosingAll) close_testSuite(0);
};

document.getElementById("close-testSuite").addEventListener('click', function(event) {
    event.stopPropagation();
    isClosingAll = false;
    var suites = document.getElementById("testCase-grid").getElementsByClassName("message");
    var s_suite = getSelectedSuite();
    var i = 0;
    while (i < suites.length) {
        if (suites[i].id === s_suite.id) {
            break;
        }
        i++;
    }
    close_testSuite(i);
}, false);

document.getElementById("close-all-testSuites").addEventListener('click', function(event) {
    event.stopPropagation();
    isClosingAll = true;
    close_testSuite(0);
}, false);


function close_testSuite(suite_index) {
    var suites = document.getElementById("testCase-grid").getElementsByClassName("message");
    if (suites[suite_index] && suites[suite_index].id.includes("suite")) {
        var c_suite = suites[suite_index];
        setSelectedSuite(c_suite.id);
        if ($(c_suite).find(".modified").length) {
            confirmCloseSuite("Would you like to save the " + zeuz_testSuite[c_suite.id].title + " test suite?").then(function(answer) {
                if (answer === "true"){
                    downloadSuite(c_suite, remove_testSuite);
            	} else {
                    remove_testSuite();
                }
            });
        } else {
            remove_testSuite();
        }
    }
};

document.getElementById("add-testCase").addEventListener("click", function(event) {
    var title = prompt("Please enter the Test Case's name", "Untitled Test Case");
    if (title) {
        var id = "case" + zeuz_testCase.count;
        zeuz_testCase.count++;
        addTestCase(title, id);
    }
}, false);

var remove_testCase = function() {
    var s_case = getSelectedCase();
    zeuz_testCase[s_case.id] = null;
    s_case.parentNode.removeChild(s_case);
    clean_panel();
};

document.getElementById("delete-testCase").addEventListener('click', function() {
    var s_case = getSelectedCase();
    if (s_case) {
        if ($(s_case).hasClass("modified")) {
            confirmCloseSuite("Would you like to save this test case?").then(function(answer) {
                if (answer === "true")
                    downloadSuite(getSelectedSuite(), remove_testCase);
                else
                    remove_testCase();
                if (getCaseNumInSuite() == 0) {
                    disableButton("playback");
                }
            });
        } else {
            remove_testCase();
            if (getCaseNumInSuite() == 0) {
                disableButton("playback");
            }
        }
    }
}, false);

function clickSaveIcon(event) {
    event.stopPropagation();
    event.target.parentNode.parentNode.click();
    document.getElementById('save-testSuite').click();
}

function clickCasePlusIcon(event) {
    event.stopPropagation();
    event.target.parentNode.parentNode.click();
    document.getElementById('add-testCase').click();
}

function clickSuitePlusIcon(event) {
    document.getElementById("add-testSuite").click();
}

function clickSuiteOpenIcon(event) {
    document.getElementById("load-testSuite-hidden").click();
}

document.getElementById("suite-plus").addEventListener("click", clickSuitePlusIcon);
document.getElementById("suite-open").addEventListener("click", clickSuiteOpenIcon);
