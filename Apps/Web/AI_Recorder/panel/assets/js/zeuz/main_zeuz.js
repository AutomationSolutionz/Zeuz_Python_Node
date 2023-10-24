var newFormatters = {};
var dataFiles;
var extensions;
this.log = console; 

function readSuiteFromString(test_suite) {
    var id = "suite" + zeuz_testSuite.count;
    zeuz_testSuite.count++;
    var suiteName = parseSuiteName(test_suite);
    addTestSuite(suiteName, id);
    zeuz_testSuite[id] = {
        file_name: suiteName + '.html',
        title: suiteName
    };

    test_case = test_suite.match(/<table[\s\S]*?<\/table>/gi);
    if (test_case) {
        for (var i = 0; i < test_case.length; ++i) {
            readCase(test_case[i]);
        }
    }
}

function parseSuiteName(test_suite) {
    var pattern = /<title>(.*)<\/title>/gi;
    var suiteName = pattern.exec(test_suite)[1];
    return suiteName;
}

$(function() {
    chrome.storage.local.get(null, function(result) {
        try {
            if (result.data) {
                if (!result.backup) {
                    var data = {
                        backup: result.data
                    };
                    browser.storage.local.set(data);
                }
                for (var i = 0; i < result.data.length; i++) {
                    readSuiteFromString(result.data[i]);
                }
            }
            if (result.language) {
                $("#select-script-language-id").val(result.language);
            }
        } catch (e) {
            console.log(e);
        }
    });
});

function getContentOfTestSuite(s_suite) {
    var cases = s_suite.getElementsByTagName("p"),
    output = "",
    old_case = getSelectedCase();
    for (var i = 0; i < cases.length; ++i) {
        setSelectedCase(cases[i].id);
        saveNewTarget();
        output = output +
            '<table cellpadding="1" cellspacing="1" border="1">\n<thead>\n<tr><td rowspan="1" colspan="3">' +
            zeuz_testCase[cases[i].id].title +
            '</td></tr>\n</thead>\n' +
            panelToFile(document.getElementById("records-grid").innerHTML) +
            '</table>\n';
    }
    output = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ' +
        'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:' +
        'lang="en" lang="en">\n<head>\n\t<meta content="text/html; charset=UTF-8" http-equiv="content-type" />\n\t<title>' +
        zeuz_testSuite[s_suite.id].title +
        '</title>\n</head>\n<body>\n' +
        output +
        '</body>\n</html>';

    if (old_case) {
        setSelectedCase(old_case.id);
    } else {
        setSelectedSuite(s_suite.id);
    }

    return output;
}

function storeAllTestSuites() {
    var suites = document.getElementById("testCase-grid").getElementsByClassName("message");
    var length = suites.length;
    var data = [];
    for (var i=0; i<length; i++) {
        if (suites[i].id.includes("suite")) {
            var suite = suites[i];
            var content = getContentOfTestSuite(suite);
            data.push(content);
        }
    }
    return data;
}

$(window).on('resize', function() {
    var data = {
        window: {
            width: window.outerWidth,
            height: window.outerHeight
        }
    };
    browser.storage.local.set(data);
});


function saveSetting() {
    try {
        var data = {
            language: $("#select-script-language-id").val()
        };
        browser.storage.local.set(data);
    } catch (e) {
        console.log(e);
    }
}

function saveData() {
    try {

        var s_suite = getSelectedSuite();
        var s_case = getSelectedCase();
        var data = {
            data: storeAllTestSuites()
        };
        console.log(">>> data", data);
        browser.storage.local.set(data);
        if (s_suite) {
            setSelectedSuite(s_suite.id);
        }
        if (s_case) {
            setSelectedCase(s_case.id);
        }

        /* Custom Function */
        CustomFunction.SaveCaseDataAsJson();
        /* Custom Function */

    } catch (e) {
        console.log(e);
    }
}

// save test suite before exiting
window.addEventListener('beforeunload', function(e) {
    //saveData();
});

