/* global jQuery, padding */
var browserAppData = chrome || browser;
import $ from 'jquery';
// import jQuery from 'jquery';
// import 'jquery-ui/ui/widgets/sortable';
// import 'jquery-ui/themes/base/core.css';
// import 'jquery-ui/themes/base/theme.css';
// import 'jquery-ui/themes/base/selectable.css';
// import 'jquery-ui/ui/core';
// import 'jquery-ui/ui/widgets/selectable';

/* Zeuz Background Start */
var selfWindowId;
var contentWindowId;

var CustomFunction = {
	unsavedActionsFlag: false,
	isRecording: false,

	async LoadActions(case_value) {
		console.log('case_value',case_value);
		let result = await browserAppData.storage.local.get(['meta_data']);
		$('#case_data_wrap>tr').slice(result.meta_data['actionsLen']).remove();
		var len = $('#case_data_wrap>tr').length;
			$.each(case_value, function (single_case_index, single_case_value) {
			var disableClass = "";
			if (single_case_value.is_disable == 1) {
				disableClass = 'disabled-case';
			}
			let data_json = JSON.stringify(single_case_value);
			`ToDo: Use flexbox below`
			let tr = $(
			`<tr class="tr ${disableClass} pt-2 px-2 fs-7">
				<td class="col-1 td-no pt-1 ml-1 mb-2">
					<img src="small_logo.png" class="mr-2"><span>${single_case_index + len + 1}</span>
				</td>
				<td class="col-8 font_black pt-1 mb-2" data-case_commend="action">
				${single_case_value.name}
				</td>
				<td class="col-1 font_black" data-case_commend="action">
					<span class="material-icons-outlined del-btn">delete</span>
				</td>
			</tr>`);
			tr.attr('data-json',data_json);
			// console.log(JSON.parse(tr.attr('data-json')))
			$('#case_data_wrap').append(tr);
		})
	},
	
	PostProcess(actions){
		let new_actions = []
		for(let i = 0; i < actions.length; i++){
			let action = actions[i];
			if([null, undefined].includes(action)) continue;
			if(
				action.action == 'click' && 
				i < actions.length - 1 && 
				['click', 'text', 'double click', 'validate full text', 'validate full text by ai'].includes(actions[i+1].action)  &&
				action.xpath == actions[i+1].xpath
			) continue;
			new_actions.push(action);
		}
		return new_actions;
	},
	// This Function is called when Record_stop button is pressed
	SaveCaseDataAsJson() {
		setTimeout(()=>{	// Setting 0.5 sec so that the last action is saved properly in storage.local
			browserAppData.storage.local.get(null, function (result) {
				try {
					if (!result.recorded_actions) return;
					console.log("result.recorded_actions >>>",result.recorded_actions);
					result.recorded_actions = result.recorded_actions.filter(element => ![null, undefined, 'empty'].includes(element));

					// If the step is not totally blank we dont add 'go to link' action
					// var shift = false;
					// if(result.meta_data.stepNo == 1 && CustomFunction.caseDataArr[0].suite_value[0].case_value.length > 0 && result.recorded_actions.length > 0 && result.recorded_actions[0].action == 'go to link') 
					// 	shift = true
					// if(shift)
					// 	result.recorded_actions.shift();
					// result.recorded_actions.shift();
					let recorded_actions = CustomFunction.PostProcess(result.recorded_actions);
					CustomFunction.LoadActions(recorded_actions)
					browserAppData.storage.local.set({
						recorded_actions: recorded_actions,
					})
					CustomFunction.unsavedActionsFlag = true;
					
				} catch (e) {
					console.error(e);
				}
			})
		}, 500)
	},

	LoadEvent: function (case_data) {
		CustomFunction.LoadActions(case_data);
	},

	FetchActions: async function () {
		let result = await browserAppData.storage.local.get('meta_data');
		let meta_data = result.meta_data
		console.log("metdata =====",result);
		let resp = await $.ajax({
			type: "GET",
			url: `${meta_data.url}/ai_recorder_init`,
			headers: {
				// "Content-Type": "application/json",
				"X-Api-Key": `${meta_data.apiKey}`,
			},
			data: {"test_id":`${meta_data.testNo}`, "step_seq":`${meta_data.stepNo}`},
		});
		console.log("resp =====",resp);
		// $('#test_label').text(meta_data.testNo);

		let case_data = resp.step.actions.map(action => {
			return {
				"action": action.short.action,
				"element": action.short.element,
				"value": action.short.value,
				"is_disable": action.is_disable,
				"name": action.name,
				"main": action.main,
			}
		})
		CustomFunction.LoadEvent(case_data)
	}
}

