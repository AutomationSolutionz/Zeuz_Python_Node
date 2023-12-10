function LocatorBuilders(window) {
    this.window = window;
}

LocatorBuilders.prototype.detach = function() {
    if (this.window._locator_pageBot) {
        this.window._locator_pageBot = undefined;
    }
};

LocatorBuilders.prototype.pageBot = function() {
    var pageBot = this.window._locator_pageBot;
    if (pageBot == null) {
        pageBot = new MozillaBrowserBot(this.window);
        var self = this;
        pageBot.getCurrentWindow = function() {
            return self.window;
        };
        this.window._locator_pageBot = pageBot;
    }
    return pageBot;
};

LocatorBuilders.prototype.buildWith = function(name, event, opt_contextNode) {
    return LocatorBuilders.builderMap[name].call(this, event, opt_contextNode);
};

LocatorBuilders.prototype.elementEquals = function(name, event, locator) {
    var fe = this.findElement(locator);
    return (event == fe) || (LocatorBuilders.builderMap[name] && LocatorBuilders.builderMap[name].match && LocatorBuilders.builderMap[name].match(event, fe));
};

LocatorBuilders.prototype.build = function(evnt) {
    var locators = this.buildAll(evnt);
    if (locators.length > 0) {
        return locators[0][0];
    } else {
        return "LOCATOR_DETECTION_FAILED";
    }
};

LocatorBuilders.prototype.buildAll = function(element) {
    var e = core.firefox.unwrap(element);
    var xpathLevel = 0;
    var maxLevel = 10;
    var buildWithResults;
    var locators = [];
    var coreLocatorStrategies = this.pageBot().locationStrategies;
    for (var i = 0; i < LocatorBuilders.order.length; i++) {
        var finderName = LocatorBuilders.order[i];
        var locator;
        var locatorResults = [];
        try {
            buildWithResults = this.buildWith(finderName, e);
            if (!Array.isArray) {
                Array.isArray = function (obj) {
                    return Object.prototype.toString.call(obj) === '[object Array]';
                }
            };
            if (Array.isArray(buildWithResults)) {
                for (var j = 0; j < buildWithResults.length; j++) {
                    locatorResults.push(buildWithResults[j]);
                }
            } else {
                locatorResults.push(buildWithResults);
            }

            for (var j = 0; j < locatorResults.length; j++) {
                locator = locatorResults[j];

                if (locator) {
                    locator = String(locator);
                    if (finderName != 'tac') {
                        var fe = this.findElement(locator);
                        if ((e == fe) || (coreLocatorStrategies[finderName] && coreLocatorStrategies[finderName].is_fuzzy_match && coreLocatorStrategies[finderName].is_fuzzy_match(fe, e))) {
                            locators.push([locator, finderName]);
                        }
                    } else {
                        locators.splice(0, 0, [locator, finderName]);
                    }
                }
            }
        } catch (e) {
        }
    }
    return locators;
};

LocatorBuilders.prototype.findElement = function(locator) {
    try {
        return this.pageBot().findElement(locator);
    } catch (error) {
        return null;
    }
};

LocatorBuilders.order = [];

LocatorBuilders.builderMap = {};
LocatorBuilders._preferredOrder = [];
LocatorBuilders.add = function(name, finder) {
    if (this.order.indexOf(name) < 0) {
        this.order.push(name);
    }
    this.builderMap[name] = finder;
    this._orderChanged();
};

LocatorBuilders.setPreferredOrder = function(preferredOrder) {
    if (typeof preferredOrder === 'string') {
        this._preferredOrder = preferredOrder.split(',');
    } else {
        this._preferredOrder = preferredOrder;
    }
    this._orderChanged();
};

LocatorBuilders.getPreferredOrder = function() {
    return this._preferredOrder;
};

LocatorBuilders._orderChanged = function() {
    var changed = this._ensureAllPresent(this.order, this._preferredOrder);
    this._sortByRefOrder(this.order, this._preferredOrder);
    if (changed) {
    }
};

LocatorBuilders._sortByRefOrder = function(arrayToSort, sortOrderReference) {
    var raLen = sortOrderReference.length;
    arrayToSort.sort(function(a, b) {
        var ai = sortOrderReference.indexOf(a);
        var bi = sortOrderReference.indexOf(b);
        return (ai > -1 ? ai : raLen) - (bi > -1 ? bi : raLen);
    });
};