function _loadSeleniumCommands() {
    var commands = [];

    var nonWaitActions = ['open', 'selectWindow', 'chooseCancelOnNextConfirmation', 'answerOnNextPrompt', 'close', 'setContext', 'setTimeout', 'selectFrame'];

    for (func in Selenium.prototype) {
        var r;
        if (func.match(/^do[A-Z]/)) {
            var action = func.substr(2,1).toLowerCase() + func.substr(3);
            commands.push(action);
            if (!action.match(/^waitFor/) && nonWaitActions.indexOf(action) < 0) {
                commands.push(action + "AndWait");
            }
        } else if (func.match(/^assert.+/)) {
            commands.push(func);
            commands.push("verify" + func.substr(6));
        } else if ((r = func.match(/^(get|is)(.+)$/))) {
            var base = r[2];
            commands.push("assert" + base);
            commands.push("verify" + base);
            commands.push("store" + base);
            commands.push("waitFor" + base);
            var r2;
            if ((r = func.match(/^is(.*)Present$/))) {
                base = r[1];
                commands.push("assert" + base + "NotPresent");
                commands.push("verify" + base + "NotPresent");
                commands.push("waitFor" + base + "NotPresent");
            } else {
                commands.push("assertNot" + base);
                commands.push("verifyNot" + base);
                commands.push("waitForNot" + base);
            }
        }
    }

    commands.push("pause");
    commands.push("store");
    commands.push("echo");
    commands.push("break");

    commands.push('if');
    commands.push('elseIf');
    commands.push('else');
    commands.push('endIf');
    commands.push('while');
    commands.push('endWhile');
    commands.push('loadVars');
    commands.push('endLoadVars');
    commands.push('storeCsv');

    commands.push('dragAndDropToObjectByJqueryUI');

    commands.push('gotoIf');
    commands.push('gotoLabel');
    commands.push('label');

    commands.sort();

    var uniqueCommands = [];
    var previousCommand = null;
    for (var i = 0; i < commands.length; i++) {
        var currentCommand = commands[i];
        if (previousCommand != currentCommand) {
            uniqueCommands.push(currentCommand);
        }
        previousCommand = currentCommand;
    }
    return uniqueCommands;
}


$(function() {
    $.ajax({
        url: 'assets/js/zeuz/selenium-ide/iedoc-core.xml',
        success: function (document) {
            Command.apiDocuments = new Array(document);
        },
        async: false,
        dataType: 'xml'
    });
});


function scrape(word){
    emptyNode(document.getElementById("refercontainer"));
    var command = new Command(word);
    var def = command.getDefinition();
    help_log.logHTML((def) ? def.getReferenceFor(command): '');
    $('#tab4.case_roll').scrollTop(0);
}

// modify and add handler for command grid toolbar buttons
$(function() {
    $('#grid-add-btn').on('click', function(event) {
        $('#grid-add').click();
    });

    $('#grid-delete-btn').on('click', function(event) {
        $('#grid-delete').click();
    });

    $('#grid-copy-btn').on('click', function(event) {
        $('#grid-copy').click();
    });

    $('#grid-paste-btn').on('click', function(event) {
        $('#grid-paste').click();
    });

    var selectElementButton = $('#selectElementButton');
    var showElementButton = $('#showElementButton');
    selectElementButton.text("");
    showElementButton.text("");
});


function addContextMenuButton(id, node, menu, isCase) {
    var buttonWrapper = document.createElement('div');
    buttonWrapper.innerHTML = '<button class="btn-more">More</button>';
    var button = buttonWrapper.firstChild;
    node.appendChild(button);
    button.addEventListener("click", function(event) {
        if (isCase) {
            setSelectedCase(id);
        } else {
            setSelectedSuite(id);
        }
        var mid = "#" + "menu" + id;
        $(".menu").css("left", event.pageX);
        $(".menu").css("top", event.pageY);
        $(mid).show();

    }, false);

}

function saveAsFileOfTestCase(fileName, content) {
    var link = makeTextFile(content);
    var downloading = browser.downloads.download({
        filename: fileName,
        url: link,
        saveAs: true,
        conflictAction: 'overwrite'
    });
    var result = function(id) {
        browser.downloads.onChanged.addListener(function downloadCompleted(downloadDelta) {
            if (downloadDelta.id == id && downloadDelta.state &&
                downloadDelta.state.current == "complete") {
                $( "#generateToScriptsDialog" ).dialog("close");
            } else if (downloadDelta.id == id && downloadDelta.error) {
                browser.downloads.onChanged.removeListener(downloadCompleted);
            }
        })
    };
    var onError = function(error) {
        console.log(error);
    };
    downloading.then(result, onError);
}

$(function() {
    $("#export").click(function() {
        browser.runtime.sendMessage({
            getExternalCapabilities: true
        }).then(function(externalCapabilities) {
            var selectInput = $('#select-script-language-id');
            var language = selectInput.val();
            selectInput.find('option.external-exporter').remove();
            Object.keys(externalCapabilities).forEach(function(capabilityGlobalId) {
                var capability = externalCapabilities[capabilityGlobalId];
                if (capability.type == 'export') {
                    var optionId = 'external-exporter-' + capabilityGlobalId;
                    var summary = capability.summary + ' (via plugin)';
                    var tooltip = 'Extension ID: ' + capability.extensionId;
                    selectInput.append($('<option></option>')
                        .attr('id', optionId)
                        .attr('value', optionId)
                        .attr('title', tooltip)
                        .data('extensionId', capability.extensionId)
                        .data('capabilityId', capability.capabilityId)
                        .addClass('external-exporter')
                        .text(summary));
                }
            });
            var option = selectInput.find('option[value=' + language + ']');
            if (option.length > 0) {
                selectInput.val(language);
            }
            handleGenerateToScript();
        });
    });

    $("#select-script-language-id").change(function() {
        handleGenerateToScript();
        saveSetting();
    });
})

