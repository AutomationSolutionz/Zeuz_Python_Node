/* Zeuz start function */
var seleniumBase = undefined;
var olderTestCaseFiles = undefined;

function checkIsTestSuite(input) {
    if (input.search("suiteTable") >= 0) {
        return true;
    }
    return false;
}

function transformTestSuiteVersion(str) {
    let component = splitTbody(str);
    caseResult = loadCaseIntoSuite(component[1]);
    return caseResult;
}

function loadCaseIntoSuite(str) {
    let href = [];
    let anchor = str.match(/<a href=\"[^\"]*\">/g);
    for (let i=0 ; i<anchor.length ; i++) {
        let temp = anchor[i];
        href[i] = temp.substring(temp.indexOf("\"")+1, temp.lastIndexOf("\""));
    }

    let testCaseName = "";
    testCaseName += ("\"" + href[0] + "\"");
    for (let i=1 ; i<href.length ; i++) {
        testCaseName += (", \"" + href[i] + "\"");
    }

    openOldFileDialog("This is test suite of early version of Selenium IDE. Please load " + testCaseName)
        .then(function(answer) {
            if (answer == "true") {
                document.getElementById("load-older-testSuite").click();
            } else {
                return ;
            }
    });
    return;
}

function transformVersion(input) {
    getSeleniumBase(input);
    let component = splitTbody(input);
    component[1] = addDatalistTag(component[1]);
    component[0] = addMeta(component[0]);
    return component[0] + component[1] + component[2];
}

document.getElementById("load-older-testSuite").addEventListener("change", afterLoadOlderTestCase, false);
function afterLoadOlderTestCase(event) {
    event.stopPropagation();
    olderTestCaseFiles = this.files;
    readOlderTestCase(this.files[0], 0, this.files.length);
}

function readOlderTestCase(file, index, filesLength) {
    var reader = new FileReader();
    reader.onload = function(event) {
        let result = event.target.result;
        olderTestSuiteResult = appendOlderTestCase(event.target.result);
        if(index == filesLength-1) {
            appendTestSuite(olderTestSuiteFile, olderTestSuiteResult);
        } else {
            index += 1;
            readOlderTestCase(olderTestCaseFiles[index], index, filesLength);
        }
    };
    reader.onerror = function(e) {
        console.log("Error", e);
    };
    reader.readAsText(file);
}

function appendOlderTestCase(str) {
    getSeleniumBase(str);
    let postindex = olderTestSuiteResult.indexOf("</body>");
    let fore = olderTestSuiteResult.substring(0, postindex);
    let back = olderTestSuiteResult.substring(postindex);
    fore += addDatalistTag(splitTag(str, "table"));

    return fore + back;
}

function getSeleniumBase(str) {
    let bases = str.match(/<link rel="selenium\.base" href=\"[^\"]*\"/g);
    if (bases) {
        seleniumBase = bases[0].substring(bases[0].indexOf("href=\"")+6, bases[0].lastIndexOf("\""));
        if (seleniumBase.charAt(seleniumBase.length-1) == "/") {
            seleniumBase = seleniumBase.substring(0, seleniumBase.length-1);
        }
    } else {
        seleniumBase = '';
    }
}

function checkIsVersion2(input) {
    if (input.search("<meta name=\"description\" content=\"ZeuZ2\">") >= 0) {
        return true;
    }
    return false;
}

function appendOpenCommandTarget(str) {
    return "<td>" + seleniumBase + str.substring(4, str.length-5) + "</td>";
}

function appendTestSuite(suiteFile, suiteResult) {
    var id = "suite" + zeuz_testSuite.count;
    zeuz_testSuite.count++;
    var suiteFileName;
    if (suiteFile.name.lastIndexOf(".") >= 0) {
        suiteFileName = suiteFile.name.substring(0, suiteFile.name.lastIndexOf("."));
    } else {
        suiteFileName = suiteFile.name;
    }

    addTestSuite(suiteFileName, id);
    zeuz_testSuite[id] = {
        file_name: suiteFile.name,
        title: suiteFileName
    };

    test_case = suiteResult.match(/<table[\s\S]*?<\/table>/gi);
    if (test_case) {
        for (var i = 0; i < test_case.length; ++i) {
            readCase(test_case[i]);
        }
    }

    setSelectedSuite(id);
    clean_panel();
}

function splitTbody(str) {
    let preindex = str.indexOf("<tbody>");
    let postindex = str.indexOf("</tbody>");

    let component = [];
    component[0] = str.substring(0, preindex);
    component[1] = str.substring(0, postindex+8).substring(preindex);
    component[2] = str.substring(postindex+8);

    return component;
}

function splitForeAndBack(str, tag) {
    let postindex = str.indexOf(tag);
    return [str.substring(0, postindex), str.substring(postindex)];
}

function splitTag(str, tag) {
    let preindex = str.indexOf("<" + tag);
    let postindex = str.indexOf("</" + tag + ">");
    return str.substring(preindex, postindex+3+tag.length);
}

function addDatalistTag(str) {
    var tempFore = "";
    if (str.search("<table") >= 0) {
        var tbodyIndex = str.indexOf("<tbody>");
        tempFore = str.substring(0, tbodyIndex);
        str = str.substring(tbodyIndex);
    }

    let preindex = str.indexOf("<td>");
    let postindex = str.indexOf("</td>");
    let count = 0;
    let isOpenCommand = false;
    while (preindex>=0 && postindex>=0) {
        if (count == 0) {
            if (str.substring(preindex, postindex).search("open") >= 0) {
                isOpenCommand = true;
            }
        }

        if (count == 1) {
            if (isOpenCommand) {
                let originBase = str.substring(preindex, postindex+5)
                let insertBase = appendOpenCommandTarget(originBase);
                str = str.substring(0, preindex) + insertBase + str.substring(postindex+5);
                postindex += (insertBase.length-originBase.length);
                isOpenCommand = false;
            }

            let insert = "<datalist>" + addOption(str.substring(preindex, postindex)) + "</datalist>";
            str = str.substring(0, postindex) + insert + str.substring(postindex);
            postindex += insert.length;
        }

        preindex = str.indexOf("<td>", preindex+1);
        postindex = str.indexOf("</td>", postindex+1);
        count = (count+1) % 3;
    }
    return tempFore + str;
}

function addMeta(str) {
    let part = splitForeAndBack(str, "</head>");
    return part[0] + "<meta name=\"description\" content=\"ZeuZ2\">" + part[1];
}

function addOption(str) {
    return "<option>" + str.substring(4) + "</option>";
}

var openOldFileDialog = function(question) {
    var defer = $.Deferred();
    $('<div></div>')
        .html(question)
        .dialog({
            title: "Open Test Cases",
            resizable: false,
            height: "auto",
            width: 400,
            modal: true,
            buttons: {
                "browse...": function() {
                    defer.resolve("true");
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
