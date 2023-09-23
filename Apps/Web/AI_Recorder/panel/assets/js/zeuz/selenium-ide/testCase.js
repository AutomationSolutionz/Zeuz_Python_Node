
/* Start zeuz test case */
function Command(command, target, value) {
    this.command = command != null ? command : '';
    if (target != null && target instanceof Array) {
        if (target[0]) {
            this.target = target[0][0];
            this.targetCandidates = target;
        } else {
            this.target = "LOCATOR_DETECTION_FAILED";
        }
    } else {
        this.target = target != null ? target : '';
    }
    this.value = value != null ? value : '';
}

/* Create Copy */
Command.prototype.createCopy = function() {
    var copy = new Command();
    for (prop in this) {
        copy[prop] = this[prop];
    }
    return copy;
};


Command.prototype.getRealTarget = function() {
    if (this.value) {
        return this.target;
    } else {
        return null;
    }
}

Command.prototype.getRealValue = function() {
    if (this.value) {
        return this.value;
    } else {
        return this.target;
    }
}

Command.innerHTML = function(element) {
    var html = "";
    var nodes = element.childNodes;
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes.item(i);
        switch (node.nodeType) {
        case 1:
            html += "<" + node.nodeName + ">";
            html += this.innerHTML(node);
            html += "</" + node.nodeName + ">";
            break;
        case 3:
            html += node.data;
            break;
        }
    }
    return html;
}

Command.loadAPI = function() {
  if (!this.functions) {
    var document;
    var documents = this.apiDocuments;
    var functions = {};
    for (var d = 0; d < documents.length; d++) {
      document = documents[d];
      var functionElements = document.documentElement.getElementsByTagName("function");
      for (var i = 0; i < functionElements.length; i++) {
        var element = functionElements.item(i);
        var def = new CommandDefinition(String(element.attributes.getNamedItem('name').value));
        
        var returns = element.getElementsByTagName("return");
        if (returns.length > 0) {
          var returnType = new String(returns.item(0).attributes.getNamedItem("type").value);
          returnType = returnType.replace(/string/, "String");
          returnType = returnType.replace(/number/, "Number");
          def.returnType = returnType;
          def.returnDescription = this.innerHTML(returns.item(0));
        }
        
        var comments = element.getElementsByTagName("comment");
        if (comments.length > 0) {
          def.comment = this.innerHTML(comments.item(0));
        } else {
            def.comment = '';
        }

        var alternatives = element.getElementsByTagName("alternatives");
        if (alternatives.length > 0) {
          def.alternatives = this.innerHTML(alternatives.item(0));
        }
        var deprecated = element.getElementsByTagName("deprecated");
        if (deprecated.length > 0) {
          def.deprecated = this.innerHTML(deprecated.item(0));
          if (def.deprecated.length == 0 && def.alternatives) {
            def.deprecated = "Use the ${alternatives} command instead.";
          }
        }

        var params = element.getElementsByTagName("param");
        for (var j = 0; j < params.length; j++) {
          var paramElement = params.item(j);
          var param = {};
          param.name = String(paramElement.attributes.getNamedItem('name').value);
          param.description = this.innerHTML(paramElement);
          def.params.push(param);
        }
        functions[def.name] = def;
        if (def.name.match(/^(is|get)/)) {
          def.isAccessor = true;
          functions["!" + def.name] = def.negativeAccessor();
        }
        if (def.name.match(/^assert/)) {
          var verifyDef = new CommandDefinition(def.name);
          verifyDef.params = def.params;
          functions["verify" + def.name.substring(6)] = verifyDef;
        }
      }
    }
    functions['assertFailureOnNext'] = new CommandDefinition('assertFailureOnNext');
    functions['verifyFailureOnNext'] = new CommandDefinition('verifyFailureOnNext');
    functions['assertErrorOnNext'] = new CommandDefinition('assertErrorOnNext');
    functions['verifyErrorOnNext'] = new CommandDefinition('verifyErrorOnNext');
    this.functions = functions;
  }
  return this.functions;
};

function CommandDefinition(name) {
    this.name = name;
    this.params = [];
}