function handleGenerateToScript() {
    var selectedTestCase = getSelectedCase();
    if (selectedTestCase) {
        loadScripts();
    } else {
        alert('Please select a testcase');
    }
}

function copyToClipboard() {
    $("#txt-script-id").show();
    $("#txt-script-id").select();
    document.execCommand("copy");
    $("#txt-script-id").hide();
}

function saveToFile() {
    var $textarea = $("#txt-script-id");
    var cm = $textarea.data('cm');
    var format = '.' + window.options.defaultExtension;
    var fileName = testClassName(getTestCaseName()) + format;
    var content = cm.getValue();
    saveAsFileOfTestCase(fileName, content);
}

$(function() {
    var dialog = $( "#generateToScriptsDialog" );
    dialog.dialog({
        autoOpen: false,
        modal: true,
        height: 600,
        width: '90%',
        buttons: {
            "Copy to Clipboard": copyToClipboard,
            "Save As File...": saveToFile,
            Close: function() {
                $(this).dialog("close");
            }
        }
    });
    dialog.dialog({
        close: function() {
        }
    });
});

function getCommandsToGenerateScripts() {
    var ret = [];
    let commands = getRecordsArray();
    for (var index=0; index<commands.length; index++) {
        let commandName = getCommandName(commands[index]);
        let commandTarget = getCommandTarget(commands[index]);
        let commandValue = getCommandValue(commands[index]);

        ret.push(new Command(commandName, commandTarget, commandValue));
    }
    return ret;
}

function loadScripts() {
    var language = $("#select-script-language-id").val();
    var scriptNames = [];
    var isExternalCapability = false;
    var newFormatter = null;
    switch (language) {
        case 'cs-wd-nunit':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/csharp/cs-rc.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/csharp/cs-wd.js"
            ];
            break;
        case 'cs-wd-mstest':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/csharp/cs-rc.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/csharp/cs-wd.js",
                "assets/js/zeuz/selenium-ide/format/csharp/cs-mstest-wd.js"
            ];
            break;
        case 'zeuz':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/java/java-rc.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-junit4.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-testng.js",
                "assets/js/zeuz/selenium-ide/format/java/java-backed-junit4.js",
                "assets/js/zeuz/selenium-ide/format/zeuz/zeuz.js"
            ];
            break;
        case 'java-wd-testng':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/java/java-rc.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-junit4.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-testng.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/java/webdriver-testng.js"
            ];
            break;
        case 'java-wd-junit':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/java/java-rc.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-junit4.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-testng.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/java/webdriver-junit4.js"
            ];
            break;
        case 'java-rc-junit':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/java/java-rc.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-junit4.js",
                "assets/js/zeuz/selenium-ide/format/java/java-rc-testng.js",
                "assets/js/zeuz/selenium-ide/format/java/java-backed-junit4.js"
            ];
            break;
        case 'python-appdynamics':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/python/python2-rc.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/python/python-appdynamics.js"
            ];
            break;
        case 'python2-wd-unittest':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/python/python2-rc.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/python/python2-wd.js"
            ];
            break;
        case 'robot':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/format/robot/robot.js'
            ];
            break;
        case 'ruby-wd-rspec':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/remoteControl.js',
                "assets/js/zeuz/selenium-ide/format/ruby/ruby-rc.js",
                "assets/js/zeuz/selenium-ide/format/ruby/ruby-rc-rspec.js",
                'assets/js/zeuz/selenium-ide/webdriver.js',
                "assets/js/zeuz/selenium-ide/format/ruby/ruby-wd-rspec.js"
            ];
            break;
        case 'xml':
            scriptNames = [
                'assets/js/zeuz/selenium-ide/formatCommandOnlyAdapter.js',
                'assets/js/zeuz/selenium-ide/format/xml/XML-formatter.js'
            ];
            break;
        default:
            if (language.indexOf('new-formatter') >= 0) {
                var newFormatterId = language.replace('new-formatter-', '');
                newFormatter = newFormatters[newFormatterId];
            } else {
                isExternalCapability = true;
            }
    }

    if (isExternalCapability) {
        generateScripts(isExternalCapability, language);
    } else if (newFormatter) {
        generateScripts(isExternalCapability, language, newFormatter);
    } else {
        $("[id^=formatter-script-language-id-]").remove();
        var j = 0;
        for (var i = 0; i < scriptNames.length; i++) {
            var script = document.createElement('script');
            script.id = "formatter-script-language-id-" + language + '-' + i;
            script.src = scriptNames[i];
            script.async = false; // This is required for synchronous execution
            script.onload = function() {
                j++;
            }
            document.head.appendChild(script);
        }
        var interval = setInterval(
            function() {
                if (j == scriptNames.length) {
                    clearInterval(interval);
                    generateScripts(isExternalCapability, language);
                }
            },
            100
        );
    }
}