LocatorBuilders._ensureAllPresent = function(sourceArray, destArray) {
    var changed = false;
    sourceArray.forEach(function(elm) {
        if (destArray.indexOf(elm) == -1) {
            destArray.push(elm);
            changed = true;
        }
    });
    return changed;
};


/* Start Prototopy function */

LocatorBuilders.prototype.preciseXPath = function(xpath, e) {
    if (this.findElement(xpath) != e) {
        var result = e.ownerDocument.evaluate(xpath, e.ownerDocument, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (var i = 0, len = result.snapshotLength; i < len; i++) {
            var newPath = 'xpath=(' + xpath + ')[' + (i + 1) + ']';
            if (this.findElement(newPath) == e) {
                return newPath;
            }
        }
    }
    return xpath;
};

LocatorBuilders.prototype.xpathHtmlElement = function(name) {
    if (this.window.document.contentType == 'application/xhtml+xml') {
        return "x:" + name;
    } else {
        return name;
    }
};

LocatorBuilders.prototype.relativeXPathFromParent = function(current) {
    var index = this.getNodeNbr(current);
    var currentPath = '/' + this.xpathHtmlElement(current.nodeName.toLowerCase());
    if (index > 0) {
        currentPath += '[' + (index + 1) + ']';
    }
    return currentPath;
};

LocatorBuilders.prototype.getCSSSubPath = function(e) {
    var css_attributes = ['id', 'name', 'class', 'type', 'alt', 'title', 'value'];
    for (var i = 0; i < css_attributes.length; i++) {
        var attr = css_attributes[i];
        var value = e.getAttribute(attr);
        if (value) {
            if (attr == 'id')
                return '#' + value;
            if (attr == 'class')
                return e.nodeName.toLowerCase() + '.' + value.replace(/\s+/g, ".").replace("..", ".");
            return e.nodeName.toLowerCase() + '[' + attr + '="' + value + '"]';
        }
    }
    if (this.getNodeNbr(e))
        return e.nodeName.toLowerCase() + ':nth-of-type(' + this.getNodeNbr(e) + ')';
    else
        return e.nodeName.toLowerCase();
};

LocatorBuilders.prototype.findDomFormLocator = function(form) {
    if (form.hasAttribute('name')) {
        var name = form.getAttribute('name');
        var locator = "document." + name;
        if (this.findElement(locator) == form) {
            return locator;
        }
        locator = "document.forms['" + name + "']";
        if (this.findElement(locator) == form) {
            return locator;
        }
    }
    var forms = this.window.document.forms;
    for (var i = 0; i < forms.length; i++) {
        if (form == forms[i]) {
            return "document.forms[" + i + "]";
        }
    }
    return null;
};

LocatorBuilders.prototype.attributeValue = function(value) {
    if (value.indexOf("'") < 0) {
        return "'" + value + "'";
    } else if (value.indexOf('"') < 0) {
        return '"' + value + '"';
    } else {
        var result = 'concat(';
        var part = "";
        while (true) {
            var apos = value.indexOf("'");
            var quot = value.indexOf('"');
            if (apos < 0) {
                result += "'" + value + "'";
                break;
            } else if (quot < 0) {
                result += '"' + value + '"';
                break;
            } else if (quot < apos) {
                part = value.substring(0, apos);
                result += "'" + part + "'";
                value = value.substring(part.length);
            } else {
                part = value.substring(0, quot);
                result += '"' + part + '"';
                value = value.substring(part.length);
            }
            result += ',';
        }
        result += ')';
        return result;
    }
};

LocatorBuilders.prototype.getNodeNbr = function(current) {
    var childNodes = current.parentNode.childNodes;
    var total = 0;
    var index = -1;
    for (var i = 0; i < childNodes.length; i++) {
        var child = childNodes[i];
        if (child.nodeName == current.nodeName) {
            if (child == current) {
                index = total;
            }
            total++;
        }
    }
    return index;
};

/* Starting add Function */

/* adding ui  */
LocatorBuilders.add('ui', function(pageElement) {
    return UIMap.getInstance().getUISpecifierString(pageElement,
        this.window.document);
});

/* Adding css */
LocatorBuilders.add('css', function (e) {
    var current = e;
    var sub_path = this.getCSSSubPath(e);
    while (this.findElement("css=" + sub_path) != e && current.nodeName.toLowerCase() != 'html') {
        sub_path = this.getCSSSubPath(current.parentNode) + ' > ' + sub_path;
        current = current.parentNode;
    }
    return "css=" + sub_path;
});

/* adding link  */
LocatorBuilders.add('link', function(e) {
    if (e.nodeName == 'A') {
        var text = e.textContent;
        if (!text.match(/^\s*$/)) {
            return "link=" + exactMatchPattern(text.replace(/\xA0/g, " ").replace(/^\s*(.*?)\s*$/, "$1"));
        }
    }
    return null;
});

/* adding name  */
LocatorBuilders.add('name', function(e) {
    if (e.name) {
        return 'name=' + e.name;
    }
    return null;
});

/* adding index  */
LocatorBuilders.add('dom:index', function(e) {
    if (e.form) {
        var formLocator = this.findDomFormLocator(e.form);
        if (formLocator) {
            var elements = e.form.elements;
            for (var i = 0; i < elements.length; i++) {
                if (elements[i] == e) {
                    return formLocator + ".elements[" + i + "]";
                }
            }
        }
    }
    return null;
});

/* adding dom name  */
LocatorBuilders.add('dom:name', function(e) {
    if (e.form && e.name) {
        var formLocator = this.findDomFormLocator(e.form);
        if (formLocator) {
            var candidates = [formLocator + "." + e.name,
            formLocator + ".elements['" + e.name + "']"
            ];
            for (var c = 0; c < candidates.length; c++) {
                var locator = candidates[c];
                var found = this.findElement(locator);
                if (found) {
                    if (found == e) {
                        return locator;
                    } else if (found instanceof NodeList) {
                        // multiple elements with same name
                        for (var i = 0; i < found.length; i++) {
                            if (found[i] == e) {
                                return locator + "[" + i + "]";
                            }
                        }
                    }
                }
            }
        }
    }
    return null;
});

/* adding xpath link */
LocatorBuilders.add('xpath:link', function(e) {
    if (e.nodeName == 'A') {
        var text = e.textContent;
        if (!text.match(/^\s*$/)) {
            return this.preciseXPath("//" + this.xpathHtmlElement("a") + "[contains(text(),'" + text.replace(/^\s+/, '').replace(/\s+$/, '') + "')]", e);
        }
    }
    return null;
});

/* adding xpath image */
LocatorBuilders.add('xpath:img', function(e) {
    if (e.nodeName == 'IMG') {
        if (e.alt != '') {
            return this.preciseXPath("//" + this.xpathHtmlElement("img") + "[@alt=" + this.attributeValue(e.alt) + "]", e);
        } else if (e.title != '') {
            return this.preciseXPath("//" + this.xpathHtmlElement("img") + "[@title=" + this.attributeValue(e.title) + "]", e);
        } else if (e.src != '') {
            return this.preciseXPath("//" + this.xpathHtmlElement("img") + "[contains(@src," + this.attributeValue(e.src) + ")]", e);
        }
    }
    return null;
});

/* adding attribute  */

LocatorBuilders.add('xpath:attributes', function(e) {
    const PREFERRED_ATTRIBUTES = ['id', 'name', 'value', 'type', 'action', 'onclick'];
    var i = 0;

    function attributesXPath(name, attNames, attributes) {
        var locator = "//" + this.xpathHtmlElement(name) + "[";
        for (i = 0; i < attNames.length; i++) {
            if (i > 0) {
                locator += " and ";
            }
            var attName = attNames[i];
            locator += '@' + attName + "=" + this.attributeValue(attributes[attName]);
        }
        locator += "]";
        return this.preciseXPath(locator, e);
    }

    if (e.attributes) {
        var atts = e.attributes;
        var attsMap = {};
        for (i = 0; i < atts.length; i++) {
            var att = atts[i];
            attsMap[att.name] = att.value;
        }
        var names = [];
        for (i = 0; i < PREFERRED_ATTRIBUTES.length; i++) {
            var name = PREFERRED_ATTRIBUTES[i];
            if (attsMap[name] != null) {
                names.push(name);
                var locator = attributesXPath.call(this, e.nodeName.toLowerCase(), names, attsMap);
                if (e == this.findElement(locator)) {
                    return locator;
                }
            }
        }
    }
    return null;
});


/* adding href  */
LocatorBuilders.add('xpath:href', function(e) {
    if (e.attributes && e.hasAttribute("href")) {
        href = e.getAttribute("href");
        if (href.search(/^http?:\/\//) >= 0) {
            return this.preciseXPath("//" + this.xpathHtmlElement("a") + "[@href=" + this.attributeValue(href) + "]", e);
        } else {
            return this.preciseXPath("//" + this.xpathHtmlElement("a") + "[contains(@href, " + this.attributeValue(href) + ")]", e);
        }
    }
    return null;
});

/* adding id  */
LocatorBuilders.add('id', function(e) {
    if (e.id) {
        return 'id=' + e.id;
    }
    return null;
});


/* adding position  */
LocatorBuilders.add('xpath:position', function(e, opt_contextNode) {
    var path = '';
    var current = e;
    while (current != null && current != opt_contextNode) {
        var currentPath;
        if (current.parentNode != null) {
            currentPath = this.relativeXPathFromParent(current);
        } else {
            currentPath = '/' + this.xpathHtmlElement(current.nodeName.toLowerCase());
        }
        path = currentPath + path;
        var locator = '/' + path;
        if (e == this.findElement(locator)) {
            return locator;
        }
        current = current.parentNode;
    }
    return null;
});

/* adding idRelative  */
LocatorBuilders.add('xpath:idRelative', function(e) {
    var path = '';
    var current = e;
    while (current != null) {
        if (current.parentNode != null) {
            path = this.relativeXPathFromParent(current) + path;
            if (1 == current.parentNode.nodeType &&
                current.parentNode.getAttribute("id")) {
                return this.preciseXPath("//" + this.xpathHtmlElement(current.parentNode.nodeName.toLowerCase()) +
                    "[@id=" + this.attributeValue(current.parentNode.getAttribute('id')) + "]" +
                    path, e);
            }
        } else {
            return null;
        }
        current = current.parentNode;
    }
    return null;
});

// The following code is fetched from https://github.com/firebug/firebug which is BSD licensed
// A 3rd party tool to build exact xpath /html/body/div/...
// Have not implemented this into locator_builder yet
var Xpath = {};
Xpath.getElementXPath = function(element)
{
    if (element && element.id)
        return '//*[@id="' + element.id + '"]';
    else
        return Xpath.getElementTreeXPath(element);
};

Xpath.getElementTreeXPath = function(element)
{
    var paths = [];

    // Use nodeName (instead of localName) so namespace prefix is included (if any).
    for (; element && element.nodeType == Node.ELEMENT_NODE; element = element.parentNode)
    {
        var index = 0;
        var hasFollowingSiblings = false;
        for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling)
        {
            // Ignore document type declaration.
            if (sibling.nodeType == Node.DOCUMENT_TYPE_NODE)
                continue;

            if (sibling.nodeName == element.nodeName)
                ++index;
        }

        for (var sibling = element.nextSibling; sibling && !hasFollowingSiblings;
            sibling = sibling.nextSibling)
        {
            if (sibling.nodeName == element.nodeName)
                hasFollowingSiblings = true;
        }

        var tagName = (element.prefix ? element.prefix + ":" : "") + element.localName;
        var pathIndex = (index || hasFollowingSiblings ? "[" + (index + 1) + "]" : "");
        paths.splice(0, 0, tagName + pathIndex);
    }

    return paths.length ? "/" + paths.join("/") : null;
};

Xpath.cssToXPath = function(rule)
{
    var regElement = /^([#.]?)([a-z0-9\\*_-]*)((\|)([a-z0-9\\*_-]*))?/i;
    var regAttr1 = /^\[([^\]]*)\]/i;
    var regAttr2 = /^\[\s*([^~=\s]+)\s*(~?=)\s*"([^"]+)"\s*\]/i;
    var regPseudo = /^:([a-z_-])+/i;
    var regCombinator = /^(\s*[>+\s])?/i;
    var regComma = /^\s*,/i;

    var index = 1;
    var parts = ["//", "*"];
    var lastRule = null;

    while (rule.length && rule != lastRule)
    {
        lastRule = rule;

        // Trim leading whitespace
        rule = Str.trim(rule);
        if (!rule.length)
            break;

        // Match the element identifier
        var m = regElement.exec(rule);
        if (m)
        {
            if (!m[1])
            {
                // XXXjoe Namespace ignored for now
                if (m[5])
                    parts[index] = m[5];
                else
                    parts[index] = m[2];
            }
            else if (m[1] == '#')
                parts.push("[@id='" + m[2] + "']");
            else if (m[1] == '.')
                parts.push("[contains(concat(' ',normalize-space(@class),' '), ' " + m[2] + " ')]");

            rule = rule.substr(m[0].length);
        }

        // Match attribute selectors
        m = regAttr2.exec(rule);
        if (m)
        {
            if (m[2] == "~=")
                parts.push("[contains(@" + m[1] + ", '" + m[3] + "')]");
            else
                parts.push("[@" + m[1] + "='" + m[3] + "']");

            rule = rule.substr(m[0].length);
        }
        else
        {
            m = regAttr1.exec(rule);
            if (m)
            {
                parts.push("[@" + m[1] + "]");
                rule = rule.substr(m[0].length);
            }
        }

        // Skip over pseudo-classes and pseudo-elements, which are of no use to us
        m = regPseudo.exec(rule);
        while (m)
        {
            rule = rule.substr(m[0].length);
            m = regPseudo.exec(rule);
        }

        // Match combinators
        m = regCombinator.exec(rule);
        if (m && m[0].length)
        {
            if (m[0].indexOf(">") != -1)
                parts.push("/");
            else if (m[0].indexOf("+") != -1)
                parts.push("/following-sibling::");
            else
                parts.push("//");

            index = parts.length;
            parts.push("*");
            rule = rule.substr(m[0].length);
        }

        m = regComma.exec(rule);
        if (m)
        {
            parts.push(" | ", "//", "*");
            index = parts.length-1;
            rule = rule.substr(m[0].length);
        }
    }

    var xpath = parts.join("");
    return xpath;
};

Xpath.getElementsBySelector = function(doc, css)
{
    var xpath = Xpath.cssToXPath(css);
    return Xpath.getElementsByXPath(doc, xpath);
};

Xpath.getElementsByXPath = function(doc, xpath)
{
    try
    {
        return Xpath.evaluateXPath(doc, xpath);
    }
    catch(ex)
    {
        return [];
    }
};

/**
 * Evaluates an XPath expression.
 *
 * @param {Document} doc
 * @param {String} xpath The XPath expression.
 * @param {Node} contextNode The context node.
 * @param {int} resultType
 *
 * @returns {*} The result of the XPath expression, depending on resultType :<br> <ul>
 *          <li>if it is XPathResult.NUMBER_TYPE, then it returns a Number</li>
 *          <li>if it is XPathResult.STRING_TYPE, then it returns a String</li>
 *          <li>if it is XPathResult.BOOLEAN_TYPE, then it returns a boolean</li>
 *          <li>if it is XPathResult.UNORDERED_NODE_ITERATOR_TYPE
 *              or XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, then it returns an array of nodes</li>
 *          <li>if it is XPathResult.ORDERED_NODE_SNAPSHOT_TYPE
 *              or XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, then it returns an array of nodes</li>
 *          <li>if it is XPathResult.ANY_UNORDERED_NODE_TYPE
 *              or XPathResult.FIRST_ORDERED_NODE_TYPE, then it returns a single node</li>
 *          </ul>
 */
Xpath.evaluateXPath = function(doc, xpath, contextNode, resultType)
{
    if (contextNode === undefined)
        contextNode = doc;

    if (resultType === undefined)
        resultType = XPathResult.ANY_TYPE;

    var result = doc.evaluate(xpath, contextNode, null, resultType, null);

    switch (result.resultType)
    {
        case XPathResult.NUMBER_TYPE:
            return result.numberValue;

        case XPathResult.STRING_TYPE:
            return result.stringValue;

        case XPathResult.BOOLEAN_TYPE:
            return result.booleanValue;

        case XPathResult.UNORDERED_NODE_ITERATOR_TYPE:
        case XPathResult.ORDERED_NODE_ITERATOR_TYPE:
            var nodes = [];
            for (var item = result.iterateNext(); item; item = result.iterateNext())
                nodes.push(item);
            return nodes;

        case XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE:
        case XPathResult.ORDERED_NODE_SNAPSHOT_TYPE:
            var nodes = [];
            for (var i = 0; i < result.snapshotLength; ++i)
                nodes.push(result.snapshotItem(i));
            return nodes;

        case XPathResult.ANY_UNORDERED_NODE_TYPE:
        case XPathResult.FIRST_ORDERED_NODE_TYPE:
            return result.singleNodeValue;
    }
};

Xpath.getRuleMatchingElements = function(rule, doc)
{
    var css = rule.selectorText;
    var xpath = Xpath.cssToXPath(css);
    return Xpath.getElementsByXPath(doc, xpath);
};