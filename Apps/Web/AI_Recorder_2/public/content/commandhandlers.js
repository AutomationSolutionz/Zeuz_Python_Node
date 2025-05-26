var CommandHandlerFactory = classCreate();
objectExtend(CommandHandlerFactory.prototype, {

    initialize: function() {
        this.handlers = {};
    },

    registerAccessor: function(name, accessBlock) {
        this.handlers[name] = new AccessorHandler(accessBlock);
    },

    registerAction: function(name, actionBlock, wait, dontCheckAlertsAndConfirms) {
        this.handlers[name] = new ActionHandler(actionBlock, wait, dontCheckAlertsAndConfirms);
    },

    registerAssert: function(name, assertBlock, haltOnFailure) {
        this.handlers[name] = new AssertHandler(assertBlock, haltOnFailure);
    },

    _register_all_accessors: function(seleniumApi) {
        for (var functionName in seleniumApi) {
            var match = /^(get|is)([A-Z].+)$/.exec(functionName);
            if (match) {
                var accessMethod = seleniumApi[functionName];
                var accessBlock = fnBind(accessMethod, seleniumApi);
                var baseName = match[2];
                var isBoolean = (match[1] == "is");
                var requiresTarget = (accessMethod.length == 1);

                this.registerAccessor(functionName, accessBlock);
                this._register_store_command_for_accessor(baseName, accessBlock, requiresTarget);

                var predicateBlock = this._predicate_for_accessor(accessBlock, requiresTarget, isBoolean);
                this._register_assertions_for_predicate(baseName, predicateBlock);
                this._register_wait_for_commands_for_predicate(seleniumApi, baseName, predicateBlock);
            }
        }
    },

    _register_all_actions: function(seleniumApi) {
        for (var functionName in seleniumApi) {
            var match = /^do([A-Z].+)$/.exec(functionName);
            if (match) {
                var actionName = match[1].lcfirst();
                var actionMethod = seleniumApi[functionName];
                var dontCheckPopups = actionMethod.dontCheckAlertsAndConfirms;
                var actionBlock = fnBind(actionMethod, seleniumApi);
                this.registerAction(actionName, actionBlock, false, dontCheckPopups);
                this.registerAction(actionName + "AndWait", actionBlock, false, dontCheckPopups);
            }
        }
    },

    getCommandHandler: function(name) {
        return this.handlers[name];
    },

    _register_all_asserts: function(seleniumApi) {
        for (var functionName in seleniumApi) {
            var match = /^assert([A-Z].+)$/.exec(functionName);
            if (match) {
                var assertBlock = fnBind(seleniumApi[functionName], seleniumApi);

                var assertName = functionName;
                this.registerAssert(assertName, assertBlock, true);

                var verifyName = "verify" + match[1];
                this.registerAssert(verifyName, assertBlock, false);
            }
        }
    },

    registerAll: function(seleniumApi) {
        this._register_all_accessors(seleniumApi);
        this._register_all_actions(seleniumApi);
        this._register_all_asserts(seleniumApi);
    },

    _predicate_for_accessor: function(accessBlock, requiresTarget, isBoolean) {
        if (isBoolean) {
            return this._predicate_for_boolean_accessor(accessBlock);
        }
        if (requiresTarget) {
            return this._predicate_for_single_arg_accessor(accessBlock);
        }
        return this._predicate_for_no_arg_accessor(accessBlock);
    },

    _predicate_for_no_arg_accessor: function(accessBlock) {
        return function(value) {
            var accessorResult = accessBlock();
            accessorResult = selArrayToString(accessorResult);
            if (PatternMatcher.matches(value, accessorResult)) {
                return new PredicateResult(true, "Actual value '" + accessorResult + "' did match '" + value + "'");
            } else {
                return new PredicateResult(false, "Actual value '" + accessorResult + "' did not match '" + value + "'");
            }
        };
    },


    _predicate_for_single_arg_accessor: function(accessBlock) {
        return function(target, value) {
            var accessorResult = accessBlock(target);
            accessorResult = selArrayToString(accessorResult);
            if (PatternMatcher.matches(value, accessorResult)) {
                return new PredicateResult(true, "Actual value '" + accessorResult + "' did match '" + value + "'");
            } else {
                return new PredicateResult(false, "Actual value '" + accessorResult + "' did not match '" + value + "'");
            }
        };
    },

    _predicate_for_boolean_accessor: function(accessBlock) {
        return function() {
            var accessorResult;
            if (arguments.length > 2) throw new SeleniumError("Too many arguments! " + arguments.length);
            if (arguments.length == 2) {
                accessorResult = accessBlock(arguments[0], arguments[1]);
            } else if (arguments.length == 1) {
                accessorResult = accessBlock(arguments[0]);
            } else {
                accessorResult = accessBlock();
            }
            if (accessorResult) {
                return new PredicateResult(true, "true");
            } else {
                return new PredicateResult(false, "false");
            }
        };
    },

    _invert_predicate: function(predicateBlock) {
        return function(target, value) {
            try {
                var result = predicateBlock(target, value);
            } catch (e) {
                var result = new PredicateResult(false, e);
            }
            result.isTrue = !result.isTrue;
            return result;
        };
    },

    _invert_predicate_name: function(baseName) {
        var matchResult = /^(.*)Present$/.exec(baseName);
        if (matchResult != null) {
            return matchResult[1] + "NotPresent";
        }
        return "Not" + baseName;
    },

    create_assertion_from_predicate: function(predicateBlock) {
        return function(target, value) {
            var result = predicateBlock(target, value);
            if (!result.isTrue) {
                Assert.fail(result.message);
            }
        };
    },

    _register_assertions_for_predicate: function(baseName, predicateBlock) {
        var assertBlock = this.create_assertion_from_predicate(predicateBlock);
        this.registerAssert("assert" + baseName, assertBlock, true);
        this.registerAssert("verify" + baseName, assertBlock, false);

        var invertedPredicateBlock = this._invert_predicate(predicateBlock);
        var negativeassertBlock = this.create_assertion_from_predicate(invertedPredicateBlock);
        this.registerAssert("assert" + this._invert_predicate_name(baseName), negativeassertBlock, true);
        this.registerAssert("verify" + this._invert_predicate_name(baseName), negativeassertBlock, false);
    },

    _wait_for_action_for_predicate: function(predicateBlock) {
        return function(target, value) {
            var terminationCondition = function () {
                try {
                    return predicateBlock(target, value).isTrue;
                } catch (e) {
                    return false;
                }
            };
            return Selenium.decorateFunctionWithTimeout(terminationCondition, this.defaultTimeout);
        };
    },

    _register_wait_for_commands_for_predicate: function(seleniumApi, baseName, predicateBlock) {
        var waitForActionMethod = this._wait_for_action_for_predicate(predicateBlock);
        var waitForActionBlock = fnBind(waitForActionMethod, seleniumApi);

        var invertedPredicateBlock = this._invert_predicate(predicateBlock);
        var waitForNotActionMethod = this._wait_for_action_for_predicate(invertedPredicateBlock);
        var waitForNotActionBlock = fnBind(waitForNotActionMethod, seleniumApi);

        this.registerAction("waitFor" + baseName, waitForActionBlock, false, true);
        this.registerAction("waitFor" + this._invert_predicate_name(baseName), waitForNotActionBlock, false, true);
        this.registerAction("waitForNot" + baseName, waitForNotActionBlock, false, true);
    },

    _register_store_command_for_accessor: function(baseName, accessBlock, requiresTarget) {
        var action;
        if (requiresTarget) {
            action = function(target, varName) {
                storedVars[varName] = accessBlock(target);
                browser.runtime.sendMessage({ "storeStr": storedVars[varName], "storeVar": varName });
            };
        } else {
            action = function(varName) {
                storedVars[varName] = accessBlock();
                browser.runtime.sendMessage({ "storeStr": storedVars[varName], "storeVar": varName });
            };
        }
        this.registerAction("store" + baseName, action, false, true);
    }

});

