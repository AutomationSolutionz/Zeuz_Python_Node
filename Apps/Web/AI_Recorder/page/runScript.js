/* Start zeuz run script */
function zeuzSendMessage(result) {
	window.postMessage({
		direction: "from-page-runscript",
		result: result
	}, "*");
}

function zeuzRunScript(script) {
	var result;
	try {
		var scriptResult = script();
		result = {
			status: true,
			result: scriptResult
		}
	} catch (e) {
		var message = 'Error: ' + e.toString();
		result = {
			status: false,
			result: message
		}
	}
	zeuzSendMessage(result);
}

window.addEventListener("message", function(event) {
	if (event.source == window && event.data && event.data.direction == "from-content-runscript") {
		isWanted = true;
		var doc = window.document;
		var scriptTag = doc.createElement("script");
		scriptTag.type = "text/javascript"
		scriptTag.text = 'zeuzRunScript(function() {' + event.data.script + ';})';
		doc.body.appendChild(scriptTag);
	}
});