$(document).ready(async function () {
	let result = await browserAppData.storage.local.get('meta_data');
	let meta_data = result.meta_data;
	if (result.meta_data.testNo != "TEST-0000"){
		// CustomFunction.FetchTestData(meta_data.testNo, meta_data.stepNo);
		CustomFunction.FetchActions();
	}
	$('#server_address').val(result.meta_data.url);
	$('#api_key').val(result.meta_data.apiKey);

	// $(function () {
	// 	$("#case_data_wrap").sortable({
	// 		// stop: function( event, ui ) {
	// 		start: function (event, ui) {},
	// 		stop: function (event, ui) {},
	// 		update: function (event, ui) {
	// 			var idx = 1
	// 			for (var step of $('#case_data_wrap').children('tr')) {
	// 				$($(step).children()[0]).find('span').text(idx++);
	// 			}
	// 			CustomFunction.unsavedActionsFlag = true;
	// 		}
	// 	});
	// 	$("#case_data_wrap").disableSelection();
	// });

	$(document).on('click', '.del-btn', function (e) {
		const target = $(e.target.parentElement.parentElement)
		const idx = target.attr('data-mainindex');
		target.remove();
		var i = 1;
		for (var step of $('#case_data_wrap').children('tr')) {
			$($(step).children()[0]).find('span').text(i++);
		}
		CustomFunction.unsavedActionsFlag = true;
	})

	$(document).on('click', '#fetch', async function () {
		try{
			$('#fetch').text('Fetching...');
			$("#fetch").attr('disabled', true).css('opacity',0.5);
	
			if (![4,5].includes($('#test_id').val().length)){
				alert('Provide 4 digit test-id. Ex: TEST-1234');
				$('#fetch').text('Error!!');
				$("#fetch").attr('disabled', true).css('opacity',0.5);
				setTimeout(()=>{
					$('#fetch').text('Fetch');
					$("#fetch").removeAttr('disabled').css('opacity',1);
				},1500)
				return;
			}
			// await CustomFunction.FetchTestData(`TEST-${$('#test_id').val()}`, 1);
			$('#case_data_wrap').html('');
			await CustomFunction.FetchActions();
			$('#fetch').text('Fetched!');
			setTimeout(()=>{
				$('#fetch').text('Fetch');
				$("#fetch").removeAttr('disabled').css('opacity',1);
			},1500)
			return;
		}
		catch(e){
			$('#fetch').text('Error!!');
			$("#fetch").attr('disabled', true).css('opacity',0.5);
			setTimeout(()=>{
				$('#fetch').text('Fetch');
				$("#fetch").removeAttr('disabled').css('opacity',1);
			},1500)
			return;
		}
	})

	$('input#test_id').attr('maxLength','5').keypress(function(e) {
		if (e.keyCode == 8) { return true; }
		return this.value.length < $(this).attr("maxLength");
	});

	$(document).on('change', '#step_select', async function () {
		// try {
		// 	if(CustomFunction.unsavedActionsFlag && confirm("Recorded actions will vanish. Save changes?")){
		// 		$("#save_button").click();
		// 	}
		// 	if($('#record_label').text() == 'Stop') return alert('First Stop the recording then Save');
		// 	var result = await browserAppData.storage.local.get(null);
		// 	result.meta_data['stepNo'] = this.value;
		// 	await browserAppData.storage.local.set({
		// 		meta_data: result.meta_data,
		// 	})
		// 	$('#case_data_wrap').html('');
		// 	CustomFunction.FetchActions();
		// 	CustomFunction.unsavedActionsFlag = false;
		// } catch (error) {
		// 	alert(error);
		// }
	})

	$(document).on('hover', '.del-btn', async function (e) {
		try {
			$(e.target).attr('opacity', 1);
			console.log($(e.target).attr('opacity'))
		} catch (error) {
			console.error(error);
		}
	})
	
	$( ".del-btn" ).hover(
		() => { //hover
		  $(this).attr("opacity",1);
		  console.log($(this).attr("opacity"))
		}, 
		() => { //out
		  $(this).removeClass("hover");
		}
  	);

	$(document).on('click', '#record', async function () {
		// let icon = $('#record_icon');
		// let label = $('#record_label');

		// if(label[0].textContent == 'Record'){
		// 	let result = await browserAppData.storage.local.get(['meta_data']);
		// 	result.meta_data['actionsLen'] = $('#case_data_wrap>tr').length;
		// 	browserAppData.storage.local.set({'meta_data': result.meta_data});
		// }
		// else{
		// 	browserAppData.storage.local.set({recorded_actions:[]});
		// }

		// label[0].textContent = label[0].textContent.trim() == 'Record' ? 'Stop' : 'Record';
		// icon.text(icon[0].textContent.trim() == 'camera' ? 'stop' : 'camera');

		// CustomFunction.isRecording = $('#record_label')[0].textContent != 'Record';
		// $('#save_wrap, #run_this_button, #run_wrap, #login_wrap').attr('disabled', true).css('opacity',0.5);
		// if (CustomFunction.isRecording) {			
			
				
		// }
		// else {
		// 	$('#save_wrap, #run_this_button, #run_wrap, #login_wrap').removeAttr('disabled').css('opacity',1);
		// 	// CustomFunction.SaveCaseDataAsJson();

		// }



	})	
	/* Save all newlly recorded actions with old actions and auto naming */
	$(document).on('click', '#save_button', async function () {
		try{
			if($('#record_label').text() == 'Stop') return alert('First Stop the recording then Save');
			$('#save_label').text('Saving...');
			$("#save_button").attr('disabled', true).css('opacity',0.5);
			let result = await browserAppData.storage.local.get(["meta_data"]);
			let trs = $('#case_data_wrap>tr');
			let case_value = trs.map((i) =>{
				return JSON.parse($(trs[i]).attr('data-json'));
			}).get();
			console.log('case_value', case_value);
			var save_data = {
				TC_Id: result.meta_data.testNo,
				step_sequence: result.meta_data.stepNo,
				step_data: JSON.stringify(case_value.map(action => {
					return action.main;
				})),
				step_id: result.meta_data.stepId,
				dataset_name: JSON.stringify(case_value.map((action, idx) => {
					return [
						action.name,
						idx+1,
						!action.is_disable,
					]
				}))
			}
			$.ajax({
				url: result.meta_data.url + '/Home/nothing/update_specific_test_case_step_data_only/',
				method: 'POST',
				data: save_data,
				headers: {
					// "Content-Type": "application/json",
					"X-Api-Key": `${result.meta_data.apiKey}`,
				},
				success: function(response) {
					console.log(response);
					$('#save_label').text('Success!');
					setTimeout(()=>{
						$('#save_label').text('Save');
						$("#save_button").removeAttr('disabled').css('opacity',1);
					},1500)
				},
				error: function(jqXHR, textStatus, errorThrown) {
					console.error(errorThrown);
					$('#save_label').text('Error!!');
					setTimeout(()=>{
						$('#save_label').text('Save');
						$("#save_button").removeAttr('disabled').css('opacity',1);
					}, 1500)
				}
			})
			CustomFunction.unsavedActionsFlag = false;
		}
		catch(e){
			console.error(e);
			$('#save_label').text('Error!!');
			setTimeout(()=>{
				$('#save_label').text('Save');
				$("#save_button").removeAttr('disabled').css('opacity',1);
			}, 1500)
		}
		
	});
	
	$(document).on('click', '#authenticate', async function () {
		try {
			$('#authenticate').text('Authenticaing...');
			$("#authenticate").attr('disabled', true).css('opacity',0.5);
			var result = await browserAppData.storage.local.get(["meta_data"]);
			var server_address = $('#server_address').val();
			server_address = server_address.endsWith("/") ? server_address.slice(0,-1) : server_address
			var api_key = $('#api_key').val();
			$.ajax({
				url: `${server_address}/api/auth/token/verify`,
				method: 'GET',
				data: {
					api_key: api_key,
				},
				success: function(response) {
					console.log(response);
					result.meta_data.url = server_address;
					result.meta_data.apiKey = api_key;
					browserAppData.storage.local.set({
						meta_data: result.meta_data
					})
					$('#authenticate').text('Success!');
					setTimeout(()=>{
						$('#authenticate').text('Authenticate');
						$("#authenticate").removeAttr('disabled').css('opacity',1);
					},1500)
				},
				error: function(jqXHR, textStatus, errorThrown) {
					console.error(errorThrown);
					$('#authenticate').text('Error!!');
					setTimeout(()=>{
						$('#authenticate').text('Authenticate');
						$("#authenticate").removeAttr('disabled').css('opacity',1);
					},1500)
				}
			})
		} catch (error) {
			console.error(error);
			$('#authenticate').text('Error!!');
			setTimeout(()=>{
				$('#authenticate').text('Authenticate');
				$("#authenticate").removeAttr('disabled').css('opacity',1);
			},1500)
		}
		
	});
	$(window).off('beforeunload');
	$(document).on('click', '#run_button', async function () {
		try {
			$('#run_label').text('Running...');
			$("#run_button").attr('disabled', true).css('opacity',0.5);
			var result = await browserAppData.storage.local.get(["meta_data"]);
			const input = {
				method: "POST",
				headers: {
					// "Content-Type": "application/json",
					"X-Api-Key": result.meta_data.apiKey,
				}
			}
			var r = await fetch(result.meta_data.url + '/run_config_ai_recorder/', input)
			var response = await r.json();					
			console.log("response_1", response);

			const machine = response["machine"];
			const project_id = response["project_id"];
			const team_id = response["team_id"];
			const user_id = response["user_id"];

			if (navigator.userAgent.indexOf("Edg") != -1)
				var browser = 'Microsoft Edge Chromium'
			else if (navigator.userAgent.indexOf("Chrome") != -1) 
				var browser = 'Chrome'
			let dependency = {"Browser": browser, "Mobile": "Android"}
			const run_data = {
				"test_case_list": JSON.stringify([result.meta_data.testNo]),
				"dependency_list": JSON.stringify(dependency),
				"all_machine": JSON.stringify([machine]),
				"debug": 'yes',
				"debug_clean": "yes",
				"debug_steps": JSON.stringify([]), // [] means Run all steps
				"RunTestQuery": JSON.stringify([result.meta_data.testNo, machine]),
				"dataAttr": JSON.stringify(["Test Case"]),
				"project_id": project_id,
				"team_id": team_id,
				"user_id": user_id,
			}
			var url = `${result.meta_data.url}/Home/nothing/Run_Test/`;

			$.ajax({
				url: url,
				method: 'GET',
				data: run_data,
				headers: {
					"Content-Type": "application/json",
					"X-Api-Key": result.meta_data.apiKey,
				},
				success: function(response) {
					console.log("response_2",response);
					$('#run_label').text('Queued!');
					setTimeout(()=>{
						$('#run_label').text('Run all');
						$("#run_button").removeAttr('disabled').css('opacity',1);
					},1500)
				},
				error: function(jqXHR, textStatus, errorThrown) {
					console.error(errorThrown);
					$('#run_label').text('Error!!');
					setTimeout(()=>{
						$('#run_label').text('Run all');
						$("#run_button").removeAttr('disabled').css('opacity',1);
					},1500)
				}
			})
		} catch (error) {
			console.error(error);
			$('#run_label').text('Error!!');
			setTimeout(()=>{
				$('#run_label').text('Run all');
				$("#run_button").removeAttr('disabled').css('opacity',1);
			},1500)
		}
	})
	$(document).on('click', '#run_this_button', async function () {
		try {
			$('#run_this_label').text('Running...');
			$("#run_this_button").attr('disabled', true).css('opacity',0.5);
			var result = await browserAppData.storage.local.get(["meta_data"]);
			const input = {
				method: "POST",
				headers: {
					// "Content-Type": "application/json",
					"X-Api-Key": result.meta_data.apiKey,
				}
			}
			var r = await fetch(result.meta_data.url + '/run_config_ai_recorder/', input)
			var response = await r.json();					
			console.log("response_1", response);

			const machine = response["machine"];
			const project_id = response["project_id"];
			const team_id = response["team_id"];
			const user_id = response["user_id"];

			if (navigator.userAgent.indexOf("Edg") != -1)
				var browser = 'Microsoft Edge Chromium'
			else if (navigator.userAgent.indexOf("Chrome") != -1) 
				var browser = 'Chrome'
			let dependency = {"Browser": browser, "Mobile": "Android"}
			const run_data = {
				"test_case_list": JSON.stringify([result.meta_data.testNo]),
				"dependency_list": JSON.stringify(dependency),
				"all_machine": JSON.stringify([machine]),
				"debug": 'yes',
				"debug_clean": "yes",
				"debug_steps": JSON.stringify([result.meta_data.stepNo]), // [] means Run all steps
				"RunTestQuery": JSON.stringify([result.meta_data.testNo, machine]),
				"dataAttr": JSON.stringify(["Test Case"]),
				"project_id": project_id,
				"team_id": team_id,
				"user_id": user_id,
			}
			var url = `${result.meta_data.url}/Home/nothing/Run_Test/`;

			$.ajax({
				url: url,
				method: 'GET',
				data: run_data,
				headers: {
					"Content-Type": "application/json",
					"X-Api-Key": result.meta_data.apiKey,
				},
				success: function(response) {
					console.log("response_2",response);
					$('#run_this_label').text('Queued!');
					setTimeout(()=>{
						$('#run_this_label').text('Run this');
						$("#run_this_button").removeAttr('disabled').css('opacity',1);
					},1500)
				},
				error: function(jqXHR, textStatus, errorThrown) {
					console.error(errorThrown);
					$('#run_this_label').text('Error!!');
					setTimeout(()=>{
						$('#run_this_label').text('Run this');
						$("#run_this_button").removeAttr('disabled').css('opacity',1);
					},1500)
				}
			})
		} catch (error) {
			console.error(error);
			$('#run_label').text('Error!!');
			setTimeout(()=>{
				$('#run_label').text('Run this');
				$("#run_button").removeAttr('disabled').css('opacity',1);
			},1500)
		}
	})
})