CommandDefinition.prototype.getReferenceFor = function(command) {
    var paramNames = [];
    for (var i = 0; i < this.params.length; i++) {
        paramNames.push(this.params[i].name);
    }
    var originalParamNames = paramNames.join(", ");
    if (this.name.match(/^is|get/)) {
        if (command.command) {
            if (command.command.match(/^store/)) {
                paramNames.push("variableName");
            } else if (command.command.match(/^(assert|verify|waitFor)/)) {
                if (this.name.match(/^get/)) {
                    paramNames.push("pattern");
                }
            }
        }
    }
    var note = "";
    if (command.command && command.command != this.name) {
        note = "<dt>Generated from <strong>" + this.name + "(" +
            originalParamNames + ")</strong></dt>";
    }
    var params = "";
    if (this.params.length > 0) {
        params += "<div>Arguments:</div><ul>";
        for (var i = 0; i < this.params.length; i++) {
            params += "<li>" + this.params[i].name + " - " + this.params[i].description + "</li>";
        }
        params += "</ul>";
    }
    var returns = "";
    if (this.returnDescription) {
        returns += "<dl><dt>Returns:</dt><dd>" + this.returnDescription + "</dd></dl>";
    }
  var deprecated = "";
  if (this.deprecated) {
    deprecated += '<div class="deprecated">This command is deprecated. ' + this.deprecated + "</div>";
    if (this.alternatives) {
      deprecated = deprecated.replace("${alternatives}", "<strong>" + CommandDefinition.getAlternative(command.command, this.alternatives) + "</strong>");
    }
  }

    var sample = '';
  
    return "<dl><dt><strong>" + (command.command || this.name) + "(" +
      paramNames.join(", ") + ")</strong></dt>" +
      deprecated + note +
        '<dd>' + 
        params + returns +
        this.comment + sample + "</dd></dl>";
};

CommandDefinition.getAlternative = function(command, alternative) {
  if (command == null) return '';
  var alt = alternative;
  var r = /^(.*?)(AndWait)?$/.exec(command);
  var commandName = r[1];
  var prefix = '';
  var suffix = r[2] ? r[2] : '';
  var negate = false;
  r = /^(assert|verify|store|waitFor)(.*)$/.exec(commandName);
  if (r) {
    prefix = r[1];
    var commandName = r[2];
    if ((r = /^(.*)NotPresent$/.exec(commandName)) != null) {
      negate = true;
    } else if ((r = /^Not(.*)$/.exec(commandName)) != null) {
      negate = true;
    }
    if (negate) {
      if (alt.match(/Present$/)) {
        alt = alt.replace(/Present$/, 'NotPresent');
      } else {
        prefix += 'Not';
      }
    }
  }

  return prefix + (prefix.length > 0 ? alt.charAt(0).toUpperCase() : alt.charAt(0).toLowerCase()) + alt.substr(1) + suffix;
};

CommandDefinition.prototype.negativeAccessor = function() {
    var def = new CommandDefinition(this.name);
    for (var name in this) {
        def[name] = this[name];
    }
    def.isAccessor = true;
    def.negative = true;
    return def;
};

Command.prototype.getDefinition = function() {
    if (this.command == null) return null;
    var commandName = this.command.replace(/AndWait$/, '');
    var api = Command.loadAPI();
    var r = /^(assert|verify|store|waitFor)(.*)$/.exec(commandName);
    if (r) {
        var suffix = r[2];
        var prefix = "";
        if ((r = /^(.*)NotPresent$/.exec(suffix)) != null) {
            suffix = r[1] + "Present";
            prefix = "!";
        } else if ((r = /^Not(.*)$/.exec(suffix)) != null) {
            suffix = r[1];
            prefix = "!";
        }
        var booleanAccessor = api[prefix + "is" + suffix];
        if (booleanAccessor) {
            return booleanAccessor;
        }
        var accessor = api[prefix + "get" + suffix];
        if (accessor) {
            return accessor;
        }
    }
    return api[commandName];
}

Command.prototype.getAPI = function() {
    return window.editor.seleniumAPI;
}

Command.prototype.getParameterAt = function(index) {
    switch (index) {
    case 0:
        return this.target;
    case 1:
        return this.value;
    default:
        return null;
    }
}

Command.prototype.type = 'command';

Command.prototype.toString = function(){
    var s = this.command
    if (this.target) {
        s += ' | ' + this.target;
        if (this.value) {
            s += ' | ' + this.value;
        }
    }
    return s;
}

Command.prototype.isRollup = function(){
    return /^rollup(?:AndWait)?$/.test(this.command);
}

function Comment(comment) {
    this.comment = comment != null ? comment : '';
}

Comment.prototype.type = 'comment';

function Line(line) {
    this.line = line;
}

Line.prototype.type = 'line';

Comment.prototype.createCopy = function() {
    var copy = new Comment();
    for (prop in this) {
        copy[prop] = this[prop];
    }
    return copy;
};

