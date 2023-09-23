/* start the zeuz fnction */

/* On input */
$("#command-command").on("input", function(event) {
    var temp = getSelectedRecord();
    if (temp) {
        var div = getTdRealValueNode(document.getElementById(temp), 0);
        if (div.childNodes && div.childNodes[0]) {
            div.removeChild(div.childNodes[0]);
        }
        div.appendChild(document.createTextNode(event.target.value));

        var command_command = event.target.value;
        div = getTdShowValueNode(document.getElementById(temp), 0);
        if (div.childNodes && div.childNodes[0]) {
            div.removeChild(div.childNodes[0]);
        }
        div.appendChild(document.createTextNode(command_command));
        var s_case = getSelectedCase();
        if (s_case) {
            zeuz_testCase[s_case.id].records = document.getElementById("records-grid").innerHTML;
			modifyCaseSuite();		
        }
    }
});

/* Command value on input */
$("#command-value").on("input", function(event) {
    var temp = getSelectedRecord();
    if (temp) {
        var div = getTdRealValueNode(document.getElementById(temp), 2);
        if (div.childNodes && div.childNodes[0]) {
            div.removeChild(div.childNodes[0]);
        }
        div.appendChild(document.createTextNode(event.target.value));

        var command_value = event.target.value;
        div = getTdShowValueNode(document.getElementById(temp), 2);
        if (div.childNodes && div.childNodes[0]) {
            div.removeChild(div.childNodes[0]);
        }
        div.appendChild(document.createTextNode(command_value));

        var s_case = getSelectedCase();
        if (s_case) {
            zeuz_testCase[s_case.id].records = document.getElementById("records-grid").innerHTML;
			modifyCaseSuite();
        }
    }
});

/* command target on input */
$("#command-target").on("input", function(event) {
    var temp = getSelectedRecord();
    if (temp) {
        var div = getTdRealValueNode(document.getElementById(temp), 1);
        if (!(div.childNodes[0] && div.childNodes[0].textContent.includes("d-XPath") && event.target.value.includes("tac"))) {
            var real_command_target = event.target.value;
            if (real_command_target == "auto-located-by-tac") {
                var real_tac = getTargetDatalist(document.getElementById(temp)).options[0].text;
                if (real_tac == "") real_tac = "auto-located-by-tac";
                real_command_target = real_tac;
            }
            if (div.childNodes && div.childNodes[0]) {
                div.removeChild(div.childNodes[0]);
            }
            div.appendChild(document.createTextNode(real_command_target));

            var command_target = event.target.value;
            div = getTdShowValueNode(document.getElementById(temp), 1);
            if (div.childNodes && div.childNodes[0]) {
                div.removeChild(div.childNodes[0]);
            }
            div.appendChild(document.createTextNode(command_target));
            let datalist = getTargetDatalist(document.getElementById(temp));
        }

        var s_case = getSelectedCase();
        if (s_case) {
            zeuz_testCase[s_case.id].records = document.getElementById("records-grid").innerHTML;
            modifyCaseSuite();
        }
    }
});