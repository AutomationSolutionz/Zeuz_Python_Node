/* Zeuz shortable UI */

$(document).ready(function() {
    /* shortable the test container */
    $("#testCase-container").sortable({
        axis: "y",
        handle: "strong",
        items: ".message",
        scroll: true,
        revert: 300,
        scrollSensitivity: 20,
        start: function(event, ui) {
            ui.placeholder.height(ui.item.height());
        }
    });

    /* shortable the record gride  */
    $("#records-grid").sortable({
        axis: "y",
        items: "tr",
        scroll: true,
        revert: 200,
        scrollSensitivity: 20,
        connectWith: "#records-grid",
        helper: function(e, tr) {
            var $originals = tr.children();
            var $helper = tr.clone();
            $helper.children().each(function(index) {
                $(this).width($originals.eq(index).width());
            });
            return $helper;
        },
        update: function(event, ui) {
            getSelectedCase().classList.add("modified");
            getSelectedSuite().getElementsByTagName("strong")[0].classList.add("modified");
            closeConfirm(true);

            var start_ID = ui.item.attr("id"),
                end_ID = ui.item.prev().attr("id");
            reAssignId(start_ID, (end_ID.includes("count")?"records-0":(end_ID)));

            $('#records-grid .selectedRecord').removeClass('selectedRecord'); 
            $(".record-bottom").removeClass("active");
            ui.item.addClass('selectedRecord');

            document.getElementById("command-command").value = getCommandName(ui.item[0]);
            document.getElementById("command-target").value = getCommandTarget(ui.item[0], true);
            document.getElementById("command-value").value = getCommandValue(ui.item[0]);

            var s_case = getSelectedCase();
            if (s_case) {
                zeuz_testCase[s_case.id].records = document.getElementById("records-grid").innerHTML;
            }
        }
    });
});

function makeCaseSortable(suite) {
    var prevSuite = null;
    $(suite).sortable({
        axis: "y",
        items: "p",
        scroll: true,
        revert: 300,
        scrollSensitivity: 20,
        connectWith: ".message",
        start: function(event, ui) {
            ui.placeholder.html(ui.item.html()).css({ "visibility": "visible", "opacity": 0.3 });
            prevSuite = event.target;
        },
        update: function(event, ui) {
            if (prevSuite !== event.target)
                $(prevSuite).find("strong").addClass("modified");
            $(event.target).find("strong").addClass("modified");
            closeConfirm(true);
        }
    });
}