function displayOnCodeMirror(language, outputScript) {
    var $textarea = $("#txt-script-id");
    $textarea.val(outputScript);
    var textarea = $textarea.get(0);

    var language = $("#select-script-language-id").val();
    var mode = window.options && window.options.mimetype;
    if (!mode) {
        switch (language) {
            case 'cs-wd-nunit':
            case 'cs-wd-mstest':
                mode = 'text/x-csharp';
                break;
            case 'zeuz':
                mode = 'text/x-groovy';
                break;
            case 'java-wd-testng':
            case 'java-wd-junit':
            case 'java-rc-junit':
                mode = 'text/x-java';
                break;
            case 'python-appdynamics':
            case 'python2-wd-unittest':
                mode = 'text/x-python';
                break;
            case 'robot':
                break;
            case 'ruby-wd-rspec':
                mode = 'text/x-ruby';
                break;
            case 'xml':
                mode = 'application/xml';
                break;
            default:
                mode = 'text/plain';
        }
    }
    var codeMirrorOptions = {
        lineNumbers: true,
        matchBrackets: true,
        readOnly: true,
        lineWrapping: true
    };
    if (mode) {
        codeMirrorOptions.mode = mode;
    }
    var cm = CodeMirror.fromTextArea(textarea, codeMirrorOptions);

    $('.kat').show();
    $('.CodeMirror').removeClass('kat-90').addClass('kat-75');

    $textarea.data('cm', cm);
}

function getTestCaseName() {
    var selectedTestCase = getSelectedCase();
    return zeuz_testCase[selectedTestCase.id].title;
}

function generateScripts(isExternalCapability, language, newFormatter) {

    let commands = getCommandsToGenerateScripts();
    var name = getTestCaseName();

    var $textarea = $("#txt-script-id");
    var cm = $textarea.data('cm');
    if (cm) {
        cm.toTextArea();
    }
    $textarea.data('cm', null);
    $("#generateToScriptsDialog").dialog("open");

    if (isExternalCapability) {
        var option = $('#' + language);
        var extensionId = option.data('extensionId');
        var capabilityId = option.data('capabilityId');
        window.options = {
            defaultExtension: 'txt',
            mimetype: 'text/plain'
        };
        browser.runtime.sendMessage(
            extensionId,
            {
                type: 'zeuz_recorder_export',
                payload: {
                    capabilityId: capabilityId,
                    name: name,
                    commands: commands
                }
            }
        ).then(function(response) {
            var payload = response.payload;
            if (response.status) {
                options = {
                    defaultExtension: payload.extension,
                    mimetype: payload.mimetype
                };
                displayOnCodeMirror(language, payload.content);
            } else {
                throw(payload);
            }
        }).catch(function(err) {
            var content = 'Could not export.';
            if (err) {
                content += ' Error: ' + JSON.stringify(err) + '.';
            }
            displayOnCodeMirror(language, content);
        });
    } else if (newFormatter) {
        var payload = newFormatter(name, commands);
        options = {
            defaultExtension: payload.extension,
            mimetype: payload.mimetype
        };
        displayOnCodeMirror(language, payload.content);
    } else {

        var testCase = new TestCase(name);
        testCase.commands = commands;
        testCase.formatLocal(name).header = "";
        testCase.formatLocal(name).footer = "";

        displayOnCodeMirror(language, format(testCase, name));

        $("[id^=formatter-script-language-id-]").remove();
        var script = document.createElement('script');
        script.id = "formatter-script-language-id-" + language;
        script.src = 'js/background/formatCommand.js';
        script.async = false; // This is required for synchronous execution
        document.head.appendChild(script);
    }
}

$(function() {
    $('#show-hide-bottom-panel').click(function (e) {
        e.stopPropagation();
        var $bottomContent = $('#tab4');
        $bottomContent.toggle();
        var $icon = $("#show-hide-bottom-panel img");
        if ($bottomContent.is(":hidden")) {
            $('.width_quarter').css("height", "calc(100% - 62px)");
            $('.width_3_quarter').css("height", "calc(100% - 62px)");
            $('.width_full').css("height", "38px");
            $icon.attr("src", $icon.data("show"));
        } else {
            $('.width_quarter').css("height", "calc(70% - 24px)");
            $('.width_3_quarter').css("height", "calc(70% - 24px)");
            $('.width_full').css("height", "30%");
            $icon.attr("src", $icon.data("hide"));
        }
    });
});