browserAppData.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.action == 'record_start') {

        }
        else if (request.action == 'record_finish____(disabled)') {
            CustomFunction.SaveCaseDataAsJson();
        }
    }
);

browserAppData.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.attachRecorderRequest) {
    // This is required when you are recording and new page loaded and you need to add the Event_handlers again
        if (CustomFunction.isRecording) {
            browserAppData.tabs.sendMessage(sender.tab.id, {attachRecorder: true});
        }
        return;
    }
});

browserAppData.runtime.onMessage.addListener(function contentWindowIdListener(message) {
	// From background script when creating panel
    if (message.selfWindowId != undefined && message.commWindowId != undefined) {
        selfWindowId = message.selfWindowId;
        contentWindowId = message.commWindowId;
        browserAppData.runtime.onMessage.removeListener(contentWindowIdListener);
    }
})

setInterval(async ()=>{
	if (!CustomFunction.isRecording) return;
	browserAppData.storage.local.get(null, function (result) {
		if (result.recorded_actions.length === 0) return;
		// console.log("Opacity =================", result.recorded_actions);
		for(let i = 0; i < result.recorded_actions.length; i++){
			if (result.recorded_actions[i] === 'empty'){
				// console.log("Opacity 2222 =================", result.recorded_actions);
				$("#record_label").text("Recording...");
				$("#record").attr('disabled', true).css('opacity',0.5);
				return;
			}
		}
		if($("#record_label").text() == 'Recording...'){
			$("#record").removeAttr('disabled').css('opacity',1);
			$("#record_label").text("Stop");
			$('#record_icon').text('stop');
			console.log('Record elem change panel_recorder 1');
		}
	})
	return;
}, 500)
var recording_flag = false
setInterval(async ()=>{
	if (!CustomFunction.isRecording) return;
	browserAppData.storage.local.get(null, function (result) {
		if (result.recorded_actions.length === 0) return;
		for(let i = 0; i < result.recorded_actions.length; i++){
			if (result.recorded_actions[i] === 'empty'){
				if (!recording_flag) recording_flag = true;
				else{
					var new_arr = [];
					for (const action of result.recorded_actions) {
						if (action !== 'empty') new_arr.push(action);
					}
					result.recorded_actions = new_arr;
					browserAppData.storage.local.set({
						recorded_actions: new_arr
					})
					recording_flag = false;
					if($("#record_label").text() == 'Recording...'){
						$("#record").removeAttr('disabled').css('opacity',1);
						$("#record_label").text("Stop");
						$('#record_icon').text('stop');
						console.log('Record elem change panel_recorder 2');
					}
				}
				return;
			}
		}
	})
	return;
}, 30000)
