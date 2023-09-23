/* Zuez function start */
var olderTestSuiteResult = undefined;
var olderTestSuiteFile = undefined;

document.getElementById("load-testSuite-hidden").addEventListener("change", function(event) {
    event.stopPropagation();
    for (var i = 0; i < this.files.length; i++) {
        readSuite(this.files[i]);
    }
    this.value = null;
}, false);

document.getElementById("load-testSuite-show").addEventListener("click", function(event) {
    event.stopPropagation();
    document.getElementById('load-testSuite-hidden').click();
}, false);

document.getElementById("load-testSuite-show-menu").addEventListener("click", function(event) {
    event.stopPropagation();
    document.getElementById('load-testSuite-hidden').click();
}, false);

$(document).ready(function() {

    $("#testCase-container").on('drag dragstart dragend dragover dragenter dragleave drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
    })
    .on('dragover dragenter', function() {
        $("#testCase-container").addClass('is-dragover');
    })
    .on('dragleave dragend drop', function() {
        $("#testCase-container").removeClass('is-dragover');
    })
    .on('drop', function(e) {
        let droppedFiles = e.originalEvent.dataTransfer.files;
        let droppedFilesLength = droppedFiles.length;
        for (var i = 0; i < droppedFilesLength; i++) {
            readSuite(droppedFiles[i]);
        }
    });
});

function fileToPanel(f) {
    var output = f.match(/<tbody>[\s\S]+?<\/tbody>/);
    if (!output) {
        return null;
    }
    output = output[0]
        .replace(/<tbody>/, "")
        .replace(/<\/tbody>/, "");
    var tr = output.match(/<tr>[\s\S]*?<\/tr>/gi);
    output = "";
    if (tr)
        for (var i = 0; i < tr.length; ++i) {
            pattern = tr[i].match(/(?:<tr>)([\s]*?)(?:<td>)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<datalist>)([\s\S]*?)(?:<\/datalist>([\s]*?)<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<\/tr>)/);
            if (pattern === null) {
                pattern = tr[i].match(/(?:<tr>)([\s]*?)(?:<td class="break">)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<datalist>)([\s\S]*?)(?:<\/datalist>([\s]*?)<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<\/tr>)/);
            }
            if (pattern == null) {
                pattern = tr[i].match(/(?:<tr>)([\s]*?)(?:<td class="[\w\s-]*?">)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<datalist>)([\s\S]*?)(?:<\/datalist>([\s]*?)<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<\/tr>)/);
            }
            var index = pattern[4].indexOf('\n');
            if (index > 0) {
                pattern[4] = pattern[4].substring(0, index);
            } else if (index === 0) {
                pattern[4] = '';
            }
            var new_tr = '<tr>' + pattern[1] + '<td><div style="display: none;">' + pattern[2] + '</div><div style="overflow:hidden;height:15px;"></div></td>' + pattern[3] + '<td><div style="display: none;">' + pattern[4] +
                '</div><div style="overflow:hidden;height:15px;"></div>\n        ' + '<datalist>' + pattern[5] + '</datalist>' + pattern[6] + '</td>' +
                pattern[7] + '<td><div style="display: none;">' + pattern[8] + '</div><div style="overflow:hidden;height:15px;"></div></td>' + pattern[9] + '</tr>';

            output = output + new_tr + "\n";

        }
    output = '<input id="records-count" value="' + ((!tr) ? 0 : tr.length) + '" type="hidden">' + output;
    return output;
}

function readCase(f) {
    var grid_content = fileToPanel(f);
    if (grid_content) {
        clean_panel();
        document.getElementById("records-grid").innerHTML = escapeHTML(grid_content);
        var count = getRecordsNum();
        if (count !== '0') {
            reAssignId("records-1", "records-" + count);
            var r = getRecordsArray();
            for (var i = 1; i <= count; ++i) {
                for (var j = 0; j < 3; ++j) {
                    var node = document.getElementById("records-" + i).getElementsByTagName("td")[j];
                    var adjust = unescapeHtml(node.childNodes[0].innerHTML);
                    node.childNodes[1].appendChild(document.createTextNode(adjust));
                }
            }
            attachEvent(1, count);
        }
    } else {
        clean_panel();
    }

    var id = "case" + zeuz_testCase.count;
    zeuz_testCase.count++;
    var records = document.getElementById("records-grid").innerHTML;
    var case_title = f.match(/(?:<thead>[\s\S]*?<td rowspan="1" colspan="3">)([\s\S]*?)(?:<\/td>)/)[1];
    zeuz_testCase[id] = {
        records: records,
        title: case_title
    };
    addTestCase(case_title, id);
}

function readSuite(f) {
    var reader = new FileReader();
    if (!f.name.includes("htm")) return;
    reader.readAsText(f);

    reader.onload = function(event) {
        //setTimeout(saveData, 0);
        var test_suite = reader.result;
        if (!checkIsVersion2(test_suite)) {
            if (test_suite.search("<table") > 0 && test_suite.search("<datalist>") < 0) {
                if (checkIsTestSuite(test_suite)) {
                    olderTestSuiteResult = test_suite.substring(0, test_suite.indexOf("<table")) + test_suite.substring(test_suite.indexOf("</body>"));
                    olderTestSuiteFile = f;
                    loadCaseIntoSuite(test_suite);
                    return;
                } else {
                    test_suite = transformVersion(test_suite);
                }
            }
            test_suite = addMeta(test_suite);
        }

        appendTestSuite(f, test_suite);
        return;
    };
    reader.onerror = function(e) {
        console.log("Error", e);
    };
}