function PredicateResult(isTrue, message) {
    this.isTrue = isTrue;
    this.message = message;
}

function CommandHandler(type, haltOnFailure) {
    this.type = type;
    this.haltOnFailure = haltOnFailure;
}

function ActionHandler(actionBlock, wait, dontCheckAlerts) {
    this.actionBlock = actionBlock;
    CommandHandler.call(this, "action", true);
    if (wait) {
        this.wait = true;
    }
    this.checkAlerts = (dontCheckAlerts) ? false : true;
}

ActionHandler.prototype = new CommandHandler;
ActionHandler.prototype.execute = function(seleniumApi, command) {
    if (this.checkAlerts && (null == /(Alert|Confirmation)(Not)?Present/.exec(command.command))) {
        seleniumApi.ensureNoUnhandledPopups();
    }

    var handlerCondition = this.actionBlock(command.target, command.value);

    var terminationCondition = (this.wait)
        ? seleniumApi.makePageLoadCondition() : handlerCondition;

    return new ActionResult(terminationCondition);
};

function ActionResult(terminationCondition) {
    this.terminationCondition = terminationCondition;
}

function AccessorHandler(accessBlock) {
    this.accessBlock = accessBlock;
    CommandHandler.call(this, "accessor", true);
}
AccessorHandler.prototype = new CommandHandler;
AccessorHandler.prototype.execute = function(seleniumApi, command) {
    var returnValue = this.accessBlock(command.target, command.value);
    return new AccessorResult(returnValue);
};

function AccessorResult(result) {
  if (result.terminationCondition) {
    var self = this;
    this.terminationCondition = function() {
      return result.terminationCondition.call(self);
    };
  } else {
    this.result = result;
  }
}


function AssertHandler(assertBlock, haltOnFailure) {
    this.assertBlock = assertBlock;
    CommandHandler.call(this, "assert", haltOnFailure || false);
}
AssertHandler.prototype = new CommandHandler;
AssertHandler.prototype.execute = function(seleniumApi, command) {
    var result = new AssertResult();
    try {
        this.assertBlock(command.target, command.value);
    } catch (e) {
        if (!e.isAssertionFailedError) {
            throw e;
        }
        if (this.haltOnFailure) {
            var error = new SeleniumError(e.failureMessage);
            throw error;
        }
        result.setFailed(e.failureMessage);
    }
    return result;
};

function AssertResult() {
    this.passed = true;
}

AssertResult.prototype.setFailed = function(message) {
    this.passed = null;
    this.failed = true;
    this.failureMessage = message;
};

function SeleniumCommand(command, target, value, isBreakpoint) {
    this.command = command.trim();
    this.target = target;
    this.value = value;
    this.isBreakpoint = isBreakpoint;
}