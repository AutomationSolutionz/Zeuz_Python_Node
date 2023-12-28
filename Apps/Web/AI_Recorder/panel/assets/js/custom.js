browserAppData = chrome || browser;
var CustomFunction = {
	caseDataArr: {},
	StepCopyData: null,
	copyType: null,
	is_auth_user: false,
	isPreFocus: false,
	isPreFocusElement: false,
	/* Hidden field*/
	LoadTheRecordDataHtml(recordData) {
		CustomFunction.FetchChromeCaseData()
		.then(() => {
			/* Fetch selected suite */
			var selected_suite = 0;

			var selectedCase = -1;
			$('.case-main-wrap').each(function () {
				if ($(this).hasClass('selected-case')) {
					selectedCase = $(this).data('mainindex');
				}
			});

			var caseDataValues = CustomFunction.caseDataArr[selected_suite].suite_value;
			if (selected_suite != -1 && selectedCase != -1 && caseDataValues.length > 0 && CustomFunction.caseDataArr[selected_suite].suite_value[selectedCase] != undefined) {
				var actionData = CustomFunction.caseDataArr[selected_suite].suite_value[selectedCase];
				if (actionData.case_value != undefined && actionData.case_value.length > 0 && (actionData.is_disable == undefined || actionData.is_disable == 0)) {


					//var caseHtml = `<input id="records-count" value="`+actionData.case_value.length+`" type="hidden">`;
					var caseHtml = ``;
					var caseValLength = 0;
					var disableCount = 0;
					$.each(actionData.case_value, function (indx, val) {
						if (val.is_disable == undefined || val.is_disable == 0) {
							caseValLength++;
							caseHtml += `<tr id="records-` + caseValLength + `" class="odd">
								<td>
									<div style="display: none;">` + val.action + `</div>
									<div style="overflow:hidden;height:15px;">` + val.action + `</div>
								</td>
								<td>
									<div style="display: none;">` + val.element + `</div>
									<div style="overflow:hidden;height:15px;">` + val.element + `</div>
		        					<datalist>
		        						<option>
		        							` + val.element + `
		        						</option>
		        					</datalist>
		        				</td>
		        				<td>
		        					<div style="display: none;">` + val.value + `</div>
		        					<div style="overflow:hidden;height:15px;">` + val.value + `</div>
		        				</td>
							</tr>`;
						} else {
							disableCount = disableCount + 1;
						}
					})
					caseHtml += `<input id="records-count" value="` + caseValLength + `" type="hidden">`;
					caseHtml += `<input id="disable-count" value="` + disableCount + `" type="hidden">`;
					$('#records-grid').html(caseHtml);
				} else {
					caseHtml = `<input id="records-count" value="0" type="hidden">`;
					$('#records-grid').html(caseHtml);
				}
			} else {
				caseHtml = `<input id="records-count" value="0" type="hidden">`;
				$('#records-grid').html(caseHtml);
			}		
		})
	},

	LoadCaseSuiteHtml(SuiteMainArr) {
		var suiteHtml = ``;
		if (SuiteMainArr != undefined && SuiteMainArr.length > 0) {
			$.each(SuiteMainArr, function (indx, val) {
				if (indx < 5) {
					var suite_name = val.suite_name;
					var extraCls = '';
					var ChildExtraCls = '';
					if (indx == 0) {
						extraCls = 'head_text pl-3';
						ChildExtraCls = 'current_selected_tab';
					}
					suiteHtml += `<li class="` + extraCls + `">
					<a data-toggle="tab" class="single-suite-tab suite-tab-` + indx + ` ` + ChildExtraCls + `" href="javascript:void(0);" data-suite="` + indx + `">` + suite_name + `</a>
					<span class="suite-action" style="display:none">`;
					if (indx > 0) {
						suiteHtml += `<a href="javascript:void(0);" title="Remove" style="color:red" class="delete-suite" data-name="` + suite_name + `" data-suite="` + indx + `">
						<svg class="bi bi-x-circle" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
						  <path fill-rule="evenodd" d="M8 15A7 7 0 108 1a7 7 0 000 14zm0 1A8 8 0 108 0a8 8 0 000 16z" clip-rule="evenodd"/>
						  <path fill-rule="evenodd" d="M11.854 4.146a.5.5 0 010 .708l-7 7a.5.5 0 01-.708-.708l7-7a.5.5 0 01.708 0z" clip-rule="evenodd"/>
						  <path fill-rule="evenodd" d="M4.146 4.146a.5.5 0 000 .708l7 7a.5.5 0 00.708-.708l-7-7a.5.5 0 00-.708 0z" clip-rule="evenodd"/>
						</svg>
					</a>`;
					}

					suiteHtml += `<a href="javascript:void(0);" title="Edit" style="color:black" class="edit-suite" data-name="` + suite_name + `" data-suite="` + indx + `">
						<svg class="bi bi-pencil" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
						  <path fill-rule="evenodd" d="M11.293 1.293a1 1 0 011.414 0l2 2a1 1 0 010 1.414l-9 9a1 1 0 01-.39.242l-3 1a1 1 0 01-1.266-1.265l1-3a1 1 0 01.242-.391l9-9zM12 2l2 2-9 9-3 1 1-3 9-9z" clip-rule="evenodd"/>
						  <path fill-rule="evenodd" d="M12.146 6.354l-2.5-2.5.708-.708 2.5 2.5-.707.708zM3 10v.5a.5.5 0 00.5.5H4v.5a.5.5 0 00.5.5H5v.5a.5.5 0 00.5.5H6v-1.5a.5.5 0 00-.5-.5H5v-.5a.5.5 0 00-.5-.5H3z" clip-rule="evenodd"/>
						</svg>
					</a>
					</span></li>`;
				}
			});

			if (SuiteMainArr.length > 5) {
				suiteHtml += `<li class="pr-3 has-dropdown-menu"> <div class="dropdown">
                  <a class="dropdown-toggle" href="#" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    More<span><img src="assets/images/more-arrow-down.png"> </span></a>
                    <div class="dropdown-menu dropdown-menu-right dropdown-menu-lg-left" aria-labelledby="dropdownMenuLink">`;
				/* For more tab */
				$.each(SuiteMainArr, function (indx, val) {
					if (indx > 4) {
						var suite_name = val.suite_name;
						suiteHtml += `<div class="single-drop"><a data-toggle="tab" class="dropdown-item single-suite-tab" href="javascript:void(0);" data-suite="` + indx + `">` + suite_name + `</a>
						<span class="suite-action" id="suitaction` + indx + `" style="display:none;">
						<a href="javascript:void(0);" title="Remove" style="color:red" class="delete-suite" data-name="` + suite_name + `" data-suite="` + indx + `">
						<svg class="bi bi-x-circle" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
						  <path fill-rule="evenodd" d="M8 15A7 7 0 108 1a7 7 0 000 14zm0 1A8 8 0 108 0a8 8 0 000 16z" clip-rule="evenodd"/>
						  <path fill-rule="evenodd" d="M11.854 4.146a.5.5 0 010 .708l-7 7a.5.5 0 01-.708-.708l7-7a.5.5 0 01.708 0z" clip-rule="evenodd"/>
						  <path fill-rule="evenodd" d="M4.146 4.146a.5.5 0 000 .708l7 7a.5.5 0 00.708-.708l-7-7a.5.5 0 00-.708 0z" clip-rule="evenodd"/>
						</svg>
					</a><a href="javascript:void(0);" title="Edit" style="color:black" class="edit-suite" data-name="` + suite_name + `" data-suite="` + indx + `">
						<svg class="bi bi-pencil" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
						  <path fill-rule="evenodd" d="M11.293 1.293a1 1 0 011.414 0l2 2a1 1 0 010 1.414l-9 9a1 1 0 01-.39.242l-3 1a1 1 0 01-1.266-1.265l1-3a1 1 0 01.242-.391l9-9zM12 2l2 2-9 9-3 1 1-3 9-9z" clip-rule="evenodd"/>
						  <path fill-rule="evenodd" d="M12.146 6.354l-2.5-2.5.708-.708 2.5 2.5-.707.708zM3 10v.5a.5.5 0 00.5.5H4v.5a.5.5 0 00.5.5H5v.5a.5.5 0 00.5.5H6v-1.5a.5.5 0 00-.5-.5H5v-.5a.5.5 0 00-.5-.5H3z" clip-rule="evenodd"/>
						</svg>
					</a></span></div>`;
					}
				});
			}



			$('#header_tab').html(suiteHtml);
		}
	},

	async FetchTestData(test_id, step_no) {
		var result = await browserAppData.storage.local.get(null);
		try {
			var r = await fetch(`${result.meta_data.url}/zsvc/tc/v1/${test_id}/json`);
			var response = await r.json();
			if (response.error){
				$('#test_title').val(response.error);
				console.log("response.error", response.error)
				alert(response.error);
				return Promise.reject("Invalid test-id");
			}
			result.meta_data['testNo'] = test_id;
			result.meta_data['stepNo'] = step_no;
			await browserAppData.storage.local.set({
				meta_data: result.meta_data,
			})
			$('#test_id').val(response.testCaseDetail.id.substring(5));
			$('#test_title').text(response.testCaseDetail.name);
			$("#step_select").empty();
			response.steps.forEach(step => {
				$("#step_select").append(new Option(`Step-${step.sequence} : ${step.name}`, step.sequence));
			});
			console.log("step_no", step_no);
			$(`#step_select option[value="${step_no}"]`).prop('selected', true);
		} catch (e) {
			console.error(e);
			alert(e);
			$('#test_title').val(e);
		}
	},

	LoadActions(CasemainArr, case_index, isReloadHeaderTab, display_type) {
		var html = '';
		// console.log('CasemainArr',CasemainArr);
		// console.log('case_index',case_index);

		if (CasemainArr === undefined || CasemainArr.length === 0) return;

		var singleSuiteDataArr = CasemainArr[0];
		var singleSuiteValue = singleSuiteDataArr.suite_value;

		var sortableCount = 0;
		if (singleSuiteValue.length == 0) {
			$('#case_data_wrap').html(''); //new code 9-6-2020
		}
		var single_value = singleSuiteValue[case_index];
		sortableCount++;
		var case_name = single_value.case_name;
		var case_no = single_value.case_no;
		var case_value = single_value.case_value;

		$.each(case_value, function (single_case_index, single_case_value) {
			sortableCount++;
			var action = single_case_value.action;
			if (single_case_value.action == '') {
				action = '&nbsp';
			}

			/* Change the command */
			if (action == "assertValue") {
				action = "validate text";
			} else if (action == "close") {
				action = "teardown";
			} else if (action == "open") {
				action = "go to link";
			} else if (action == "pause") {
				action = "sleep";
			} else if (action == "select") {
				action = "Select by Visible Text";
			} else if (action == "sendKeys") {
				action = "Keystroke keys";
			} else if (action == "store") {
				action = "save";
			} else if (action == "submit") {
				action = "click(submit)";
			} else if (action == "type") {
				action = "text";
			}


			// if(action == "open"){
			// 	action = "go to";
			// }

			var elm = single_case_value.element;

			if (single_case_value.element == '') {
				elm = '&nbsp';
			}

			var val = single_case_value.value;
			if (single_case_value.value == '') {
				val = '&nbsp';
			}

			if (elm != undefined && elm.length > 30) {
				elm = single_case_value.element.substring(0, 27) + '...';
			}

			var extraClass = "";
			if (single_case_value.is_disable == 1) {
				extraClass = 'disabled-case';
			}

			var childClass = 'child_wrap child_action' + case_index;

			var casedatalist = '';
			if (single_case_value.data_list != undefined && single_case_value.data_list.length > 0) {
				casedatalist = single_case_value.data_list.join('#');
			}

			html += `
			<tr class="sortable-` + sortableCount + ` ` + extraClass + ` ` + childClass + ` case-sub-wrap sub_tr_index_` + (single_case_index + 1) + ` ui-state-default" data-caseindex="` + (single_case_index + 1) + `" data-mainindex="` + (single_case_index) + `" data-stepindex="` + case_index + `" data-sortposition="` + sortableCount + `" data-caselist="` + encodeURI(casedatalist) + `">
				<td class="col-1"><img id="more_button" src="assets/images/more.png">
				<img src="assets/images/small_logo.png">
				` + (single_case_index + 1) + `
				</td>
				<td class="col-3 font_black has-input" data-case_commend="action">
				<span class="case_value_lable">` + action + `</span>
				<input list="actionlist` + single_case_index + `" type="text" class="inpt display_hide case-input supported-command-auto" name="" placeholder="Action" value="` + action + `">
				<a class="down-arrow display_hide" href="javascript:void(0);" id="downArrow` + single_case_index + `">
					<svg class="bi bi-chevron-down" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
						<path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 01.708 0L8 10.293l5.646-5.647a.5.5 0 01.708.708l-6 6a.5.5 0 01-.708 0l-6-6a.5.5 0 010-.708z" clip-rule="evenodd"/>
					</svg>
				</a>
				</td>
				<td class="col-4 has-input" data-case_commend="element">
				<span class="case_value_lable  gray-font">` + elm + `</span>
				<input type="text" style="padding-right:25px" class="inpt display_hide case-input single-case-data-list" name="" placeholder="Element" value='` + single_case_value.element + `'>
				<a class="down-arrow-element display_hide" href="javascript:void(0);" id="downArrowElement` + single_case_index + `">
					<svg class="bi bi-chevron-down" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
						<path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 01.708 0L8 10.293l5.646-5.647a.5.5 0 01.708.708l-6 6a.5.5 0 01-.708 0l-6-6a.5.5 0 010-.708z" clip-rule="evenodd"/>
					</svg>
				</a>
				</td>
				<td class="col-4 has-input" data-case_commend="value">
				<span class="case_value_lable gray-font">` + val + `</span>
				<input type="text" class="inpt display_hide case-input" name="" placeholder="Value" value='` + single_case_value.value + `'>
				</td>
			</tr>`;
		})
		$('#case_data_wrap').html(html);
		$('#active_action_icon').show();

		CustomFunction.LoadTheRecordDataHtml();
		if (isReloadHeaderTab == true) {
			CustomFunction.LoadCaseSuiteHtml(CasemainArr);
		}

		var supportedComm = supportedAllCommand();

		/* Action autocomplete as a dropdown */
		$(".supported-command-auto").autocomplete({
			source: supportedComm,
			minLength: 0,
		}).focus(function () {
			$(this).autocomplete({
				disabled: false
			});
			$(this).autocomplete('search', "")
			$(this).autocomplete("widget").css({
				"width": (250 + "px"),
			}).hide();
		}).keyup(function (e) {
			$(this).autocomplete({
				disabled: true
			});
		})

		$(document).on('click', '.down-arrow', function (e) {
			e.stopImmediatePropagation();
			$(this).siblings('.supported-command-auto').autocomplete({
				disabled: false
			});
			if ($(this).siblings('.supported-command-auto').autocomplete("widget").is(":visible") || CustomFunction.isPreFocus == true) {
				$(this).siblings('.supported-command-auto').autocomplete("widget").hide();
				CustomFunction.isPreFocus = false;
			} else {
				if (!$(this).siblings('.supported-command-auto').is(":focus")) {
					$(this).siblings('.supported-command-auto').focus().autocomplete("widget").show();
					CustomFunction.isPreFocus = true;
				} else {
					$(this).siblings('.supported-command-auto').autocomplete("widget").show();
					CustomFunction.isPreFocus = true;
				}
			}
		});

		/* Action autocomplete as a dropdown end */


		/* Element autocomplete as a dropdown */
		$('.single-case-data-list').autocomplete({
			source: [],
			minLength: 0,
		}).focus(function () {
			$(this).autocomplete({
				disabled: false
			});
			var list = $(this).parent('td').parent('tr').data('caselist');
			if (list != undefined && list != '') {
				var decodedlist = decodeURI(list);
				var res = decodedlist.split("#");
				//res.push($(this).val());
				$(this).autocomplete('option', {
					source: res
				});
			} else {
				$(this).autocomplete('option', {
					source: res
				});
			}
			$(this).autocomplete('search', "");
			$(this).autocomplete("widget").css({
				"width": (330 + "px")
			}).hide();
		}).keyup(function (e) {
			$(this).autocomplete({
				disabled: true
			});
		});
		// /down-arrow-element
		$(document).on('click', '.down-arrow-element', function (e) {
			e.stopImmediatePropagation();
			$(this).siblings('.single-case-data-list').autocomplete({
				disabled: false
			});
			if ($(this).siblings('.single-case-data-list').autocomplete("widget").is(":visible") || CustomFunction.isPreFocusElement == true) {
				$(this).siblings('.single-case-data-list').autocomplete("widget").hide();
				CustomFunction.isPreFocusElement = false;
			} else {
				if (!$(this).siblings('.single-case-data-list').is(":focus")) {
					$(this).siblings('.single-case-data-list').focus().autocomplete("widget").show();
					CustomFunction.isPreFocusElement = true;
				} else {
					$(this).siblings('.single-case-data-list').autocomplete("widget").show();
					CustomFunction.isPreFocusElement = true;
				}
			}
		});



		$.extend($.ui.autocomplete.prototype.options, {
			open: function (event, ui) {
				$(this).autocomplete("widget").css({
					"width": ($(this).width() + "px")
				});
			}
		});
	},
	
	PostProcess(actions){
		let new_actions = []
		for(let i = 0; i < actions.length; i++){
			action = actions[i];
			if([null, undefined].includes(action)) continue;
			if(
				action.action == 'click' && 
				i < actions.length - 1 && 
				['click', 'text', 'double click'].includes(actions[i+1].action)  &&
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
					CustomFunction.FetchChromeCaseData()
					.then( () => {
						console.log("CustomFunction.caseDataArr >>>",CustomFunction.caseDataArr);
						console.log("result.recorded_actions >>>",result.recorded_actions);
						result.recorded_actions = result.recorded_actions.filter(element => ![null, undefined].includes(element));
						// If the step is not totally blank we dont add 'go to link' action
						if(CustomFunction.caseDataArr[0].suite_value[0].case_value.length > 0 && result.recorded_actions.length > 0 && result.recorded_actions[0].action == 'go to link') 
							result.recorded_actions.shift();
						recorded_actions = CustomFunction.PostProcess(result.recorded_actions);
						CustomFunction.caseDataArr[0].suite_value[0].case_value = CustomFunction.caseDataArr[0].suite_value[0].case_value.concat(recorded_actions)
	
						// Save old actions + new actions in caseDataArr and display
						browser.storage.local.set({
							case_data: CustomFunction.caseDataArr,
						})

						// Wipe out recorded_actions
						.then(CustomFunction.DisplayCaseData);
						browserAppData.storage.local.set({
							recorded_actions: [],
						})
					});
					
				} catch (e) {
					console.error(e);
				}
			})
		}, 500)
		

		// setTimeout(function () {
		// 	/* auto assign the case if there is no already case exists */
		// 	var mainArrLength = Object.keys(CasemainArr).length;
		// 	if (CasemainArr == undefined || mainArrLength == 0) {
		// 		var tempObj = {
		// 			case_name: "Enter Step Name",
		// 			case_value: [],
		// 		};
		// 		var objArr = [];
		// 		objArr.push(tempObj);
		// 		CasemainArr.suite_name = "Untitled";
		// 		CasemainArr.suite_value = objArr;

		// 		var mainTestSuidData = [];

		// 		/* initial time untitled test suit position is zero */
		// 		mainTestSuidData.push(CasemainArr);
		// 		CasemainArr = mainTestSuidData;
		// 	} else {
		// 		/* fetch selected case */
		// 		var selectedCase = -1;
		// 		var defaultCaseName = 'Enter Step Name';
		// 		$('.case-main-wrap').each(function () {
		// 			if ($(this).hasClass('selected-case')) {
		// 				selectedCase = $(this).data('mainindex');
		// 				defaultCaseName = $(this).children('.has-input').children('.case-input').val();
		// 			}
		// 		});

		// 		if (selectedCase == -1) {
		// 			var selected_suite = -1;
		// 			$('.single-suite-tab').each(function () {
		// 				if ($(this).hasClass('current_selected_tab')) {
		// 					selected_suite = $(this).data('suite');
		// 				}
		// 			});
		// 			if (selected_suite != -1) {
		// 				var currentCaseVal = CasemainArr.suite_value[0].case_value;
		// 				var tempObj = {
		// 					case_name: "Enter Step Name",
		// 					case_value: currentCaseVal,
		// 				};
		// 				var objArr = [];
		// 				objArr.push(tempObj);
		// 				console.log(objArr);
		// 				var SavedCaseData = CustomFunction.caseDataArr;
		// 				SavedCaseData[selected_suite].suite_value = objArr;
		// 				CasemainArr = SavedCaseData;
		// 			}

		// 		} else {

		// 			//if(selectedCase > -1){

		// 			/* Fetch selected suite */
		// 			var selected_suite = -1;
		// 			$('.single-suite-tab').each(function () {
		// 				if ($(this).hasClass('current_selected_tab')) {
		// 					selected_suite = $(this).data('suite');
		// 				}
		// 			});

		// 			if (selected_suite != -1) {
		// 				var currentCaseVal = CasemainArr.suite_value[0].case_value;
		// 				var SavedCaseData = CustomFunction.caseDataArr;

		// 				SavedCaseData[selected_suite].suite_value[selectedCase].case_value = currentCaseVal;

		// 				CasemainArr = SavedCaseData;
		// 			}

		// 		}
		// 	}

		// 	console.log('CasemainArr', CasemainArr);

		// 	if (CasemainArr != undefined) {
		// 		var case_data = {
		// 			case_data: CasemainArr,
		// 		};
		// 		browser.storage.local.set(case_data);
		// 		//CustomFunction.DisplayCaseData(true);
		// 		CustomFunction.DisplayCaseData('save_record_data', false);
		// 	}
		// }, 1000);
	},

	UpdateCaseData(textValue, case_command, case_index, update_step_or_action, stepindex) {
		/* fetch Pre save data */
		CustomFunction.FetchChromeCaseData()
		.then(() => {
			/* Fetch selected suite */
			var selected_suite = -1;
			$('.single-suite-tab').each(function () {
				if ($(this).hasClass('current_selected_tab')) {
					selected_suite = $(this).data('suite');
				}
			});	
			if (selected_suite != -1) {
				var SavedCaseData = CustomFunction.caseDataArr;
				if (update_step_or_action == 'update_action') {

					// if(case_command == 'action' && textValue == "go to"){
					// 	textValue = "open";
					// }

					if (case_command == 'action') {

						if (textValue == "validate text") {
							textValue = "assertValue";
						} else if (textValue == "teardown") {
							textValue = "close";
						} else if (textValue == "go to link") {
							textValue = "open";
						} else if (textValue == "sleep") {
							textValue = "pause";
						} else if (textValue == "Select by Visible Text") {
							textValue = "select";
						} else if (textValue == "Keystroke keys") {
							textValue = "sendKeys";
						} else if (textValue == "save") {
							textValue = "store";
						} else if (textValue == "click(submit)") {
							textValue = "submit";
						} else if (textValue == "text") {
							textValue = "type";
						}
					}

					SavedCaseData[selected_suite].suite_value[stepindex].case_value[case_index][case_command] = textValue;
				} else {
					//SavedCaseData[selected_suite].suite_value[case_index].case_name = textValue
					SavedCaseData[selected_suite].suite_value[case_index][case_command] = textValue
				}

				var case_data = {
					case_data: SavedCaseData,
				};

				browser.storage.local.set(case_data);
				/* Update the recorder html */
				CustomFunction.LoadTheRecordDataHtml();
			}
		});
	},

	DisplayCaseData(display_type, is_reload_header_tab, selectedTabIndx) {
		//console.log('display_type',display_type);
		CustomFunction.FetchChromeCaseData().then(() => {
			console.log('CustomFunction.caseDataArr',CustomFunction.caseDataArr);
			CustomFunction.LoadActions(CustomFunction.caseDataArr, 0, is_reload_header_tab, display_type);
			/* when add setp the suite is not auto matic click */
			//if(display_type != 'add_case_step' && display_type != "add_action"){
			setTimeout(function () {
				if (selectedTabIndx != undefined) {
					$('.suite-tab-' + selectedTabIndx).trigger('click');
				} else {
					$('.current_selected_tab').trigger('click');
				}
			}, 550);
			//}

			if (display_type == "save_record_data") {
				var sortposition = $('.selected-case').data('sortposition');
				setTimeout(function () {
					console.log('sortposition', sortposition);
					$('.sortable-' + sortposition).trigger('click');
				}, 800);
			}					
		});
		
	},

	async FetchChromeCaseData() {
		CustomFunction.caseDataArr = {};
		result = await browserAppData.storage.local.get(null);
		try {
			if (result.case_data) {
				CustomFunction.caseDataArr = result.case_data;
			} else {
				/* Create a new record initial time */
				var tempObj = {
					case_name: "Enter Step Name",
					case_value: [],
				};
				var objArr = [];
				objArr.push(tempObj);
				var tempMainArr = {
					suite_name: "Untitled",
					suite_value: objArr,
				}

				var mainTestSuidData = [];

				/* initial time untitled test suit position is zero */
				mainTestSuidData.push(tempMainArr);

				CustomFunction.caseDataArr = mainTestSuidData;

				/* save on local storage */
				var case_data = {
					case_data: mainTestSuidData,
				};
				browser.storage.local.set(case_data);
			}
		} catch (e) {
			console.log(e);
		}
		
	},

	LoadAccordion: function () {
		var acc = document.getElementsByClassName("accordion");
		var i;

		for (i = 0; i < acc.length; i++) {
			acc[i].addEventListener("click", function () {
				this.classList.toggle("active");
				var panel = this.nextElementSibling;
				if (panel.style.maxHeight) {
					panel.style.maxHeight = null;
				} else {
					panel.style.maxHeight = panel.scrollHeight + "px";
				}
			});
		}
	},

	UserAuthAjaxCall(server_url, username, password, server_port, callType) {
		if (callType == "setting_page") {
			$('#auth_loading').show();
		}
		/* Api calling to authenticate the user */
		var form = new FormData();
		form.append("username", username);
		form.append("password", password);
		var settings = {
			"async": true,
			"crossDomain": true,
			//"url": "https://qa.zeuz.ai/api/auth/token/generate",
			"url": server_url + "/api/auth/token/generate",
			"method": "POST",
			"headers": {
				"cache-control": "no-cache",
			},
			"processData": false,
			"contentType": false,
			"mimeType": "multipart/form-data",
			"data": form
		}

		$.ajax(settings).done(function (response) {
			$('#auth_loading').hide();
			var succobj = JSON.parse(response);
			if (succobj.access_token != undefined && succobj.access_token != '') {

				var accessToken = succobj.access_token;
				var recorder_settings = {
					"async": true,
					"crossDomain": true,
					"url": server_url + "/api/recorder/",
					"method": "POST",
					"headers": {
						"content-type": "application/json",
						"authorization": "Bearer " + accessToken,
						"cache-control": "no-cache",
						"postman-token": "0d962438-f69b-3319-20de-a026197f55e3"
					}
				}

				$.ajax(recorder_settings).done(function (response) {
					$('#export_wrap').show();
				}).fail(function (xhr, err) {
					$('#export_wrap').hide();
				})


				var data = {
					"server_url": server_url,
					"username": username,
					"password": password,
					"server_port": server_port,
				};

				var textString = JSON.stringify(data);
				var words = CryptoJS.enc.Utf8.parse(textString); // WordArray object
				var base64 = CryptoJS.enc.Base64.stringify(words);

				var base64_data = {
					auth_data: base64,
				};
				browser.storage.local.set(base64_data);
				CustomFunction.is_auth_user = true;

				var serverhtml = `<a target="_blank" href="` + server_url + `" style="background: transparent;border-bottom: 1px solid transparent;padding-top:0px;">
                <img class="normal-image" style="width: 100px; margin-left:20px" src="assets/images/leftIcon/server-new.png">
                <img class="hover-image" style="width: 100px; margin-left:20px" src="assets/images/leftIcon/server-new.png">
                <span>` + server_url + `</>
              </a>`;
				$('#servericon').html(serverhtml);

				var exportBtnHtml = `<div class="pl-0 sidebar_menu" id="export_case">
                <img class="normal-image" src="assets/images/icons/export.png">
                <img class="hover-image" src="assets/images/icons/export-on.png">
              </div>`;
				$('#export_wrap').html(exportBtnHtml);

				if (callType == "setting_page") {
					$('.err-wrap').html('').hide();
					$('.succ-wrap').show().html('<p>Your username and API token has been registered. Feel free to export your test case to your ZeuZ server</p>');
					setTimeout(function () {
						$('.succ-wrap,.err-wrap').hide();
					}, 5000);
				} else {
					$('#server_url').val(server_url);
					$('#username').val(username);
					$('#password').val(password);
					$('#server_port').val(server_port);
				}
			}
		}).fail(function (jqXHR, textStatus, errorThrown) {
			CustomFunction.is_auth_user = false;
			if (callType == "setting_page") {
				if (jqXHR.responseText != undefined) {
					try {
						var errobj = JSON.parse(jqXHR.responseText);
						$('.succ-wrap').html('').hide();
						$('.err-wrap').show().html('<p>' + errobj.message + '</p>');
						$('#auth_loading').hide();
						setTimeout(function () {
							$('.succ-wrap,.err-wrap').hide();
						}, 5000);

						var base64_data = {
							auth_data: '',
						};
						browser.storage.local.set(base64_data);
						CustomFunction.is_auth_user = false;
						$('#servericon').html('');
						$('#export_wrap').html('');
					} catch (e) {

						var base64_data = {
							auth_data: '',
						};
						browser.storage.local.set(base64_data);
						CustomFunction.is_auth_user = false;
						$('#servericon').html('');
						$('#export_wrap').html('');

						$('.succ-wrap').html('').hide();
						$('.err-wrap').show().html('<p> Please try again! You might need to regenerate your API token or contact ZeuZ if you feel something is wrong. </p>');
						$('#auth_loading').hide();
						setTimeout(function () {
							$('.succ-wrap,.err-wrap').hide();
						}, 5000);
					}
				} else {

					var base64_data = {
						auth_data: '',
					};
					browser.storage.local.set(base64_data);
					CustomFunction.is_auth_user = false;
					$('#servericon').html('');
					$('#export_wrap').html('');

					$('.succ-wrap').html('').hide();
					$('.err-wrap').show().html('<p> Please try again! You might need to regenerate your API token or contact ZeuZ if you feel something is wrong. </p>');
					$('#auth_loading').hide();
					setTimeout(function () {
						$('.succ-wrap,.err-wrap').hide();
					}, 5000);
				}
			}
		});
	},

	LoadEvent: function () {
		CustomFunction.LoadAccordion();
		CustomFunction.DisplayCaseData('initial_load', true);

		/* Close the main page content */
		function show_content_section () {
			var section = "content";
			var i, tabcontent, tablinks;
			tabcontent = document.getElementsByClassName("tabcontent");
			for (i = 0; i < tabcontent.length; i++) {
				tabcontent[i].style.display = "none";
			}
			tablinks = document.getElementsByClassName("tablink");
			for (i = 0; i < tablinks.length; i++) {
				tablinks[i].style.backgroundColor = "";
			}
			document.getElementById(section).style.display = "block";
		}
		$(document).on('click', '.close_main_page', show_content_section);

		$(document).on('click', '#test_case', show_content_section)

		/* user authentication */
		$(document).on('click', '#authenticate', function () {
			CustomFunction.UserAuthentication();
		})

		/* Click case or action */
		$(document).on('click', '.case-sub-wrap', function (e) {

			var shiftHeld = e.shiftKey;


			//var is_class_deactive = '';
			var is_class_deactive = false;
			//if ($('.case-sub-wrap').hasClass('disabled-case')) {
			/*if ($(this).hasClass('disabled-case')) {
				is_class_deactive = true;
			}else {
				is_class_deactive = false;
			}*/

			if (is_class_deactive != true) {
				if (!$(this).hasClass('show_text_box')) {
					if (shiftHeld == true) {
						if ($(this).hasClass('case-main-wrap')) {
							$('.case-sub-wrap').removeClass('selected-case');
						}
						/* using shift key user only selected either action or step.*/
						$('.case-main-wrap').removeClass('selected-case');
						$(this).addClass('selected-case');
					} else {
						$('.case-sub-wrap').removeClass('selected-case');
						$(this).addClass('selected-case');
					}
					$('.case-sub-wrap').removeClass('show_text_box');
					$('.case-input').addClass('display_hide');
					$('.down-arrow').addClass('display_hide');
					$('.down-arrow-element').addClass('display_hide');
					$('.case_value_lable').removeClass('display_hide');

					//$('#inactive_action_icon').attr('style','display:none !important');
					$('#active_action_icon').show();

					$('.case-input').removeClass('input-focus');
				}


				/*if(shiftHeld == true){
					window.getSelection().empty(); // Remove the default text select when press shift and click

					/* Working with shift key */
				/*var first_selected_case_index = $('.selected-case').data('caseindex');
					var current_selected_case_index = $(this).data('caseindex');

					var min = first_selected_case_index;
					var max = current_selected_case_index;

					if(first_selected_case_index < current_selected_case_index){
						min = first_selected_case_index;
						max = current_selected_case_index;
					}else{
						min = current_selected_case_index;
						max = first_selected_case_index;
					}

					$('.case-sub-wrap').removeClass('selected-case');

					for(var i = min; i <= max; i++){
						$('.sub_tr_index_'+i).addClass('selected-case');
					}
				}else{

					/* Working without shift key */
				/*if(!$(this).hasClass('show_text_box')){

						$('.case-sub-wrap').removeClass('selected-case');
						$(this).addClass('selected-case');
						$('.case-sub-wrap').removeClass('show_text_box');
						$('.case-input').addClass('display_hide');
						$('.case_value_lable').removeClass('display_hide');

						$('#inactive_action_icon').attr('style','display:none !important');
						$('#active_action_icon').show();

						$('.case-input').removeClass('input-focus');
					}
				}*/

			}


			if ($(this).hasClass('case-main-wrap')) {
				CustomFunction.LoadTheRecordDataHtml();
			} else {

				/* Play not working when user click on action */
				var caseHtml = `<input id="records-count" value="0" type="hidden">`;
				$('#records-grid').html(caseHtml);
			}
		})


		/* Update Case */
		$(document).on('blur', '.case-input', function () {
			var textValue = $(this).val();
			var spanTxt = textValue;
			if (spanTxt == "") {
				spanTxt = "&nbsp;"
			}

			if (spanTxt != undefined && spanTxt.length > 30) {
				spanTxt = spanTxt.substring(0, 27) + '...';
			}

			$(this).siblings('.case_value_lable').html(spanTxt);
			var case_command = $(this).parent('td').data('case_commend');
			var case_index = $(this).parent('td').parent('tr').data('mainindex');
			var stepindex = $(this).parent('td').parent('tr').data('stepindex');

			/* Check edit step name or action */
			if ($(this).parent('td').parent('tr').hasClass('case-main-wrap')) {
				CustomFunction.UpdateCaseData(textValue, case_command, case_index, 'update_step');
			} else {
				CustomFunction.UpdateCaseData(textValue, case_command, case_index, 'update_action', stepindex);
			}
		})

		/* when out side click then hide the edit text box */
		$(document).mouseup(function (e) {
			var container = $(".case-sub-wrap");
			if (!container.is(e.target) && container.has(e.target).length === 0) {
				$('.case-sub-wrap').removeClass('show_text_box');
				$('.case-input').addClass('display_hide');
				$('.down-arrow').addClass('display_hide');
				$('.down-arrow-element').addClass('display_hide');
				$('.case_value_lable').removeClass('display_hide');
				CustomFunction.isPreFocus = false;
				CustomFunction.isPreFocusElement = false;
			}
		})

		/* Edit Case */
		$(document).on('click', '#edit_case', function () {
			$('.selected-case').each(function () {
				if (!$(this).hasClass('disabled-case')) {
					$(this).children('td').children('.case-input').removeClass('display_hide');
					$(this).children('td').children('.down-arrow').removeClass('display_hide');
					$(this).children('td').children('.down-arrow-element').removeClass('display_hide');
					$(this).children('td').children('.case_value_lable').addClass('display_hide');
					$(this).addClass('show_text_box');
				}
			})
		});

		/* add  class when click on the text box */
		$(document).on('click', '.case-input', function () {
			$('.case-input').removeClass('input-focus');
			$(this).addClass('input-focus');
		});

		/* Delete case and suit */
		$(document).on('click', '#case_delete', function (event) {
			event.preventDefault();
			var r = confirm("Are you sure? you want to delete!");

			if (r == true) {
				var selected_suite = -1;
				$('.single-suite-tab').each(function () {
					if ($(this).hasClass('current_selected_tab')) {
						selected_suite = $(this).data('suite');
					}
				});

				if (selected_suite != -1) {
					var selectedCase = $('.selected-case').data('mainindex');
					var selectedStep = $('.selected-case').data('stepindex');

					if (selectedStep == undefined) {
						/* Remove the step */
						$('.case-main-wrap').each(function () {
							if ($(this).hasClass('selected-case')) {
								selectedStep = $(this).data('mainindex');
							}
						});

						/* After delete creat a new array */
						var afterDeleteArr = [];
						$.each(CustomFunction.caseDataArr[selected_suite].suite_value, function (indx, val) {
							if (indx != selectedStep) {
								afterDeleteArr.push(val);
							}
						});

						console.log('afterDeleteArr', afterDeleteArr);

						/* push the new array to the suit value */
						//if(afterDeleteArr.length > 0){ //new code 9-6-2020
						/* the 1st step can not be delete */
						CustomFunction.caseDataArr[selected_suite].suite_value = afterDeleteArr;
						//}
						var case_data = {
							case_data: CustomFunction.caseDataArr,
						};

					} else {
						var currentDataArr = CustomFunction.caseDataArr;
						/* Remove the action */
						var newArr = [];
						var temp = 0;
						$('.selected-case').each(function () {
							selectedCase = $(this).data('mainindex'); //action
							selectedStep = $(this).data('stepindex');

							selectedCase = selectedCase - temp;
							CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.splice(selectedCase, 1);
							//console.log('CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value',CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value);
							temp++;
						})
						var case_data = {
							case_data: CustomFunction.caseDataArr,
						};
					}

					//console.log('case_data',case_data);

					browser.storage.local.set(case_data);
					CustomFunction.DisplayCaseData('delete_case', false);
				}
			}
		});

		/* Sudipto Start*/
		/* *===* Draggable & Droppable start *===* */
		$(function () {
			$("#case_data_wrap").sortable({
				// stop: function( event, ui ) {
				start: function (event, ui) {

				},
				stop: function (event, ui) {

				},

				update: function (event, ui) {

					/* Fetch selected suite */
					var selected_suite = -1;
					$('.single-suite-tab').each(function () {
						if ($(this).hasClass('current_selected_tab')) {
							selected_suite = $(this).data('suite');
						}
					});

					if (selected_suite != -1) {
						var mainindex = ui.item.data("mainindex");
						var caseindex = ui.item.data("caseindex");

						var sortposition = ui.item.data("sortposition");
						var drop_position = ui.item.index();
						drop_position = drop_position + 1;
						var arrPosition = mainindex - 1;

						var sort_condition = false;
						if ($('.sortable-' + sortposition).hasClass('parent_wrap') && $('.sortable-' + drop_position).hasClass('parent_wrap')) {
							sort_condition = true;
						} else if ($('.sortable-' + sortposition).hasClass('child_wrap') && ($('.sortable-' + drop_position).hasClass('child_wrap') || $('.sortable-' + drop_position).hasClass('parent_wrap'))) {
							sort_condition = true;
						}


						if (sort_condition == true) {
							var stepIndex = ui.item.data("stepindex"); /* Current element step index */
							if (stepIndex == undefined) {
								/* Update the step position */
								/* swap the data */
								var tempHold = CustomFunction.caseDataArr[selected_suite].suite_value[mainindex];
								var dropMainIndex = $('.sortable-' + drop_position).data('mainindex');
								CustomFunction.caseDataArr[selected_suite].suite_value[mainindex] = CustomFunction.caseDataArr[selected_suite].suite_value[dropMainIndex];
								CustomFunction.caseDataArr[selected_suite].suite_value[dropMainIndex] = tempHold;

								var case_data = {
									case_data: CustomFunction.caseDataArr,
								};
								browser.storage.local.set(case_data);
								CustomFunction.DisplayCaseData(false);
							} else {
								/* Update the action */
								var dropMainIndex = $('.sortable-' + drop_position).data('mainindex');
								var nextPos = dropMainIndex;
								if ($('.sortable-' + drop_position).hasClass('case-main-wrap')) {
									var dropStepIndex = dropMainIndex;
								} else {
									var dropStepIndex = $('.sortable-' + drop_position).data('stepindex');
								}
								var is_same_step = true;
								if ($('.sortable-' + drop_position).hasClass('case-main-wrap')) {
									is_same_step = false;
								}
								if (stepIndex != dropStepIndex || is_same_step == false) {
									var val = CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value[mainindex];
									if (is_same_step == false) {
										if (sortposition > drop_position) {
											CustomFunction.caseDataArr[selected_suite].suite_value[(dropStepIndex - 1)].case_value.push(val);
										} else {
											CustomFunction.caseDataArr[selected_suite].suite_value[dropStepIndex].case_value.splice(0, 0, val);
										}
									} else {
										if (sortposition > drop_position) {
											CustomFunction.caseDataArr[selected_suite].suite_value[dropStepIndex].case_value.splice(nextPos, 0, val);
										} else {
											CustomFunction.caseDataArr[selected_suite].suite_value[dropStepIndex].case_value.splice((nextPos + 1), 0, val);
										}
									}
									CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value.splice((mainindex), 1);
								} else {

									/* exq this section when drop in under same step */
									if (nextPos < mainindex) {
										/* move to up */
										var val = CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value[mainindex];
										CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value.splice(nextPos, 0, val);
										CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value.splice((mainindex + 1), 1);
									} else {
										/* Move to down */
										var val = CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value[mainindex];
										CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value.splice((mainindex), 1);
										CustomFunction.caseDataArr[selected_suite].suite_value[stepIndex].case_value.splice(nextPos, 0, val);
									}
								}

								var case_data = {
									case_data: CustomFunction.caseDataArr,
								};
								browser.storage.local.set(case_data);
								CustomFunction.DisplayCaseData(false);
							}

						} else {
							$("#case_data_wrap").sortable("cancel");
							console.log('not update');
						}
					}
				}
			});
			$("#case_data_wrap").disableSelection();
		});

	},

	FetchActions: async function () {
		result = await browser.storage.local.get('meta_data');
		meta_data = result.meta_data
		console.log("metdata =====",result);
		resp = await $.ajax({
			type: "GET",
			url: `${meta_data.url}/ai_recorder_init`,
			headers: {
				// "Content-Type": "application/json",
				"X-Api-Key": `${meta_data.apiKey}`,
			},
			data: {"test_id":`${meta_data.testNo}`, "step_seq":`${meta_data.stepNo}`},
		});
		console.log("resp =====",resp);
		$('#test_label').text(meta_data.testNo);
		case_data = [
			{
				"suite_name": meta_data.testName.substring(0,50),
				"suite_value": [
					{	
						"case_name": resp.step.name,
						"case_no": meta_data.stepNo,
						"case_value": resp.step.actions.map(action => {
							return {
								"action": action.short.action,
								"element": action.short.element,
								"value": action.short.value,
								"is_disable": action.is_disable,
								"name": action.name,
								"data_list": [
									action.short.value
								],
								"main": action.main,
							}
						}),

					}
				] 	
			}	
		]
		console.log(case_data);
		browser.storage.local.set({
			case_data: case_data
		})
		.then(CustomFunction.LoadEvent);
	}
}

