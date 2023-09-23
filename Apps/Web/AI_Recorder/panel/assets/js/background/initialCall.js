/* Start the initial js */
var zeuz_wait = {
    next_command_wait: false,
    done: true
};

var zeuz_testSuite = {
    count: 0
};

var zeuz_testCase = {
    count: 0
};

/* clean the panel */
function clean_panel() {
    emptyNode(document.getElementById("records-grid"));
    emptyNode(document.getElementById("command-target-list"));
    emptyNode(document.getElementById("target-dropdown"));
    document.getElementById("command-command").value = "";
    document.getElementById("command-target").value = "";
    document.getElementById("command-value").value = "";
}