$(function() {
    var logLi = $('#history-log');
    var referenceLi = $('#reference-log');
    var variableLi = $('#variable-log');
    var screenshotLi = $('#screenshot');
    var dataLi = $('#data-files');
    var extensionsLi = $('#extensions');
    var lis = [logLi, referenceLi, variableLi, screenshotLi, dataLi, extensionsLi];

    var logContainer = $('#logcontainer');
    var referenceContainer = $('#refercontainer');
    var variableContainer = $('#variablecontainer');
    var screenshotContainer = $('#screenshotcontainer');
    var dataContainer = $('#datacontainer');
    var extensionsContainer = $('#extensionscontainer');
    var containers = [logContainer, referenceContainer, variableContainer, screenshotContainer, dataContainer, extensionsContainer];

    var clearLog = $('#clear-log');
    var saveLog = $('#save-log');
    var upload = $('#ka-upload');
    
    var csvAdd = $('#data-files-add-csv');
    var jsonAdd = $('#data-files-add-json');
    var extensionAdd = $('#extension-add');

    setActiveTab(logLi, logContainer);

    logLi.on("click", function() {
        setActiveTab(logLi, logContainer);
    });
    referenceLi.on("click", function() {
        setActiveTab(referenceLi, referenceContainer);
    });
    variableLi.on("click", function() {
        setActiveTab(variableLi, variableContainer);
    });
    screenshotLi.on("click", function() {
        setActiveTab(screenshotLi, screenshotContainer);
    });
    dataLi.on('click', function() {
        setActiveTab(dataLi, dataContainer);
    });
    extensionsLi.on('click', function() {
        setActiveTab(extensionsLi, extensionsContainer);
    });

    function setActiveTab(li, container) {
        for (var i = 0; i < lis.length; i++) {
            lis[i].removeClass("active");
        }
        li.addClass("active");

        for (var i = 0; i < containers.length; i++) {
            containers[i].hide();
        }
        container.show();

        if (li == logLi) {
            upload.show();
            saveLog.show();
            clearLog.show();
            csvAdd.hide();
            jsonAdd.hide();
            extensionAdd.hide();
        } else if (li == screenshotLi) {
            upload.hide();
            saveLog.hide();
            clearLog.hide();
            csvAdd.hide();
            jsonAdd.hide();
            extensionAdd.hide();
        } else if (li == dataLi) { 
            upload.hide();
            saveLog.hide();
            clearLog.hide();
            csvAdd.show();
            jsonAdd.show();
            extensionAdd.hide();
        } else if (li == extensionsLi) { 
            upload.hide();
            saveLog.hide();
            clearLog.hide();
            csvAdd.hide();
            jsonAdd.hide();
            extensionAdd.show();
        } else {
            upload.hide();
            saveLog.hide();
            clearLog.hide();
            csvAdd.hide();
            jsonAdd.hide();
            extensionAdd.hide();
        }
    }
});

$(function() {
    /*$('#settings').on('click', function() {
        browser.windows.update(
            contentWindowId,
            { focused: true }
        );
        chrome.tabs.create({
            url: chrome.extension.getURL('zeuz/options.html'),
            windowId: contentWindowId
        }, function(tab){});
    });*/
});

$(function() {
    /*$('#record').attr('title', "Click and navigate to the desired browser tab and record your tests. NOTE: If the tab has been opened before ZeuZ Recorder was installed, please refresh it.");
    $('#playback').attr('title', "Run selected test case on the active tab, any interference may stop the process. NOTE: If the tab has been opened before ZeuZ Recorder was installed, please refresh it.");
    $('#playSuite').attr('title', "Run selected test suite on the active tab, any interference may stop the process. NOTE: If the tab has been opened before ZeuZ Recorder was installed, please refresh it.");
    $('#playSuites').attr('title', "Run all test suites on the active tab, any interference may stop the process. NOTE: If the tab has been opened before ZeuZ Recorder was installed, please refresh it.");
    $('#settings').attr('title', "Settings");
    $('.sub_btn#help').attr('title', "Help");
    $('#grid-add-btn').attr('title', "Add new test step");
    $('#grid-delete-btn').attr('title', "Delete the current test steps");
    $('#grid-copy-btn').attr('title', "Copy the current test steps");
    $('#grid-paste-btn').attr('title', "Paste the copied test steps as the next step of the current one");
    $('#selectElementButton').attr('title', "Select a target element for the current command");
    $('#showElementButton').attr('title', "Find and highlight the curent target element of the current command");
    $('#speed').attr('title', "Adjust play speed");
    $('#new').attr('title', "Create new test case");
    $('#export').attr('title', "Export the current test case to script in C#, Java, Ruby, Python, (ZeuZ Studio) Groovy, or Robot Framework");
    $('#suite-open').attr('title', "Open test suite");
    $('#suite-plus').attr('title', "Create new test suite");*/
})