jQuery(document).ready(async function () {
	result = await browser.storage.local.get('meta_data');
	meta_data = result.meta_data;
	CustomFunction.FetchTestData(meta_data.testNo, meta_data.stepNo);
	CustomFunction.FetchActions();

	$('#server_address').val(result.meta_data.url);
	$('#api_key').val(result.meta_data.apiKey);

	$(document).on('click', '#fetch', async function () {
		try{
			$('#fetch').text('Fetching...');
			$("#fetch").attr('disabled', true).css('opacity',0.5);
	
			if (!(4,5).includes($('#test_id').val().length)){
				alert('Provide 4 digit test-id. Ex: TEST-1234');
				$('#fetch').text('Error!!');
				$("#fetch").attr('disabled', true).css('opacity',0.5);
				setTimeout(()=>{
					$('#fetch').text('Fetch');
					$("#fetch").removeAttr('disabled').css('opacity',1);
				},1500)
				return;
			}
			await CustomFunction.FetchTestData(`TEST-${$('#test_id').val()}`, 1);
			CustomFunction.FetchActions();
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
		console.log(this.value);
		var result = await browserAppData.storage.local.get(null);
		result.meta_data['stepNo'] = this.value;
		await browserAppData.storage.local.set({
			meta_data: result.meta_data,
		})
		CustomFunction.FetchActions();
	})

	$(document).on('click', '#record', function () {
		// $('#record_wrap').hide();
		// $('#stop_wrap').show();
		let icon = $('#record_icon');
		let label = $('#record_label');

		label[0].textContent = label[0].textContent.trim() == 'Record' ? 'Stop' : 'Record';
		icon.text(icon[0].textContent.trim() == 'camera' ? 'stop' : 'camera');
	})	
	/* Save all newlly recorded actions with old actions and auto naming */
	$(document).on('click', '#save_button', async function () {
		$('#save_label').text('Saving...');
		$("#save_button").attr('disabled', true).css('opacity',0.5);
		await CustomFunction.FetchChromeCaseData()
		var result = await browserAppData.storage.local.get(["meta_data"]);
		var save_data = {
			TC_Id: result.meta_data.testNo,
			step_sequence: result.meta_data.stepNo,
			step_data: JSON.stringify(CustomFunction.caseDataArr[0].suite_value[0].case_value.map(action => {
				return action.main;
			})),
			dataset_name: JSON.stringify(CustomFunction.caseDataArr[0].suite_value[0].case_value.map((action, idx) => {
				return [
					action.name,
					idx+1,
					!action.is_disable,
				]
			}))
		}
		console.log("save_data >>>", save_data);
		$.ajax({
			url: result.meta_data.url + '/Home/nothing/update_specific_test_case_step_data_onlyx/',
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
				console.log(errorThrown);
				$('#save_label').text('Error!!');
				setTimeout(()=>{
					$('#save_label').text('Save');
					$("#save_button").removeAttr('disabled').css('opacity',1);
				}, 1500)
			}
		})
	});
	
	$(document).on('click', '#authenticate', async function () {
		$('#authenticate').text('Authenticaing...');
		$("#authenticate").attr('disabled', true).css('opacity',0.5);
		await CustomFunction.FetchChromeCaseData()
		var result = await browserAppData.storage.local.get(["meta_data"]);
		var server_address = $('#server_address').val();
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
				console.log(errorThrown);
				$('#authenticate').text('Error!!');
				setTimeout(()=>$('#authenticate').text('Authenticate'),1500)
			}
		})
	});

	$(document).on('click', '#run_button', async function () {
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
		dependency = {"Browser": browser,"Mobile":"Android"}
		const run_data = {
			"test_case_list": JSON.stringify([result.meta_data.testNo]),
			"dependency_list": JSON.stringify(dependency),
			"all_machine": JSON.stringify([machine]),
			"debug": 'yes',
			"debug_clean": "yes",
			"debug_steps": JSON.stringify([result.meta_data.stepNo.toString()]),
			"RunTestQuery": JSON.stringify([result.meta_data.testNo, machine]),
			"dataAttr": JSON.stringify(["Test Case"]),
			"project_id": project_id,
			"team_id": team_id,
			"user_id": user_id,
		}
		console.log("run_data", run_data)
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
					$('#run_label').text('Run');
					$("#run_button").removeAttr('disabled').css('opacity',1);
				},1500)
			},
			error: function(jqXHR, textStatus, errorThrown) {
				console.log(errorThrown);
				$('#run_label').text('Error!!');
				setTimeout(()=>{
					$('#run_label').text('Run');
					$("#run_button").removeAttr('disabled').css('opacity',1);
				},1500)
			}
		})
	})

	/* tab select */
	$(document).on('click', '.opensection', function () {
		var THIS = $(this);
		var section = THIS.data('section');

		var i, tabcontent, tablinks;

		tabcontent = document.getElementsByClassName("tabcontent");

		for (i = 0; i < tabcontent.length; i++) {
			tabcontent[i].style.display = "none";
		}
		tablinks = document.getElementsByClassName("tablink");

		for (i = 0; i < tablinks.length; i++) {
			tablinks[i].style.backgroundColor = "";
		}
		document.getElementById(section).style.display = "block";
	})
	
	/* *===* Dselect All by click esc start *===* */
	$(document).on('keydown', function (event) {
		if (event.key == "Escape") {
			$(".case-sub-wrap").removeClass("selected-case");
			$('.current_selected_tab').trigger('click');
		}
	});
	/* function of main.js */
	var fullHeight = function () {
		$('.js-fullheight').css('height', $(window).height());
		$(window).resize(function () {
			$('.js-fullheight').css('height', $(window).height());
		});
	};
	fullHeight();

	$('#sidebarCollapse').on('click', function () {
		$('#sidebar').toggleClass('active');
	});

	/* off the page inspect */
	//    $(document).bind("contextmenu",function(e) {
	//  e.preventDefault();
	// });
	// $(document).keydown(function(e){
	//     if(e.which === 123){
	//        return false;
	//     }
	// });
})