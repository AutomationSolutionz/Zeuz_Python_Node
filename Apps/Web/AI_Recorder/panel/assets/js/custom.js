var CustomFunction = {
	caseDataArr: {},
	StepCopyData: null,
	copyType: null,
	is_auth_user: false,
	isPreFocus: false,
	isPreFocusElement: false,
	/* Hidden field*/
	LoadTheRecordDataHtml(recordData) {
		CustomFunction.FetchChromeCaseData();

		setTimeout(function () {
			/* Fetch selected suite */
			var selected_suite = -1;
			$('.single-suite-tab').each(function () {
				if ($(this).hasClass('current_selected_tab')) {
					selected_suite = $(this).data('suite');
				}
			});

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
		}, 500);
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

	LoadCaseDataHtml(CasemainArr, suiteIndex, isReloadHeaderTab, display_type) {
		var html = '';
		//console.log('CasemainArr',CasemainArr);
		//console.log('suiteIndex',suiteIndex);

		if (CasemainArr != undefined && CasemainArr.length > 0) {

			var singleSuiteDataArr = CasemainArr[suiteIndex];
			var singleSuiteValue = singleSuiteDataArr.suite_value;

			var sortableCount = 0;
			if (singleSuiteValue.length > 0) {
				$.each(singleSuiteValue, function (case_index, single_value) {

					sortableCount++;

					var case_name = single_value.case_name;
					var case_value = single_value.case_value;
					var is_disable = single_value.is_disable;

					var extraSelectedClass = '';
					if (case_index == 0) {
						extraSelectedClass = 'selected-case';
					}

					if (display_type != undefined && (display_type == "add_case_step" || display_type == "add_action")) {
						extraSelectedClass = '';
					}

					//console.log('display_type',display_type);
					//console.log('extraSelectedClass',extraSelectedClass);

					var disableClass = '';
					if (is_disable != undefined && is_disable == 1) {
						disableClass = 'disabled-case';
					}
					var parentClass = 'parent_wrap parent_step' + case_index;

					html += `<tr class="sortable-` + sortableCount + ` case-main-wrap case-sub-wrap ` + extraSelectedClass + ` ` + disableClass + ` ` + parentClass + `" data-caseindex="` + (case_index + 1) + `" data-mainindex="` + (case_index) + `" data-sortposition="` + sortableCount + `">
	                      <td class="col-2 place_italic">
	                        <div class="table_data" data-toggle="collapse" data-target="#collapseten" aria-expanded="true" aria-controls="collapseten">
	                          <img id="more_button" src="assets/images/more.png"> Step ` + (case_index + 1) + ` :
	                        </div>
	                      </td>
	                      <td class="col-10 has-input place_italic" data-case_commend="case_name">
	                          <span class="case_value_lable">` + case_name + `</span>
	                          <input type="text" class="inpt display_hide case-input" name="" placeholder="Case Name" value="` + case_name + `">
	                      </td>
	                    </tr>`;

					if (case_value.length > 0) {
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

							console.log('elm1', elm);
							if (elm != undefined && elm.length > 30) {
								elm = single_case_value.element.substring(0, 27) + '...';
							}

							console.log('elm2', elm);

							var extraClass = "";
							if (single_case_value.is_disable == 1) {
								extraClass = 'disabled-case';
							}

							if (disableClass == 'disabled-case') {
								extraClass = 'disabled-case';
							}

							var childClass = 'child_wrap child_action' + case_index;

							var casedatalist = '';
							if (single_case_value.data_list != undefined && single_case_value.data_list.length > 0) {
								casedatalist = single_case_value.data_list.join('#');
							}
							console.log('val', val);
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
					}

					$('#case_data_wrap').html(html);
				})
			} else {
				$('#case_data_wrap').html(''); //new code 9-6-2020
			}

			//$('#inactive_action_icon').attr('style','display:none !important');
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

		}
	},

	SaveCaseDataAsJson() {
		var CasemainArr = {};
		chrome.storage.local.get(null, function (result) {
			try {
				if (result.data) {

					var caseTempArr = [];
					for (var i = 0; i < result.data.length; i++) {
						var test_suite = result.data[i];
						var pattern = /<title>(.*)<\/title>/gi;
						var suiteName = pattern.exec(test_suite)[1];
						var test_case = test_suite.match(/<table[\s\S]*?<\/table>/gi);
						if (test_case) {
							for (var j = 0; j < test_case.length; ++j) {

								var caseInfo = {};
								var f = test_case[j]
								var output = f.match(/<tbody>[\s\S]+?<\/tbody>/);
								var thead_output = f.match(/<thead>[\s\S]+?<\/thead>/);
								if (!output) {
									return null;
								}
								output = output[0]
									.replace(/<tbody>/, "")
									.replace(/<\/tbody>/, "");


								var caseName = thead_output[0]
									.replace(/<thead>/, "")
									.replace(/<\/thead>/, "");

								caseName = caseName
									.replace(/<tr>/, "")
									.replace(/<\/tr>/, "");

								caseName = caseName
									.replace(/<td rowspan="1" colspan="3">/, "")
									.replace(/<\/td>/, "");

								var tr = output.match(/<tr>[\s\S]*?<\/tr>/gi);
								output = "";

								var singleCaseArr = [];
								if (tr) {
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

										var dataList = pattern[5];
										var regex = /( |<([^>]+)>)/ig;
										dataList = dataList.replace(regex, "#");
										var res = dataList.split("#");

										var mainDataArr = [];
										if (res.length > 0) {
											$.each(res, function (idx, val) {
												if (val != '') {
													mainDataArr.push(val);
												}
											})
										}

										var singleCaseDetasils = {
											'action': pattern[2],
											'element': pattern[4],
											'value': pattern[8],
											'is_disable': 0,
											'data_list': mainDataArr,
										};

										singleCaseArr.push(singleCaseDetasils);
									}
								}

								caseInfo.case_name = caseName;
								caseInfo.case_value = singleCaseArr;
								caseTempArr.push(caseInfo);
							}

							CasemainArr.suite_name = suiteName;
							CasemainArr.suite_value = caseTempArr;
						}
					}
				}
			} catch (e) {
				console.error(e);
			}
		});


		CustomFunction.FetchChromeCaseData();

		setTimeout(function () {
			/* auto assign the case if there is no already case exists */
			var mainArrLength = Object.keys(CasemainArr).length;
			if (CasemainArr == undefined || mainArrLength == 0) {
				var tempObj = {
					case_name: "Enter Step Name",
					case_value: [],
				};
				var objArr = [];
				objArr.push(tempObj);
				CasemainArr.suite_name = "Untitled";
				CasemainArr.suite_value = objArr;

				var mainTestSuidData = [];

				/* initial time untitled test suit position is zero */
				mainTestSuidData.push(CasemainArr);
				CasemainArr = mainTestSuidData;
			} else {
				/* fetch selected case */
				var selectedCase = -1;
				var defaultCaseName = 'Enter Step Name';
				$('.case-main-wrap').each(function () {
					if ($(this).hasClass('selected-case')) {
						selectedCase = $(this).data('mainindex');
						defaultCaseName = $(this).children('.has-input').children('.case-input').val();
					}
				});

				if (selectedCase == -1) {
					var selected_suite = -1;
					$('.single-suite-tab').each(function () {
						if ($(this).hasClass('current_selected_tab')) {
							selected_suite = $(this).data('suite');
						}
					});
					if (selected_suite != -1) {
						var currentCaseVal = CasemainArr.suite_value[0].case_value;
						var tempObj = {
							case_name: "Enter Step Name",
							case_value: currentCaseVal,
						};
						var objArr = [];
						objArr.push(tempObj);
						console.log(objArr);
						var SavedCaseData = CustomFunction.caseDataArr;
						SavedCaseData[selected_suite].suite_value = objArr;
						CasemainArr = SavedCaseData;
					}

				} else {

					//if(selectedCase > -1){

					/* Fetch selected suite */
					var selected_suite = -1;
					$('.single-suite-tab').each(function () {
						if ($(this).hasClass('current_selected_tab')) {
							selected_suite = $(this).data('suite');
						}
					});

					if (selected_suite != -1) {
						var currentCaseVal = CasemainArr.suite_value[0].case_value;
						var SavedCaseData = CustomFunction.caseDataArr;

						SavedCaseData[selected_suite].suite_value[selectedCase].case_value = currentCaseVal;

						CasemainArr = SavedCaseData;
					}

				}
			}

			console.log('CasemainArr', CasemainArr);

			if (CasemainArr != undefined) {
				var case_data = {
					case_data: CasemainArr,
				};
				browser.storage.local.set(case_data);
				//CustomFunction.DisplayCaseData(true);
				CustomFunction.DisplayCaseData('save_record_data', false);
			}
		}, 1000);
	},

	UpdateCaseData(textValue, case_command, case_index, update_step_or_action, stepindex) {
		/* fetch Pre save data */
		CustomFunction.FetchChromeCaseData();

		/* Fetch selected suite */
		var selected_suite = -1;
		$('.single-suite-tab').each(function () {
			if ($(this).hasClass('current_selected_tab')) {
				selected_suite = $(this).data('suite');
			}
		});
		setTimeout(function () {
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

		}, 500);
	},

	DisplayCaseData(display_type, is_reload_header_tab, selectedTabIndx) {
		//console.log('display_type',display_type);
		CustomFunction.FetchChromeCaseData();
		var sortposition = $('.selected-case').data('sortposition');

		var selectedSuite = 0;

		if (selectedTabIndx != undefined) {
			selectedSuite = selectedTabIndx;
		}

		$('.single-suite-tab').each(function () {
			if ($(this).hasClass('current_selected_tab')) {
				selectedSuite = $(this).data('suite');
			}
		})

		if (display_type == "delete_suite") {
			selectedSuite = 0;
		}

		//console.log('CustomFunction.caseDataArr',CustomFunction.caseDataArr);

		setTimeout(function () {
			//CustomFunction.LoadCaseDataHtml(CustomFunction.caseDataArr,0,is_reload_header_tab,display_type);
			CustomFunction.LoadCaseDataHtml(CustomFunction.caseDataArr, selectedSuite, is_reload_header_tab, display_type);
		}, 500);

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
			setTimeout(function () {
				console.log('sortposition', sortposition);
				$('.sortable-' + sortposition).trigger('click');
			}, 800);
		}
	},

	ExportCaseData() {
		CustomFunction.FetchChromeCaseData();
		setTimeout(function () {
			/* Change Command */
			jsonObj = CustomFunction.caseDataArr;
			if (jsonObj.length > 0) {
				$.each(jsonObj, function (indx, val) {
					var suite_value = val.suite_value;
					$.each(suite_value, function (suite_indx, single_suite_val) {
						var case_value = single_suite_val.case_value;
						$.each(case_value, function (case_indx, single_case_val) {
							/*if(single_case_val.action == "open"){
								single_case_val.action = "go to";
							}*/

							if (single_case_val.action == "assertValue") {
								single_case_val.action = "validate text";
							} else if (single_case_val.action == "close") {
								single_case_val.action = "teardown";
							} else if (single_case_val.action == "open") {
								single_case_val.action = "go to link";
							} else if (single_case_val.action == "pause") {
								single_case_val.action = "sleep";
							} else if (single_case_val.action == "select") {
								single_case_val.action = "Select by Visible Text";
							} else if (single_case_val.action == "sendKeys") {
								single_case_val.action = "Keystroke keys";
							} else if (single_case_val.action == "store") {
								single_case_val.action = "save";
							} else if (single_case_val.action == "submit") {
								single_case_val.action = "click(submit)";
							} else if (single_case_val.action == "type") {
								single_case_val.action = "text";
							}
						})
					})

				})
			}
			CustomFunction.downloadObjectAsJson(jsonObj, 'export');

			/* Change in previous format */
			var newjsonObj = CustomFunction.caseDataArr;
			if (newjsonObj.length > 0) {
				$.each(newjsonObj, function (indx, val) {
					var suite_value = val.suite_value;
					$.each(suite_value, function (suite_indx, single_suite_val) {
						var case_value = single_suite_val.case_value;
						$.each(case_value, function (case_indx, single_case_val) {

							if (single_case_val.action == "validate text") {
								single_case_val.action = "assertValue";
							} else if (single_case_val.action == "teardown") {
								single_case_val.action = "close";
							} else if (single_case_val.action == "go to link") {
								single_case_val.action = "open";
							} else if (single_case_val.action == "sleep") {
								single_case_val.action = "pause";
							} else if (single_case_val.action == "Select by Visible Text") {
								single_case_val.action = "select";
							} else if (single_case_val.action == "Keystroke keys") {
								single_case_val.action = "sendKeys";
							} else if (single_case_val.action == "save") {
								single_case_val.action = "store";
							} else if (single_case_val.action == "click(submit)") {
								single_case_val.action = "submit";
							} else if (single_case_val.action == "text") {
								single_case_val.action = "type";
							}
						})
					})

				})
			}
			CustomFunction.caseDataArr = newjsonObj;
		}, 1500);
	},

	ExportCaseDataApi() {
		var server_url = $('#server_url').val();
		var username = $('#username').val();
		var password = $('#password').val();
		var server_port = $('#server_port').val();
		customData = CustomFunction.caseDataArr;
		console.log(customData);
		data = {
			'TestCases': []
		}
		for (var i = 0; i < customData.length; i++) {
			data['TestCases'].push({})
			test_case_name = customData[i]['suite_name']
			data['TestCases'][i]['Title'] = test_case_name;
			data['TestCases'][i]['Feature'] = "Sample Example";
			data['TestCases'][i]['Folder'] = "Sample";
			data['TestCases'][i]["Dependencies"] = {
				"Browser": ['Firefox'],
				"OS": ['windows']
			};
			data['TestCases'][i]['Steps'] = [];
			test_steps = customData[i]['suite_value']
			for (var j = 0; j < test_steps.length; j++) {
				data['TestCases'][i]['Steps'].push({})
				step_name = test_steps[j]['case_name']
				step_values = test_steps[j]['case_value']
				data['TestCases'][i]['Steps'][j]['Step name'] = step_name
				data['TestCases'][i]['Steps'][j]['Step actions'] = []
				data['TestCases'][i]['Steps'][j]['Step description'] = "Sequential Action"
				data['TestCases'][i]['Steps'][j]['Step expected'] = "Sequential Action"
				for (var k = 0; k < step_values.length; k++) {
					data['TestCases'][i]['Steps'][j]['Step actions'].push({})
					action_name = step_values[k]['action']
					element = step_values[k]['element']
					value = step_values[k]['value']
					data['TestCases'][i]['Steps'][j]['Step actions'][k]['Action name'] = action_name
					data['TestCases'][i]['Steps'][j]['Step actions'][k]['Action data'] = []
					action = []
					if (action_name == "assertValue") {
						action_name = "validate text";
					} else if (action_name == "close") {
						action_name = "teardown";
					} else if (action_name == "open") {
						action_name = "go to link";
					} else if (action_name == "pause") {
						action_name = "sleep";
					} else if (action_name == "select") {
						action_name = "Select by Visible Text";
					} else if (action_name == "sendKeys") {
						action_name = "Keystroke keys";
					} else if (action_name == "store") {
						action_name = "save";
					} else if (action_name == "submit" || action_name == "doubleClick") {
						action_name = "click";
					} else if (action_name == "type") {
						action_name = "text";
					}
					if (action_name == 'go to link') {
						data['TestCases'][i]['Steps'][j]['Step actions'][k]['Action data'].push([action_name, 'selenium action', element])
					} else {
						data['TestCases'][i]['Steps'][j]['Step actions'][k]['Action data'].push([element.split('=')[0], 'element parameter', element.split('=')[1]],
							[action_name, 'selenium action', value]
						)
					}

				}

			}


		}
		console.log(data)
		alert(JSON.stringify(data))
		var form = new FormData();
		form.append("username", username);
		form.append("password", password);

		var settings = {
			"async": true,
			"crossDomain": true,
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
				//		  	alert(JSON.stringify(data))
				user_info = {
					"async": true,
					"crossDomain": true,
					"url": server_url + "/api/user",
					"method": "GET",
					"headers": {
						"authorization": "Bearer " + accessToken,
					},

				}
				user_id = 1
				project_id = ""
				team_id = ""
				$.ajax(user_info).done(function (userResponse) {

					response = userResponse['data'][0]
					user_id = response['uid']
					project_id = response['project_id']
					team_id = response['team_id']
					var recorder_settings = {
						"async": true,
						"crossDomain": false,
						"url": server_url + "/Home/import_testcases_from_text/",
						"method": "POST",
						"headers": {
							"authorization": "Bearer " + accessToken,
						},
						data: {
							"json_text": JSON.stringify(data),
							"project_id": project_id,
							"team_id": team_id,
							"user_id": user_id

						},

					}

					$.ajax(recorder_settings).done(function (response) {
						CustomFunction.downloadObjectAsJson(response, 'export');
					}).fail(function (xhr, err) {})
				}).fail(function (xhr, err) {})



			}
		}).fail(function (jqXHR, textStatus, errorThrown) {});


	},

	exportLogs() {
		var log_data = [];
		$('#logcontainer').children('p').each(function () {
			log_data.push($(this).text());
		});

		if (log_data.length > 0) {
			CustomFunction.downloadObjectAsJson(log_data, 'log');
		} else {
			alert('Log data not found');
		}
	},

	ImportCaseData(evt) {

		var files = evt.target.files;

		// files is a FileList of File objects. List some properties.
		var output = [];
		for (var i = 0, f; f = files[i]; i++) {
			var reader = new FileReader();

			// Closure to capture the file information.
			reader.onload = (function (theFile) {
				return function (e) {
					/*console.log('e readAsText = ', e);
					console.log('e readAsText target = ', e.target);*/
					try {
						var json = JSON.parse(e.target.result);

						/*Check valid JSON file start*/
						var case_key;
						var key_status;

						var stopLoop = false;

						if (stopLoop == false) {
							$.each(json, function (jsonIndex, jsonValue) {
								jsonValueObjLength = Object.keys(jsonValue).length;
								if (jsonValueObjLength != 2) {
									key_status = false;
									stopLoop = true
								} else if (jsonValue.suite_name == undefined || jsonValue.suite_value == undefined) {
									key_status = false;
									stopLoop = true;
								} else {
									if (stopLoop == false) {
										$.each(jsonValue.suite_value, function (indx, case_data) {
											if (typeof case_data != "undefined") {
												if ((case_data.case_name == undefined || case_data.case_value == undefined)) {
													key_status = false;
													stopLoop = true;
												} else {
													if (stopLoop == false) {
														$.each(case_data.case_value, function (idx, case_action_value) {
															//console.log('case_action_value',case_action_value);
															/*if(case_action_value.action =='go to'){
																case_action_value.action = 'open';
															}*/

															if (case_action_value.action == "validate text") {
																case_action_value.action = "assertValue";
															} else if (case_action_value.action == "teardown") {
																case_action_value.action = "close";
															} else if (case_action_value.action == "go to link") {
																case_action_value.action = "open";
															} else if (case_action_value.action == "sleep") {
																case_action_value.action = "pause";
															} else if (case_action_value.action == "Select by Visible Text") {
																case_action_value.action = "select";
															} else if (case_action_value.action == "Keystroke keys") {
																case_action_value.action = "sendKeys";
															} else if (case_action_value.action == "save") {
																case_action_value.action = "store";
															} else if (case_action_value.action == "click(submit)") {
																case_action_value.action = "submit";
															} else if (case_action_value.action == "text") {
																case_action_value.action = "type";
															}

															var keys = Object.keys(case_action_value);
															if (stopLoop == false) {
																$.each(keys, function (key_indx, key_value) {
																	var tmparr = ['action', 'element', 'value', 'is_disable', 'data_list'];
																	if (tmparr.indexOf(key_value) !== -1 && stopLoop == false) {
																		key_status = true;
																	} else {
																		key_status = false;
																		stopLoop = true;
																	}
																});
															}
														});
													}
												}
											}
										});
									}
								}
							})
						}


						if (key_status == true) {

							var importJsonLength = json.length;
							var is_auth_user = CustomFunction.is_auth_user;
							var caseDataLength = CustomFunction.caseDataArr.length;

							var totalLength = importJsonLength + caseDataLength;
							if (is_auth_user == false && totalLength > 3) {
								alert('only 3 tabs are allowed, please configure your authentication settings');
							} else {
								$.each(json, function (jsonIndex, jsonValue) {
									CustomFunction.caseDataArr.push(jsonValue);
								});
								var case_data = {
									case_data: CustomFunction.caseDataArr,
								};

								browser.storage.local.set(case_data);
								CustomFunction.DisplayCaseData('import_json', true);
							}
						} else {
							alert('Invalid json format. Please check your json file');
						}

						//console.log('case data: ', key_status);
						/*Check valid JSON file end*/
					} catch (ex) {
						//alert('error when trying to parse json = ' + ex);
					}
				}
			})(f);
			reader.readAsText(f);
		}
	},

	FetchChromeCaseData() {
		CustomFunction.caseDataArr = {};
		chrome.storage.local.get(null, function (result) {
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
		});
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

	downloadObjectAsJson: function (exportObj, exportName) {
		var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
		var downloadAnchorNode = document.createElement('a');
		downloadAnchorNode.setAttribute("href", dataStr);
		downloadAnchorNode.setAttribute("download", exportName + ".json");
		document.body.appendChild(downloadAnchorNode); // required for firefox
		downloadAnchorNode.click();
		downloadAnchorNode.remove();
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

	UserAuthentication: function () {
		var server_url = $('#server_url').val();
		var username = $('#username').val();
		var password = $('#password').val();
		var server_port = $('#server_port').val();


		if (server_url == "" || username == "" || password == "") {
			$('.succ-wrap').html('').hide();
			$('.err-wrap').show().html('<p>Server URL, Username, Password are required</p>');
			setTimeout(function () {
				$('.succ-wrap,.err-wrap').hide();
			}, 3000);
		} else {

			if (server_port == undefined || server_port == null) {
				server_port = '';
			}

			CustomFunction.UserAuthAjaxCall(server_url, username, password, server_port, "setting_page");
		}
	},

	setThePlaySpeedData: function (speed, is_initial_app_open) {
		var sp_data = {
			speed_data: speed,
			is_initial_app_open: is_initial_app_open,
		};
		browser.storage.local.set(sp_data);
		document.getElementById("playback_select").value = speed;
	},

	LoadEvent: function () {
		CustomFunction.LoadAccordion();
		CustomFunction.DisplayCaseData('initial_load', true);

		/* user authentication */
		$(document).on('click', '#authenticate', function () {
			CustomFunction.UserAuthentication();
		})

		/* Close the main page content */
		$(document).on('click', '.close_main_page', function () {
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
		});

		$(document).on('click', '#add_new_case_action', function () {
			chrome.storage.local.get('meta_data', function(result) {
				console.log(result);
			});
			
			// if ($('#content').attr('style') == "display: block;") {
			// 	document.getElementById("add_new_test_case").click();
			// } else {
			// 	$('.close_main_page').trigger('click');
			// 	document.getElementById("add_new_test_case").click();
			// }
		})


		/* Mange playing speed */
		/* initial time set speed */
		chrome.storage.local.get(null, function (result) {
			try {
				if (result.speed_data) {
					var speed_data = result.speed_data;
					if (speed_data == undefined && speed_data == '') {
						CustomFunction.setThePlaySpeedData(3000, 1);
					} else {
						CustomFunction.setThePlaySpeedData(speed_data, 1);
					}
				} else {
					CustomFunction.setThePlaySpeedData(3000, 1);
				}
			} catch (e) {
				CustomFunction.setThePlaySpeedData(3000, 1);
			}
		});

		$(document).on('change', '#playback_select', function () {
			var speedval = $(this).val();
			CustomFunction.setThePlaySpeedData(speedval, 1);
		})


		/* display suite edit and delete */
		$(document).on('mouseover', '#header_tab li', function () {
			if (!$(this).hasClass('has-dropdown-menu')) {
				$('.suite-action').hide();
				$(this).children('.suite-action').show();
			}
		});

		$(document).on('mouseout', '#header_tab li', function () {
			$('.suite-action').hide();
		});

		$(document).on('mouseover', '.single-drop', function () {
			var suiteid = $(this).children('.dropdown-item').data('suite');
			$('.suite-action').hide();
			$('#suitaction' + suiteid).show();
		})
		$(document).on('mouseout', '.single-drop', function () {
			$('.suite-action').hide();
		})

		$(document).on('click', '.delete-suite', function () {
			var suiteid = $(this).data('suite');
			var r = confirm("Are you sure? you want to delete!");
			if (r == true) {
				CustomFunction.FetchChromeCaseData();
				setTimeout(function () {
					CustomFunction.caseDataArr.splice(suiteid, 1);
					var case_data = {
						case_data: CustomFunction.caseDataArr,
					};
					browser.storage.local.set(case_data);
					CustomFunction.DisplayCaseData('delete_suite', true);
				}, 500);
			}
		})

		/* edit suite */
		$(document).on('click', '.edit-suite', function () {
			var THIS = $(this);
			var suiteid = $(this).data('suite');
			var suitename = $(this).data('name');
			var changeSuiteName = prompt("Please enter the suite name", suitename);
			if (changeSuiteName != null) {
				THIS.parent('.suite-action').siblings('.single-suite-tab').html(changeSuiteName);
				CustomFunction.FetchChromeCaseData();
				setTimeout(function () {
					CustomFunction.caseDataArr[suiteid].suite_name = changeSuiteName;
					var case_data = {
						case_data: CustomFunction.caseDataArr,
					};
					browser.storage.local.set(case_data);
					CustomFunction.DisplayCaseData('edit_suite', true);
				}, 500);
			}
		})

		/* Show and Hide Play Stop wrap */
		$(document).on('click', '#record', function () {
			$('#record_wrap').hide();
			$('#stop_wrap').show();
		});

		/* Stop recording */
		$(document).on('click', '#record_stop', function () {
			$('#stop_wrap').hide();
			$('#record_wrap').show();
		});

		/* export logs */
		$(document).on('click', '#export_logs', function () {
			CustomFunction.exportLogs();
		})

		/* Json Export */
		$(document).on('click', '#export_case', function () {
			//CustomFunction.ExportCaseData();
			CustomFunction.ExportCaseDataApi();
		})

		/* Json Import */
		$(document).on('click', '#import_case', function () {
			$('#import_json').trigger('click').change();
		})

		/* Json Import */
		$(document).on('change', '#import_json', function (evt) {
			CustomFunction.ImportCaseData(evt);
			document.getElementById("import_json").value = "";
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

		/* Copy Case */
		$(document).on('click', '#case_copy', function () {

			/* Fetch selected suite */
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

					$('.case-main-wrap').each(function () {
						if ($(this).hasClass('selected-case')) {
							selectedStep = $(this).data('mainindex');
						}
					});
					/* copy the step */
					var cpyData = CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep];

					if (cpyData.case_name != '' || cpyData.case_name != undefined) {
						var newCopyObj = {
							'case_name': cpyData.case_name + ' copy',
							'case_value': cpyData.case_value,
						};

						CustomFunction.StepCopyData = newCopyObj;
						CustomFunction.copyType = 'step';
					}

				} else {

					var copyArr = [];
					/* Copy the action */
					$('.selected-case').each(function () {
						selectedCase = $(this).data('mainindex'); //action
						selectedStep = $(this).data('stepindex');

						var cpyData = CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value[selectedCase];
						copyArr.push(cpyData);

					});

					CustomFunction.StepCopyData = copyArr;
					CustomFunction.copyType = 'action';
				}

				alert('Copied!');
			}

			/* Fetch Selected Step */
			/*var selectedCase = $('.selected-case').data('mainindex');
			var selectedStep = $('.selected-case').data('stepindex');
			var selectedCase = -1;
			$('.case-main-wrap').each(function(){
				if($(this).hasClass('selected-case')){
					selectedCase = $(this).data('mainindex');
				}
			})

			if(selectedCase > -1){
				var cpyData = CustomFunction.caseDataArr.suite_value[selectedCase];
				if(cpyData.case_name !='' || cpyData.case_name != undefined){
					var newCopyObj = {
						'case_name' : cpyData.case_name +' copy',
						'case_value' : cpyData.case_value,
					};

					CustomFunction.StepCopyData = newCopyObj;
				}
			}*/
		});

		/* Paste Case */
		$(document).on('click', '#case_paste', function () {

			/* Fetch selected suite */
			var selected_suite = -1;
			$('.single-suite-tab').each(function () {
				if ($(this).hasClass('current_selected_tab')) {
					selected_suite = $(this).data('suite');
				}
			});

			if (selected_suite != -1 && CustomFunction.StepCopyData != null) {
				var selectedCase = $('.selected-case').data('mainindex');
				var selectedStep = $('.selected-case').data('stepindex');

				if (selectedStep == undefined) {
					$('.case-main-wrap').each(function () {
						if ($(this).hasClass('selected-case')) {
							selectedStep = $(this).data('mainindex');
						}
					});

					if (CustomFunction.copyType == 'step') {
						var nextPos = selectedCase + 1;

						var newArr = CustomFunction.caseDataArr[selected_suite].suite_value;
						CustomFunction.caseDataArr[selected_suite].suite_value.splice(nextPos, 0, CustomFunction.StepCopyData);

						var case_data = {
							case_data: CustomFunction.caseDataArr,
						};

						browser.storage.local.set(case_data);
						CustomFunction.DisplayCaseData('paste_case', false);

					} else if (CustomFunction.copyType == 'action') {
						if (CustomFunction.StepCopyData.length > 0) {
							$.each(CustomFunction.StepCopyData, function (indx, val) {
								CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.push(val);
							})

							var case_data = {
								case_data: CustomFunction.caseDataArr,
							};

							browser.storage.local.set(case_data);
							CustomFunction.DisplayCaseData('paste_action', false);
						}
					}


				} else {
					if (CustomFunction.copyType == 'action') {
						$('.selected-case').each(function () {
							selectedCase = $(this).data('mainindex'); //action
							selectedStep = $(this).data('stepindex');
							var nextPos = selectedCase + 1;

							$.each(CustomFunction.StepCopyData, function (indx, val) {
								//CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.push(val);
								CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.splice(nextPos, 0, val);
							})


							var case_data = {
								case_data: CustomFunction.caseDataArr,
							};

							browser.storage.local.set(case_data);
							CustomFunction.DisplayCaseData('paste_action', false);
						})
					}
				}
			}





			/*if(selectedCase > -1 && CustomFunction.StepCopyData != null){
				var nextPos = selectedCase + 1;

				var newArr = CustomFunction.caseDataArr.suite_value;
				CustomFunction.caseDataArr.suite_value.splice(nextPos, 0, CustomFunction.StepCopyData);
				var case_data = {
		            case_data: CustomFunction.caseDataArr,
		        };

		        browser.storage.local.set(case_data);
				CustomFunction.DisplayCaseData(false);
			}*/

			/*var PasteElm = document.getElementsByClassName("input-focus")[0];
			PasteElm.focus();
			document.execCommand('paste');*/
		});

		/* Disable Case */
		$(document).on('click', '#case_disable', function () {
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
					/* Disabl the step */
					$('.case-main-wrap').each(function () {
						if ($(this).hasClass('selected-case')) {
							selectedStep = $(this).data('mainindex');
						}
					});
					var textValue = 1;
					var case_command = 'is_disable';
					var case_index = selectedStep;
					CustomFunction.UpdateCaseData(textValue, case_command, case_index, 'update_step');

					$('.selected-case').addClass('disabled-case');
					$('.child_action' + selectedStep).addClass('disabled-case');

				} else {
					/* disable th action */
					$('.selected-case').each(function () {
						selectedCase = $(this).data('mainindex'); //action
						selectedStep = $(this).data('stepindex');

						/* Update the chrome case date as disable */
						var textValue = 1;
						var case_command = 'is_disable';
						var case_index = $(this).data('mainindex');

						var SavedCaseData = CustomFunction.caseDataArr;
						SavedCaseData[selected_suite].suite_value[selectedStep].case_value[case_index][case_command] = textValue;
						//CustomFunction.UpdateCaseData(textValue,case_command,case_index,'update_action',selectedStep);
					})

					var case_data = {
						case_data: CustomFunction.caseDataArr,
					};

					browser.storage.local.set(case_data);
					CustomFunction.LoadTheRecordDataHtml();

					$('.selected-case').addClass('disabled-case');
					//$( ".case-sub-wrap" ).removeClass( "selected-case" );
				}
			}
		});

		/* Enable Case */
		$(document).on('click', '#case_enable', function (event) {
			event.preventDefault();
			//$( ".case-sub-wrap" ).removeClass( "disabled-case" );

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
					/* Disabl the step */
					$('.case-main-wrap').each(function () {
						if ($(this).hasClass('selected-case')) {
							selectedStep = $(this).data('mainindex');
						}
					});
					var textValue = 0;
					var case_command = 'is_disable';
					var case_index = selectedStep;
					CustomFunction.UpdateCaseData(textValue, case_command, case_index, 'update_step');

					$('.selected-case').removeClass('disabled-case');
					$('.child_action' + selectedStep).removeClass('disabled-case');

				} else {
					/* disable th action */
					$('.selected-case').each(function () {
						selectedCase = $(this).data('mainindex'); //action
						selectedStep = $(this).data('stepindex');

						if (!$('.parent_step' + selectedStep).hasClass('disabled-case')) {

							/* Update the chrome case date as disable */
							var textValue = 0;
							var case_command = 'is_disable';
							var case_index = $(this).data('mainindex');

							var SavedCaseData = CustomFunction.caseDataArr;
							SavedCaseData[selected_suite].suite_value[selectedStep].case_value[case_index][case_command] = textValue;

							//CustomFunction.UpdateCaseData(textValue,case_command,case_index,'update_action',selectedStep);
							$(this).removeClass('disabled-case');
						}

					})

					var case_data = {
						case_data: CustomFunction.caseDataArr,
					}
					browser.storage.local.set(case_data);
					CustomFunction.LoadTheRecordDataHtml();

					//$('.selected-case').removeClass('disabled-case');
					//$( ".case-sub-wrap" ).removeClass( "selected-case" );
				}
			}


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



		/* Add New Test Case */
		$(document).on('click', '#add_new_test_case', function () {
			CustomFunction.FetchChromeCaseData();

			setTimeout(function () {

				var is_auth_user = CustomFunction.is_auth_user;
				var caseDataLength = CustomFunction.caseDataArr.length;

				/* For non auth user */
				if (is_auth_user == false && caseDataLength >= 3) {
					alert('only 3 tabs are allowed, please configure your authentication settings');
				} else {
					/* For auth user */
					var suiteVal = {
						'case_name': 'Enter Step Name',
						'case_value': []
					};
					var objArr = [];
					objArr.push(suiteVal);
					var new_obj = {
						'suite_name': 'Untitled',
						'suite_value': objArr
					};
					CustomFunction.caseDataArr.push(new_obj);
					var case_data = {
						case_data: CustomFunction.caseDataArr,
					};
					browser.storage.local.set(case_data);
					var lstIndx = CustomFunction.caseDataArr.length;
					lstIndx = lstIndx - 1;

					CustomFunction.DisplayCaseData('add_new_test_case', true, lstIndx);

				}
			}, 500);
		})

		/* Click on suit tab */
		$(document).on('click', '.single-suite-tab', function () {
			$('.dropdown-item').removeClass('active');
			$('#header_tab').children('li').removeClass('head_text pl-3');
			$(this).parent('li').addClass('head_text pl-3');
			$('.single-suite-tab').removeClass('current_selected_tab');
			$(this).addClass('current_selected_tab');

			$('.single-drop').removeClass('single-drop-active');
			if ($(this).parent().hasClass('single-drop')) {
				$(this).parent().addClass('single-drop-active');
			}

			$('.push_right').removeClass('disable_action');

			var suiteIndex = $(this).data('suite');
			CustomFunction.LoadCaseDataHtml(CustomFunction.caseDataArr, suiteIndex, false);
		});

		/* Click suit tab dopdown menu */
		$(document).on('click', '.dropdown-item', function () {
			$('.dropdown-item').removeClass('active');
			$(this).addClass('active');
			var suiteIndex = $(this).data('suite');

			$('.single-suite-tab').removeClass('current_selected_tab');
			$(this).addClass('current_selected_tab');

			CustomFunction.LoadCaseDataHtml(CustomFunction.caseDataArr, suiteIndex, false);
		})


		/* Sudipto Start*/

		/* *===* Dselect All by click esc start *===* */
		$(document).on('keydown', function (event) {
			if (event.key == "Escape") {
				$(".case-sub-wrap").removeClass("selected-case");
				$('.current_selected_tab').trigger('click');
			}
		});
		/* *===* Dselect All by click esc end *===* */

		/* Add new step start */
		$(document).on('click', '#add_case_step', function (event) {
			event.preventDefault();
			/* Fetch selected suite */
			var selected_suite = -1;
			$('.single-suite-tab').each(function () {
				if ($(this).hasClass('current_selected_tab')) {
					selected_suite = $(this).data('suite');
				}
			})

			/* get Selected case*/
			var selectedCase = -1;
			$('.case-main-wrap').each(function () {
				if ($(this).hasClass('selected-case')) {
					selectedCase = $(this).data('mainindex');
				}
			});

			var is_selected_step = true;
			/* if any step not selected the automatic create a step at the end of the all step */
			if (selectedCase == -1 && selected_suite > -1) {
				selectedCase = CustomFunction.caseDataArr[selected_suite].suite_value.length;
				selectedCase = selectedCase + 1;
				is_selected_step = false;
			}

			if (selectedCase > -1 && selected_suite > -1) {
				var nextPos = selectedCase + 1;
				var new_obj = {
					'case_name': 'Enter Step Name',
					'case_value': []
				};

				CustomFunction.caseDataArr[selected_suite].suite_value.splice(nextPos, 0, new_obj);
				var case_data = {
					case_data: CustomFunction.caseDataArr,
				};

				browser.storage.local.set(case_data);

				CustomFunction.DisplayCaseData('add_case_step', false);

				setTimeout(function () {
					console.log('nextPos', nextPos);
					if (is_selected_step == true) {
						$('.parent_step' + nextPos).trigger('click');
					} else {
						$('.parent_wrap').each(function () {
							if ($(this).data('caseindex') == (nextPos - 1)) {
								$(this).trigger('click');
							}
						})
					}
				}, 600);

			}
		});

		$(document).on('click', '.child_wrap', function () {
			$('#record_wrap,#play_wrap,#replay_wrap').addClass('disable_action');
		})
		$(document).on('click', '.parent_wrap', function () {
			$('#record_wrap,#play_wrap,#replay_wrap').removeClass('disable_action');
		})


		$(document).on('click', '#add_action', function (event) {
			event.preventDefault();

			/* Fetch selected suite */
			var selected_suite = -1;
			$('.single-suite-tab').each(function () {
				if ($(this).hasClass('current_selected_tab')) {
					selected_suite = $(this).data('suite');
				}
			});

			/* Fetch Selected Step */
			var selectedCase = $('.selected-case').data('mainindex');
			var selectedStep = $('.selected-case').data('stepindex');

			var new_obj = {
				'action': 'Action',
				'element': 'Element',
				'value': 'Value'
			};

			if (selectedStep == undefined) {
				$('.case-main-wrap').each(function () {
					if ($(this).hasClass('selected-case')) {
						selectedStep = $(this).data('mainindex');
					}
				});
				CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.push(new_obj);
				var case_data = {
					case_data: CustomFunction.caseDataArr,
				};

				var lestActionPos = CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.length;
				lestActionPos = lestActionPos - 1;
			} else {
				var nextPos = selectedCase + 1;
				CustomFunction.caseDataArr[selected_suite].suite_value[selectedStep].case_value.splice(nextPos, 0, new_obj);
				var case_data = {
					case_data: CustomFunction.caseDataArr,
				};

				var lestActionPos = nextPos;

			}

			browser.storage.local.set(case_data);
			CustomFunction.DisplayCaseData('add_action', false);

			setTimeout(function () {
				$('.child_action' + selectedStep).each(function () {
					var data_mainindex = $(this).data('mainindex');
					console.log('data_mainindex', data_mainindex);
					console.log('lestActionPos', lestActionPos);
					if (data_mainindex == lestActionPos) {
						$(this).trigger('click');
					}
				})
			}, 600);
		});


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

		chrome.storage.local.get(null, function (result) {
			try {
				if (result.is_initial_app_open) {
					$('.close_main_page').trigger('click');
				} else {
					document.getElementById("defaultOpen").click();
				}
			} catch (e) {
				document.getElementById("defaultOpen").click();
			}
		});
	},

	InitialTimeCheckAuthUserOrNot() {
		/* fetch username and password for browser storage */
		chrome.storage.local.get(null, function (result) {
			try {
				if (result.auth_data) {
					var auth_data = result.auth_data;
					if (auth_data != undefined && auth_data != '') {
						var words = CryptoJS.enc.Base64.parse(auth_data);
						var textString = CryptoJS.enc.Utf8.stringify(words); // 'Hello world'
						var authDetails = JSON.parse(textString);
						if (authDetails.server_url != undefined && authDetails.username != undefined && authDetails.password != undefined) {
							CustomFunction.UserAuthAjaxCall(authDetails.server_url, authDetails.username, authDetails.password, authDetails.server_port, "initialtime");
						}
					}
				}
			} catch (e) {
				console.log(e);
			}
		});
	},

	init: function () {
		CustomFunction.InitialTimeCheckAuthUserOrNot();
		CustomFunction.LoadEvent();
	}
}

jQuery(document).ready(function () {
	CustomFunction.init();

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