$(function() {
    var slider = $('#slider');
    var sliderContainer = $('#slider-container');
    var speedButton = $('#speed');

    slider.slider({
        min: 0,
        max: 3000,
        value: 0,
        step: 600,
        orientation: 'vertical'
    }).slider("pips", {
        rest: "label", labels: ["Fast", "", "", "", "", "Slow"]
    });
    sliderContainer.append(slider);
    slider.show();

    speedButton.on("click", function() {
        sliderContainer.toggle();
    });
})

function handleDisplayVariables() {
    var varGridBody = $('#variable-grid tbody');
    varGridBody.empty();
    for (var variable in declaredVars) {
        var value = declaredVars[variable];
        var cellName = $('<td></td>');
        cellName.text(variable);
        var cellType = $('<td></td>');
        cellType.text(typeof value);
        var cellValue = $('<td></td>');
        cellValue.text(value);
        cellValue.attr('title', value);
        var row = $('<tr></tr>');
        row.append(cellName);
        row.append(cellType);
        row.append(cellValue);
        varGridBody.append(row);
    }
}

$(function() {
    $('#new').on('click', function() {
        saveOldCase();
        $('#add-testCase').click();
    });
});

$(function() {
    var imagesLookup = {
        '#record': 'record-icon-16.svg',
        '#new': 'new-icon-16.svg',
        '#playback': 'play-icon-16.svg',
        '#stop': 'stop-icon-16.svg',
        '#playSuite': 'play-suite-icon-16.svg',
        '#playSuites': 'play-all-icon-16.svg',
        '#pause': 'pause-icon-16.svg',
        '#resume': 'resume-icon-16.svg',
        '#export': 'export-icon-16.svg',
        '#speed': 'speed-icon-16.svg',
        '#settings': 'setting-icon-16.svg',
        '.sub_btn#help': 'help-icon-16.svg',
        '#github-repo': 'github-icon.png'
    }
});

$(function() {
    var manifestData = chrome.runtime.getManifest();
    $(document).attr('title', 'ZeuZ ' + manifestData.version)
});


$(function() {
    var saveLog = $('#save-log a');
    var clearLog = $('#clear-log a');

    saveLog.empty();
    clearLog.empty();
})


function switchRecordButton(stop) {
    var record = $('#record');
    if (stop) {
        record.removeClass("record--stop");
    } else {
        record.addClass("record--stop");
    }
}

$(function() {
    $('#command-toolbar .fieldset').on("dblclick", function(event) {
        event.stopPropagation();
    });
})

var waitDialog;

function showDialog(html, showOK) {
    if (waitDialog) {
        waitDialog.dialog('close');
        waitDialog = null;
    }
    var buttons;
    if (showOK) {
        buttons = {
            Close: function() {
                $(this).dialog("close");
            }
        };
    } else {
        buttons = {};
    }
    return $('<div></div>')
        .html(html)
        .dialog({
            title: 'ZeuZ',
            resizable: false,
            height: "auto",
            width: 400,
            modal: true,
            buttons: buttons,
            close: function() {
                $(this).remove();
            }
        });
}

function showErrorDialog() {
    return showDialog('Something went wrong. Please try again later.', true);
}

$(function() {

    var kaEndpoint = 'https://www.zeuz.ai';

    var dialog = $( '#ka-select-project-dialog');
    dialog.dialog({
        autoOpen: false,
        resizable: false,
        height: 'auto',
        modal: true,
        buttons: {
            Upload: function() {
                $(this).dialog('close');

                waitDialog = showDialog('Uploading...', false);
                var select = $('#select-ka-project');
                var projectId = select.val();
                $.ajax({
                    url: `${kaEndpoint}/api/v1/files/upload-url`,
                    type: 'GET',
                    data: {
                        projectId: projectId
                    },
                    success: function(response) {
                        var path = response.path;
                        var uploadUrl = response.uploadUrl;

                        // see save-log button
                        var logcontext = '';
                        var logcontainer = document.getElementById('logcontainer');
                        for (var i = 0; i < logcontainer.childNodes.length; i++) {
                            logcontext = logcontext + logcontainer.childNodes[i].textContent + '\n' ;
                        }

                        $.ajax({
                            url: uploadUrl,
                            type: 'PUT',
                            contentType: 'text/plain',
                            data: logcontext,
                            success: function() {
                                $.ajax({
                                    url: `${kaEndpoint}/api/v1/zeuz-recorder/test-reports`,
                                    type: 'POST',
                                    data: {
                                        projectId: projectId,
                                        batch: new Date().getTime(),
                                        isEnd: true,
                                        fileName: 'KR-' + new Date().getTime() + '.log',
                                        uploadedPath: path
                                    },
                                    success: function() {
                                        showDialog('Execution logs have been uploaded successfully.', true)
                                    },
                                    error: function() {
                                        console.log(arguments);
                                        showErrorDialog();
                                    }
                                });
                            },
                            error: function() {
                                console.log(arguments);
                                showErrorDialog();
                            }
                        });
                    },
                    error: function() {
                        console.log(arguments);
                        showErrorDialog();
                    }
                })
            },
            Cancel: function() {
                $(this).dialog('close');
            }
        }
    });

    $('#ka-upload').on('click', function() {
        $.ajax({
            url: `${kaEndpoint}/api/v1/projects`,
            type: 'GET',
            data: {
                sort: 'name'
            },
            success: function(data) {
                var projects = data.content;
                var select = $('#select-ka-project');
                select.empty();
                projects.forEach(function(project) {
                    select.append($('<option/>').attr('value', project.id).text(project.name));
                });
                dialog.dialog('open');
            },
            error: function(response) {
                console.log(response);
            }
        });
    });
});