function TestCase(tempTitle) {
    if (!tempTitle) tempTitle = "Untitled";
    this.log = new Log("TestCase");
    this.tempTitle = tempTitle;
    this.formatLocalMap = {};
    this.commands = [];
    this.recordModifiedInCommands();
    this.baseURL = "";

    var testCase = this;

    this.debugContext = {
        reset: function() {
            this.failed = false;
            this.started = false;
            this.debugIndex = -1;
      this.runTimeStamp = 0;
        },
        
        nextCommand: function() {
            if (!this.started) {
                this.started = true;
                this.debugIndex = testCase.startPoint ? testCase.commands.indexOf(testCase.startPoint) : 0
            } else {
                this.debugIndex++;
            }
            for (; this.debugIndex < testCase.commands.length; this.debugIndex++) {
                var command = testCase.commands[this.debugIndex];
                if (command.type == 'command') {
          this.runTimeStamp = Date.now();
                    return command;
                }
            }
            return null;
        },

        currentCommand: function() {
            var command = testCase.commands[this.debugIndex];
            if (!command) {
                testCase.log.warn("currentCommand() not found: commands.length=" + testCase.commands.length + ", debugIndex=" + this.debugIndex);
            }
            return command;
        }
    }
}

TestCase.prototype.createCopy = function() {
    var copy = new TestCase();
    for (prop in this) {
        copy[prop] = this[prop];
    }
    return copy;
};


TestCase.prototype.formatLocal = function(formatName) {
    var scope = this.formatLocalMap[formatName];
    if (!scope) {
        scope = {};
        this.formatLocalMap[formatName] = scope;
    }
    return scope;
}

TestCase.prototype.setCommands = function(commands) {
    this.commands = commands;
    this.recordModifiedInCommands();
}

TestCase.prototype.recordModifiedInCommands = function() {
    if (this.commands.recordModified) {
        return;
    }
    this.commands.recordModified = true;
    var self = this;
    var commands = this.commands;

    var _push = commands.push;
    commands.push = function(command) {
        _push.call(commands, command);
        self.setModified();
    }

    var _splice = commands.splice;
    commands.splice = function(index, removeCount, command) {

                var removed = null;
        if (command !== undefined && command != null) {
            removed = _splice.call(commands, index, removeCount, command);
        } else {
            removed = _splice.call(commands, index, removeCount);
        }
        self.setModified();

                return removed;
    }

    var _pop = commands.pop;
    commands.pop = function() {
        var command = commands[commands.length - 1];
        commands.splice(commands.length - 1, 1);
        self.setModified();
        return command;
    }
}

TestCase.prototype.clear = function() {
    var length = this.commands.length;
    this.commands.splice(0, this.commands.length);
    this.setModified();
};

TestCase.prototype.setModified = function() {
    this.modified = true;
    this.notify("modifiedStateUpdated");
}

TestCase.prototype.clearModified = function() {
    this.modified = false;
    this.notify("modifiedStateUpdated");
}

TestCase.prototype.checkTimestamp = function() {
    if (this.file) {
        if (this.lastModifiedTime < this.file.lastModifiedTime) {
            this.lastModifiedTime = this.file.lastModifiedTime;
            return true;
        }
    }
    return false;
}

TestCase.prototype.getCommandIndexByTextIndex = function(text, index, formatter) {
    this.log.debug("getCommandIndexByTextIndex: index=" + index);
    var lineno = text.substring(0, index).split(/\n/).length - 1;
    var header = this.formatLocal(formatter.name).header;
    this.log.debug("lineno=" + lineno + ", header=" + header);
    if (header) {
        lineno -= header.split(/\n/).length - 1;
    }
    this.log.debug("this.commands.length=" + this.commands.length);
    for (var i = 0; i < this.commands.length; i++) {
        this.log.debug("lineno=" + lineno + ", i=" + i);
        if (lineno <= 0) {
            return i;
        }
        var command = this.commands[i];
        if (command.line != null) {
            lineno -= command.line.split(/\n/).length;
        }
    }
    return this.commands.length;
}

TestCase.prototype.getTitle = function() {
    if (this.title) {
        return this.title;
    } else if (this.file && this.file.leafName) {
        return this.file.leafName.replace(/\.\w+$/,'');
    } else if (this.tempTitle) {
        return this.tempTitle;
    } else {
        return null;
    }
}

TestCase.prototype.setBaseURL = function(baseURL) {
    this.baseURL = baseURL;
}

TestCase.prototype.getBaseURL = function() {
    if (!this.baseURL || this.baseURL == "") {
        return 'https://www.google.com/';
    } else {
        return this.baseURL;
    }
}
