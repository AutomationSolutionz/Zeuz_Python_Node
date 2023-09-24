/* Zeuz command function start */
var selenium = new Selenium(BrowserBot.createForWindow(window));
window.neighborXpathsGenerator = window.neighborXpathsGenerator || {};
var locatorBuilders = new LocatorBuilders(window);
var commandFactory;
var extensionsLoaded = false;

if (!extensionsLoaded) {
	extensionsLoaded = true;
	chrome.storage.local.get('extensions', function(result) {

		extensions = result.extensions;
		if (extensions) {
			var extensionScripts = Object.values(extensions);
			for (var i = 0; i < extensionScripts.length; i++) {
				var extensionScript = extensionScripts[i];
				var f = new Function(extensionScript.content);
				f();
			}
        }
        commandFactory = new CommandHandlerFactory();
        commandFactory.registerAll(selenium);
	});
}

function continue_testing_when_condition_is_true(waitForCondition, sendResponse, result) {
    try {
        if (waitForCondition == null) {
            document.body.removeAttribute("ZeuZPlayingFlag");
            if (result && result.failed) {
                sendResponse({result: 'did not match'});
            } else {
                sendResponse({result: "success"});
            }
        } else if (waitForCondition()) {
            document.body.removeAttribute("ZeuZPlayingFlag");
            if (result && result.failed) {
                sendResponse({result: 'Failure message: ' + result.failureMessage});
            } else {
                sendResponse({result: "success"});
            }
        } else {
            setTimeout(function() {
                continue_testing_when_condition_is_true(waitForCondition, sendResponse, result);
            }, 10);
        }
    } catch(e) {
        console.error(e);
        document.body.removeAttribute("ZeuZPlayingFlag");
        sendResponse({result: e.message});
    }
}

function doClick2(element) {
    //console.error("element:" + element);
}

/* call it browser runtime on message */
function doCommands(request, sender, sendResponse, type) {
    if (request.commands) {
        if (request.commands == "waitPreparation") {
            selenium["doWaitPreparation"]("", selenium.preprocessParameter(""));
            sendResponse({});
        } else if (request.commands == "prePageWait") {
            selenium["doPrePageWait"]("", selenium.preprocessParameter(""));
            sendResponse({ new_page: window.zeuz_new_page });
        } else if (request.commands == "pageWait") {
            selenium["doPageWait"]("", selenium.preprocessParameter(""));
            sendResponse({ page_done: window.zeuz_page_done });
        } else if (request.commands == "ajaxWait") {
            selenium["doAjaxWait"]("", selenium.preprocessParameter(""));
            sendResponse({ ajax_done: window.zeuz_ajax_done });
        } else if (request.commands == "domWait") {
            selenium["doDomWait"]("", selenium.preprocessParameter(""));
            sendResponse({ dom_time: window.zeuz_new_page });
        } else if (request.commands === 'captureEntirePageScreenshot' || request.commands === 'captureEntirePageScreenshotAndWait') {
            browser.runtime.sendMessage({
                captureEntirePageScreenshot: true
            }).then(function(captureResponse) {
                sendResponse({
                    result: 'success',
                    capturedScreenshot: captureResponse.image,
                    capturedScreenshotTitle: request.target
                });
            });
        } else {
            var upperCase = request.commands.charAt(0).toUpperCase() + request.commands.slice(1);
            if (selenium["do" + upperCase] != null) {
                try {
                    document.body.setAttribute("ZeuZPlayingFlag", true);
                    let returnValue = selenium["do"+upperCase](request.target,selenium.preprocessParameter(request.value));
                    if (returnValue instanceof Promise) {
                        returnValue.then(function(value) {
                            document.body.removeAttribute("ZeuZPlayingFlag");
                            if (value && value.capturedScreenshot) {
                                sendResponse(value);
                            } else {
                                sendResponse({result: "success"});
                            }
                        }).catch(function(reason) {
                            document.body.removeAttribute("ZeuZPlayingFlag");
                            sendResponse({result: reason});
                        });
                    } else {
                        document.body.removeAttribute("ZeuZPlayingFlag");
                        sendResponse({result: "success"});
                    }
                } catch(e) {
                    document.body.removeAttribute("ZeuZPlayingFlag");
                    sendResponse({result: e.message});
                }
            } else {
                try {
                    var command = request;
                    if (!command.command) {
                        command.command = command.commands;
                    }
                    var handler = commandFactory.getCommandHandler(command.command);
                    if (handler == null) {
                        sendResponse({ result: "Unknown command: " + request.commands });
                    }
                    command.target = selenium.preprocessParameter(command.target);
                    command.value = selenium.preprocessParameter(command.value);
                    var result = handler.execute(selenium, command);
                    var waitForCondition = result.terminationCondition;

                    continue_testing_when_condition_is_true(waitForCondition, sendResponse, result);
                } catch(e) {
                    console.error(e);
                    document.body.removeAttribute("ZeuZPlayingFlag");
                    sendResponse({result: e.message});
                }
            }
        }

        return true;
    }

    if (request.selectMode) {
        if (request.selecting) {
            targetSelecter = new TargetSelecter(function (element, win) {
                if (element && win) {
                    var target = locatorBuilders.buildAll(element);
                    locatorBuilders.detach();
                    if (target != null && target instanceof Array) {
                        if (target) {
                            browser.runtime.sendMessage({
                                selectTarget: true,
                                target: target
                            })
                        } else {
                        }
                    }

                }
                targetSelecter = null;
            }, function () {
                browser.runtime.sendMessage({
                    cancelSelectTarget: true
                })
            });

        } else {
            if (targetSelecter) {
                targetSelecter.cleanup();
                targetSelecter = null;
                return;
            }
        }
    }

    if (request.attachRecorder) {
        browser.runtime.sendMessage({
            attachHttpRecorder: true
        });
        recorder.attach();
        return;
    } else if (request.detachRecorder) {
        browser.runtime.sendMessage({
            detachHttpRecorder: true
        });
        recorder.detach();
        return;
    }
}
browser.runtime.onMessage.addListener(doCommands);
