/* Zeuz panel settings */
$(document).ready(function() {
    var tac = false;
    var userid = browser.runtime.id;
    $(".tablesorter").tablesorter();
    $("#command-dropdown").css({
        'width': $("#command-command").width() + 29 + "px"
    });
    $("#target-dropdown").css({
        'width': $("#command-target").width() + 29 + "px"
    });
    $("#options").click(function() {
        browser.runtime.openOptionsPage();
    });
    $(window).resize(function() {
        $("#target-dropdown").css({
            'width': $("#command-target").width() + 29 + "px"
        });

        $("#command-dropdown").css({
            'width': $("#command-command").width() + 29 + "px"
        });
    });
    $(".fa-chevron-down").click(function() {
        dropdown($("#" + $(this).attr("id") + "dropdown"));
        $(".w3-show").on("mouseleave", function() {
            dropdown($(this));
        });
    });

    $("#command-grid").colResizable({ liveDrag: true, minWidth: 75 });
    $(function() {
        $.fn.fixMe = function() {
            return this.each(function() {
                var $this = $(this),
                    $t_fixed;

                function init() {
                    $this.wrap('<div class="container" />');
                    $t_fixed = $this.clone();
                    $t_fixed.find("tbody").remove().end().addClass("fixed").insertBefore($this);
                    $t_fixed.find("th").each(function(index) {
                        var $self = $(this);
                        $this.find("th").eq(index).on("DOMAttrModified", function(e) {
                            $self.css("width", $(this).outerWidth() + "px");
                        });
                    });
                    resizeFixed();
                }

                function scrollFixed() {
                    var offset = $(this).scrollTop(),
                        tableOffsetTop = $this.offset().top,
                        tableOffsetBottom = tableOffsetTop + $this.height() - $this.find("thead").height();
                    if (offset < tableOffsetTop || offset > tableOffsetBottom) {
                        $t_fixed.hide();
                    } else if (offset >= tableOffsetTop && offset <= tableOffsetBottom && $t_fixed.is(":hidden")) {
                        $t_fixed.show();
                    }
                    var tboffBottom = (parseInt(tableOffsetBottom));
                    var tboffTop = (parseInt(tableOffsetTop));

                    if (offset >= tboffBottom && offset <= tableOffsetBottom) {
                        $t_fixed.find("th").each(function(index) {
                            $(this).css("width", $this.find("th").eq(index).outerWidth() + "px");
                        });
                    }
                }

                function resizeFixed() {
                    $t_fixed.find("th").each(function(index) {
                        $(this).css("width", $this.find("th").eq(index).outerWidth() + "px");
                    });
                }

                $(window).resize(resizeFixed);
                $(window).scroll(scrollFixed);
                init();
            });
        };
    });

    $("#slider").slider({
        min: 0,
        max: 3000,
        value: 0,
        step: 600
    }).slider("pips", {
        rest: "label", labels: ["Fast", "", "", "", "", "Slow"]
    });
    
    $("#command-dropdown,#command-command-list").html(genCommandDatalist());

    $(".record-bottom").click(function() {
        $(this).addClass("active");
        $('#records-grid .selectedRecord').removeClass('selectedRecord');
    });
});

var dropdown = function(node) {
    if (!node.hasClass("w3-show")) {
        node.addClass("w3-show");
        setTimeout(function() {
            $(document).on("click", clickWhenDropdownHandler);
        }, 200);
    } else {
        $(".w3-show").off("mouseleave");
        node.removeClass("w3-show");
        $(document).off("click", clickWhenDropdownHandler);
    }
};

var clickWhenDropdownHandler = function(e) {
    var event = $(e.target);
    if ($(".w3-show").is(event.parent())) {
        $(".w3-show").prev().prev().val(event.val()).trigger("input");
    }
    dropdown($(".w3-show"));
};

function closeConfirm(bool) {
    if (bool) {
        $(window).on("beforeunload", function(e) {
            var confirmationMessage = "You have a modified suite!";
            e.returnValue = confirmationMessage;
            return confirmationMessage;
        });
    } else {
        if (!$("#testCase-grid").find(".modified").length)
            $(window).off("beforeunload");
    }
}

var formalCommands;

/* custom function */
function supportedAllCommand(){
    var supportedCommand = [
        "addSelection",
        "answerOnNextPrompt",
        "assertAlert",
        "assertConfirmation",
        "assertPrompt",
        "assertText",
        "assertTitle",
        "assertValue",
        "chooseCancelOnNextConfirmation",
        "chooseCancelOnNextPrompt",
        "chooseOkOnNextConfirmation",
        "clickAt",
        "close",
        "doubleClickAt",
        "dragAndDropToObject",
        "echo",
        "editContent",
        "mouseDownAt",
        "mouseMoveAt",
        "mouseOut",
        "mouseOver",
        "mouseUpAt",
        "pause",
        "removeSelection",
        "runScript",
        "select",
        "selectFrame",
        "selectWindow",
        "sendKeys",
        "store",
        "storeEval",
        "storeText",
        "storeTitle",
        "storeValue",
        "submit",
        "type",
        "verifyText",
        "verifyTitle",
        "verifyValue"
    ];

    var supportedCommand = _loadSeleniumCommands();

    var supportedCommandNew = [];
    supportedCommand.push("type");
    $.each(supportedCommand,function(indx,val){
        if(val == "assertValue"){
            val = "validate text";
        }else if(val == "close"){
            val = "teardown";
        }else if(val == "open"){
            val = "go to link";
        }else if(val == "pause"){
            val = "sleep";
        }else if(val == "select"){
            val = "Select by Visible Text";
        }else if(val == "sendKeys"){
            val = "Keystroke keys";
        }else if(val == "store"){
            val = "save";
        }else if(val == "submit"){
            val = "click(submit)";
        }else if(val == "type"){
            val = "text";
        }
        supportedCommandNew.push(val);
    })

    return supportedCommandNew;


}


function genCommandDatalist() {
    var supportedCommand = [
        "addSelection",
        "answerOnNextPrompt",
        "assertAlert",
        "assertConfirmation",
        "assertPrompt",
        "assertText",
        "assertTitle",
        "assertValue",
        "chooseCancelOnNextConfirmation",
        "chooseCancelOnNextPrompt",
        "chooseOkOnNextConfirmation",
        "clickAt",
        "close",
        "doubleClickAt",
        "dragAndDropToObject",
        "echo",
        "editContent",
        "mouseDownAt",
        "mouseMoveAt",
        "mouseOut",
        "mouseOver",
        "mouseUpAt",
        "pause",
        "removeSelection",
        "runScript",
        "select",
        "selectFrame",
        "selectWindow",
        "sendKeys",
        "store",
        "storeEval",
        "storeText",
        "storeTitle",
        "storeValue",
        "submit",
        "type",
        "verifyText",
        "verifyTitle",
        "verifyValue"
    ];

    supportedCommand = _loadSeleniumCommands();

    var datalistHTML = "";
    formalCommands = {};
    supportedCommand.forEach(function(command) {
        datalistHTML += ('<option value="' + command + '">' + command + '</option>\n');
        formalCommands[command.toLowerCase()] = command;
    });

    return datalistHTML;
}