function logTime() {
    var now = new Date();
    zeuz_log.info("Time: " + now + " Timestamp: " + now.getTime());
}

function logStartTime() {
    logTime();
    zeuz_log.info('OS: ' + (bowser.osname || '') + ' Version: ' + (bowser.osversion || ''));
    zeuz_log.info('Browser: ' + (bowser.name || '') + ' Version: ' + (bowser.version || ''));
    zeuz_log.info('If the test cannot start, please refresh the active browser tab');
}

function logEndTime() {
    logTime();
}

function clearScreenshotContainer() {
    $('#screenshotcontainer ul').empty();
}

function addToScreenshot(imgSrc, title) {
    if (!title) {
        title = new Date().toString();
    }
    var screenshotUl = $('#screenshotcontainer ul');
    var li = $('<li></li>');
    var a = $('<a></a>').attr('target', '_blank').attr('href', imgSrc).attr('title', title).attr('download', title).addClass('downloadable-screenshot');
    var img = $('<img>').attr('src', imgSrc).addClass('thumbnail');
    var screenshotTitle = $('<p></p>').text(title).hide();
    li.append(a.append(img)).append(screenshotTitle);
    screenshotUl.append(li);
    zeuz_log.logScreenshot(imgSrc, title);
}


function addSampleDataToScreenshot() {
}

$(function() {
    $('#help.sub_btn').on('click', function() {
        $( "#helpDialog" ).dialog({
            autoOpen: false,
            modal: true,
            height: "auto",
            width: "584px",
            dialogClass: "help-dialog",
            draggable: false,
            resize: function(event, ui) {
                var size = ui.size;
                var helpDialog = $('#helpDialog');
                if (size.width <= 350) {
                    helpDialog.addClass('small');
                } else {
                    helpDialog.removeClass('small');
                }
            },
            open: function(event, ui) {
                $('.ui-widget-overlay').addClass("dim-overlay");
            },
            close: function(event, ui) {
                $('#helpDialog').removeClass('small');
                $('.ui-widget-overlay').removeClass("dim-overlay");
            }
        })
        .parent()
        .draggable();

        $('#helpDialog').dialog("open");

        $('#helpDialog-close').on("click", function() {
            $('#helpDialog').dialog("close");
        });
    });
});


// The following code is untested!! just replaced Eval()

// function evalIfCondition(expression) {
//     return eval(expandForStoreEval(expression));
// }

function isVarName(str) {

    if (str.trim() !== str) {
        return false;
    }

    try {
        new Function(str, 'var ' + str);
    } catch (e) {
        return false;
    }

    return true;
}

function expandForStoreEval(expression) {
    var variables = '';
    for (var i in declaredVars) {
        if (isVarName(i)) {
            variables += 'var ' + i + '=' + JSON.stringify(declaredVars[i]) + ';';
        }
    }
    var mergedVars = Object.assign({}, storedVars, declaredVars);
    variables += 'var storedVars = ' + JSON.stringify(mergedVars) + ';';
    return variables + expression;
}

$(function() {

    chrome.storage.local.get('dataFiles', function(result) {
        dataFiles = result.dataFiles;
        if (!dataFiles) {
            dataFiles = {};
        }
        resetDataList();
    });

    var csvInput = $('#load-csv-hidden');
    $('#data-files-add-csv').click(function() {
        csvInput.click();
    });
    var jsonInput = $('#load-json-hidden');
    $('#data-files-add-json').click(function() {
        jsonInput.click();
    });
    document.getElementById("load-csv-hidden").addEventListener("change", function(event) {
        event.stopPropagation();
        for (var i = 0; i < this.files.length; i++) {
            readCsv(this.files[i]);
        }
        this.value = null;
    }, false);
    document.getElementById("load-json-hidden").addEventListener("change", function(event) {
        event.stopPropagation();
        for (var i = 0; i < this.files.length; i++) {
            readJson(this.files[i]);
        }
        this.value = null;
    }, false);
});

function readCsv(f) {
    var reader = new FileReader();
    reader.readAsText(f);
    reader.onload = function(event) {
        dataFiles[f.name] = {
            content: reader.result,
            type: 'csv'
        };
        saveDataFiles();
    }
}

function readJson(f) {
    var reader = new FileReader();
    reader.readAsText(f);
    reader.onload = function(event) {
        dataFiles[f.name] = {
            content: reader.result,
            type: 'json'
        };
        saveDataFiles();
    }
}

function saveDataFiles() {
    browser.storage.local.set({
        dataFiles: dataFiles
    });
    resetDataList();
}

function resetDataList() {
    var list = $('#data-files-list');
    list.empty();
    var names = Object.keys(dataFiles).sort();
    for (var i = 0; i < names.length; i++) {
        var name = names[i];
        var tr = renderDataListItem(name);
        list.append(tr);
    }
}

function renderDataListItem(name) {
    var tr = $('<tr></tr>');
    var tdType = $('<td></td>').text( function() {
        var dataFile = dataFiles[name];
        if (!dataFile.data) {
            var type = dataFile.type;
            if (!type) {
                type = 'csv';
            }
            if (type === 'csv') {
                return "CSV";
            } else {
                return "JSON";
            }
        }
    });
    var tdName = $('<td></td>').text(name);
    var tdActions = $('<td></td>');
    var renameButton = $('<button class="rename-button"></button>');
    renameButton.on('click', function() {
        var newName = prompt('Please enter the new name for this data file.', name);
        if (newName.length > 0 && name !== newName) {
            dataFiles[newName] = dataFiles[name];
            delete dataFiles[name];
            saveDataFiles();
        }
    });
    var deleteButton = $('<button class="delete-button"></button>');
    deleteButton.on('click', function() {
        if (confirm('Do you want to remove this data file?')) {
            delete dataFiles[name];
            saveDataFiles();
        }
    });
    tdActions.append(renameButton, deleteButton);
    tr.append(tdType, tdName, tdActions);
    return tr;
}

browser.runtime.onMessage.addListener(handleFormatCommand);

function parseData(name) {
    var dataFile = dataFiles[name];
    if (!dataFile.data) {
        var type = dataFile.type;
        if (!type) {
            type = 'csv';
        }
        if (type === 'csv') {
            dataFile.data = Papa.parse(dataFile.content, { header: true }).data;
        } else {
            dataFile.data = JSON.parse(dataFile.content);
        }
    }
    return dataFile;
}

$(function() {

    chrome.storage.local.get('extensions', function(result) {
        extensions = result.extensions;
        if (!extensions) {
            extensions = {};
        }
        resetExtensionsList();
    });

    var extensionInput = $('#load-extension-hidden');
    $('#extension-add').click(function() {
        extensionInput.click();
    });
    document.getElementById("load-extension-hidden").addEventListener("change", function(event) {
        event.stopPropagation();
        for (var i = 0; i < this.files.length; i++) {
            readExtension(this.files[i]);
        }
        this.value = null;
    }, false);
});

function readExtension(f) {
    var reader = new FileReader();
    reader.readAsText(f);
    reader.onload = function(event) {
        extensions[f.name] = {
            content: reader.result,
            type: 'Extension'
        };
        saveExtensions();
    }
}

function saveExtensions() {
    browser.storage.local.set({
        extensions: extensions
    });
    resetExtensionsList();
}

function resetExtensionsList() {
    var list = $('#extensions-list');
    list.empty();
    var names = Object.keys(extensions).sort();
    for (var i = 0; i < names.length; i++) {
        var name = names[i];
        var tr = renderExtensionsListItem(name);
        list.append(tr);
    }
}

function renderExtensionsListItem(name) {
    var tr = $('<tr></tr>');
    var tdType = $('<td></td>').text('JavaScript');
    var tdName = $('<td></td>').text(name);
    var tdActions = $('<td></td>');
    var renameButton = $('<button class="rename-button"></button>');
    renameButton.on('click', function() {
        var newName = prompt('Please enter the new name for this extension script.', name);
        if (newName.length > 0 && name !== newName) {
            extensions[newName] = extensions[name];
            delete extensions[name];
            saveExtensions();
        }
    });
    var deleteButton = $('<button class="delete-button"></button>');
    deleteButton.on('click', function() {
        if (confirm('Do you want to remove this extension script?')) {
            delete extensions[name];
            saveExtensions();
        }
    });
    tdActions.append(renameButton, deleteButton);
    tr.append(tdType, tdName, tdActions);
    return tr;
}