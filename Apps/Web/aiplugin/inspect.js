const browserAppData = chrome || browser;

class Inspector {
	constructor() {
		this.win = window;
		this.doc = window.document;

		this.draw = this.draw.bind(this);
		this.getData = this.getData.bind(this);
		this.setOptions = this.setOptions.bind(this);

		this.cssNode = 'xpath-css';
		this.overlayElement = 'xpath-overlay';
		this.modalNode = 'zeuzMyModal';
		this.elementNode = 'zeuzMyElement';

	}


	getData(e) {

		e.stopImmediatePropagation();
		e.preventDefault && e.preventDefault();
		e.stopPropagation && e.stopPropagation();

		if ((e.target.id !== this.modalNode) && (e.target.id !== this.elementNode)) {


			// message element
			const modalNode = document.getElementById(this.modalNode);

			function insert_modal_text(response, modal_id) {
				console.log("insert_modal_text ..................")
				if (response["info"] == "success") {
					// show message about element
					const modalText = 'Element data was recorded. Please Click "Add by AI"';
					console.log(modalText);
					if (modalNode) {
						modalNode.innerText = modalText;
					} else {
						const modalHtml = document.createElement('div');
						modalHtml.innerText = modalText;
						modalHtml.id = modal_id;
						document.body.appendChild(modalHtml);
					}
					return true;
				}
				console.error(response["info"]);
				return false;

			}

			async function send_data(server_url, api_key, data, modal_id) {
				browserAppData.runtime.sendMessage({
					apiName: 'ai_record_single_action',
					data: data,
				},
				response => {
					insert_modal_text(response, modal_id);
				}
				);
			}

			// check if we are locating sibling now
			browserAppData.storage.local.get('mainelem', function (result) {

				if (result.mainelem == null) { // no pre-selected element

					this.elem = {};
					this.modalNode = 'zeuzMyModal';

					// Set custom Zeuz attribute
					var att = document.createAttribute("zeuz");
					att.value = "aiplugin";
					e.target.setAttributeNode(att);

					// Get element data
					this.elem['text'] = e.target.textContent;
					const element_text = e.target.textContent;
					this.elem['html'] = e.target.outerHTML;
					this.elem['original_html'] = e.target.outerHTML; // save for backup data


					// Get full page html, remove <style> and <script> tags //
					// create a new div container
					var html = document.createElement('html');
					var myString = document.documentElement.outerHTML;

					// assign your HTML to div's innerHTML
					html.innerHTML = myString;

					// get all <script> elements from div
					var elements = html.getElementsByTagName('head');
					while (elements[0])
						elements[0].parentNode.removeChild(elements[0])

					// get all <script> elements from div
					var elements = html.getElementsByTagName('script');
					while (elements[0])
						elements[0].parentNode.removeChild(elements[0])

					// get all <style> elements from div
					var elements = html.getElementsByTagName('style');
					while (elements[0])
						elements[0].parentNode.removeChild(elements[0])

					// get div's innerHTML into a new variable
					var refinedHtml = html.outerHTML;

					// choose sibling element
					browserAppData.storage.local.get(['sibling'], function (result) {
						if (result.sibling && confirm('Do you want to select a helper sibling element?')) {

							// store main
							//browserAppData.storage.local.set({mainelem: this.elem['html']});
							browserAppData.storage.local.set({
								mainelem: this.elem['html']
							}, function () {
								console.log('Main element is set to ' + element_text);

							});
						} else { // don't select sibling, send directly

							// copy action/element data
							// this.options.clipboard && ( this.copyText(XPath) );
							// this.options.clipboard && ( this.copyText(JSON.stringify(tracker_info)));

							// send data to zeuz server
							// this.sendData(tracker_info, backup_tracker_info);

							// get url-key and send data to zeuz
							browserAppData.storage.local.get(['key', 'url'], function (result) {

								// console.log('Value currently is ' + result.key);
								var server_url = result.url;
								var api_key = result.key;


								// send data to zeuz server directly

								var data = JSON.stringify({
									"page_src": refinedHtml,
									"action_type": "selenium"
								});

								send_data(server_url, api_key, data, this.modalNode);

							});
							// remove zeuz attribute
							e.target.removeAttributeNode(att);


						}
					});


				} else { // we are locating sibling now, send it with the main element


					this.sibling = {};
					this.modalNode = 'zeuzMyModal';

					// Set custom Zeuz-sibling attribute
					var att = document.createAttribute("zeuz-sibling");
					att.value = "aiplugin-sibling";
					e.target.setAttributeNode(att);

					// Get element data
					this.sibling['text'] = e.target.textContent;
					const element_text = e.target.textContent;
					this.sibling['html'] = e.target.outerHTML;
					this.sibling['original_html'] = e.target.outerHTML; // save for backup data

					// Get full page html, remove <style> and <script> tags //
					// create a new div container
					var div = document.createElement('div');
					var myString = document.documentElement.outerHTML;

					// assign your HTML to div's innerHTML
					div.innerHTML = myString;

					// get all <script> elements from div
					var elements = div.getElementsByTagName('script');

					// remove all <script> elements
					while (elements[0])
						elements[0].parentNode.removeChild(elements[0])

					// get all <style> elements from div
					var elements = div.getElementsByTagName('style');

					// remove all <style> elements
					while (elements[0])
						elements[0].parentNode.removeChild(elements[0])

					// get div's innerHTML into a new variable
					var refinedHtml = div.innerHTML;


					// get url-key and send data to zeuz
					browserAppData.storage.local.get(['key', 'url'], function (result) {

						// console.log('Value currently is ' + result.key);
						var server_url = result.url;
						var api_key = result.key;


						// send data to zeuz server directly

						var data = JSON.stringify({
							"page_src": refinedHtml,
							"action_type": "selenium"
						});

						send_data(server_url, api_key, data, this.modalNode);

					});
					// remove zeuz attribute
					e.target.removeAttributeNode(att);


					// delete main element from storage
					// browserAppData.storage.local.set({main: null});
					browserAppData.storage.local.set({
						mainelem: null
					}, function () {
						console.log('Sibling/helper element sending completed.');
					});


				}

			});


		}

	}

	getOptions() {
		console.log(navigator.userAgentData.platform);
		const storage = browserAppData.storage && (browserAppData.storage.local);
		const promise = storage.get({
			inspector: true,
			clipboard: true,
			sibling: false,
			shortid: true,
			position: 'bl'
		}, this.setOptions);
		(promise && promise.then) && (promise.then(this.setOptions()));
	}

	setOptions(options) {
		this.options = options;
		let position = 'bottom:0;left:0';
		let positionParent = 'top:0;left:0';
		let positionModal = 'top:50%;left:40%';
		switch (options.position) {
			case 'tl':
				position = 'top:0;left:0';
				break;
			case 'tr':
				position = 'top:0;right:0';
				break;
			case 'br':
				position = 'bottom:0;right:0';
				break;
			default:
				break;
		}
		this.styles = `*{cursor:crosshair!important;}#xpath-content{${position};cursor:initial!important;padding:10px;background:gray;color:white;position:fixed;font-size:14px;z-index:10000001;}#xpath-parent-content{${positionParent};cursor:initial!important;padding:10px;background:gray;color:white;position:fixed;font-size:14px;z-index:10000001;}#${this.modalNode}{${position};cursor:initial!important;padding:10px;background:#F2F2F2;color:green;position:fixed;font-size:14px;z-index:10000001;}#${this.elementNode}{${positionParent};cursor:initial!important;padding:10px;background:gray;color:white;position:fixed;font-size:14px;z-index:10000001;}`;
		this.activate();
	}

	createOverlayElements() {
		const overlayStyles = {
			background: 'rgba(120, 170, 210, 0.7)',
			padding: 'rgba(77, 200, 0, 0.3)',
			margin: 'rgba(255, 155, 0, 0.3)',
			border: 'rgba(255, 200, 50, 0.3)'
		};

		this.container = this.doc.createElement('div');
		this.node = this.doc.createElement('div');
		this.border = this.doc.createElement('div');
		this.padding = this.doc.createElement('div');
		this.content = this.doc.createElement('div');

		this.border.style.borderColor = overlayStyles.border;
		this.padding.style.borderColor = overlayStyles.padding;
		this.content.style.backgroundColor = overlayStyles.background;

		Object.assign(this.node.style, {
			borderColor: overlayStyles.margin,
			pointerEvents: 'none',
			position: 'fixed'
		});

		this.container.id = this.overlayElement;
		this.container.style.zIndex = 10000000;
		this.node.style.zIndex = 10000000;

		this.container.appendChild(this.node);
		this.node.appendChild(this.border);
		this.border.appendChild(this.padding);
		this.padding.appendChild(this.content);
	}

	removeOverlay() {
		const overlayHtml = document.getElementById(this.overlayElement);
		overlayHtml && overlayHtml.remove();
	}

	copyText(XPath) {
		const hdInp = document.createElement('textarea');
		hdInp.textContent = XPath;
		document.body.appendChild(hdInp);
		hdInp.select();
		document.execCommand('copy');
		hdInp.remove();
	}

	draw(e) {
		const node = e.target;

		this.removeOverlay();

		const box = this.getNestedBoundingClientRect(node, this.win);
		const dimensions = this.getElementDimensions(node);

		this.boxWrap(dimensions, 'margin', this.node);
		this.boxWrap(dimensions, 'border', this.border);
		this.boxWrap(dimensions, 'padding', this.padding);

		Object.assign(this.content.style, {
			height: box.height - dimensions.borderTop - dimensions.borderBottom - dimensions.paddingTop - dimensions.paddingBottom + 'px',
			width: box.width - dimensions.borderLeft - dimensions.borderRight - dimensions.paddingLeft - dimensions.paddingRight + 'px',
		});

		Object.assign(this.node.style, {
			top: box.top - dimensions.marginTop + 'px',
			left: box.left - dimensions.marginLeft + 'px',
		});

		this.doc.body.appendChild(this.container);


		// show element attributes
		const elementNode = document.getElementById(this.elementNode);
		var elementText = "";
		for (let name of e.target.getAttributeNames()) {
			let value = e.target.getAttribute(name);
			var each = name + " = \"" + value + "\", ";
			elementText += each;
		}
		if (elementNode) {
			elementNode.innerText = elementText;
		} else {
			const elementHtml = document.createElement('div');
			elementHtml.innerText = elementText;
			elementHtml.id = this.elementNode;
			document.body.appendChild(elementHtml);
		}

	}

	activate() {
		this.createOverlayElements();
		// add styles
		if (!document.getElementById(this.cssNode)) {
			const styles = document.createElement('style');
			styles.innerText = this.styles;
			styles.id = this.cssNode;
			document.getElementsByTagName('head')[0].appendChild(styles);
		}
		// add listeners
		document.addEventListener('click', this.getData, true);
		this.options.inspector && (document.addEventListener('mouseover', this.draw));
	}

	deactivate() {
		// remove overlay
		this.removeOverlay();

		this.cssNode = 'xpath-css';
		this.overlayElement = 'xpath-overlay';
		this.modalNode = 'zeuzMyModal';
		this.elementNode = 'zeuzMyElement';

		let Remove = [
			this.cssNode,
			this.overlayElement,
			this.modalNode,
			this.elementNode,
		]

		for (let elem of Remove){
			elem = document.getElementById(elem);
			elem && elem.remove();
		}

		// remove styles
		const cssNode = document.getElementById(this.cssNode);
		cssNode && cssNode.remove();

		// remove listeners
		document.removeEventListener('click', this.getData, true);
		this.options && this.options.inspector && (document.removeEventListener('mouseover', this.draw));
	}

	getXPath(el) {
		let nodeElem = el;
		if (nodeElem.id && this.options.shortid) {
			return `//*[@id="${nodeElem.id}"]`;
		}
		const parts = [];
		while (nodeElem && nodeElem.nodeType === Node.ELEMENT_NODE) {
			let nbOfPreviousSiblings = 0;
			let hasNextSiblings = false;
			let sibling = nodeElem.previousSibling;
			while (sibling) {
				if (sibling.nodeType !== Node.DOCUMENT_TYPE_NODE && sibling.nodeName === nodeElem.nodeName) {
					nbOfPreviousSiblings++;
				}
				sibling = sibling.previousSibling;
			}
			sibling = nodeElem.nextSibling;
			while (sibling) {
				if (sibling.nodeName === nodeElem.nodeName) {
					hasNextSiblings = true;
					break;
				}
				sibling = sibling.nextSibling;
			}
			const prefix = nodeElem.prefix ? nodeElem.prefix + ':' : '';
			const nth = nbOfPreviousSiblings || hasNextSiblings ? `[${nbOfPreviousSiblings + 1}]` : '';
			parts.push(prefix + nodeElem.localName + nth);
			nodeElem = nodeElem.parentNode;
		}
		return parts.length ? '/' + parts.reverse().join('/') : '';
	}

	getElementDimensions(domElement) {
		const calculatedStyle = window.getComputedStyle(domElement);
		return {
			borderLeft: +calculatedStyle.borderLeftWidth.match(/[0-9]*/)[0],
			borderRight: +calculatedStyle.borderRightWidth.match(/[0-9]*/)[0],
			borderTop: +calculatedStyle.borderTopWidth.match(/[0-9]*/)[0],
			borderBottom: +calculatedStyle.borderBottomWidth.match(/[0-9]*/)[0],
			marginLeft: +calculatedStyle.marginLeft.match(/[0-9]*/)[0],
			marginRight: +calculatedStyle.marginRight.match(/[0-9]*/)[0],
			marginTop: +calculatedStyle.marginTop.match(/[0-9]*/)[0],
			marginBottom: +calculatedStyle.marginBottom.match(/[0-9]*/)[0],
			paddingLeft: +calculatedStyle.paddingLeft.match(/[0-9]*/)[0],
			paddingRight: +calculatedStyle.paddingRight.match(/[0-9]*/)[0],
			paddingTop: +calculatedStyle.paddingTop.match(/[0-9]*/)[0],
			paddingBottom: +calculatedStyle.paddingBottom.match(/[0-9]*/)[0]
		};
	}

	getOwnerWindow(node) {
		if (!node.ownerDocument) {
			return null;
		}
		return node.ownerDocument.defaultView;
	}

	getOwnerIframe(node) {
		const nodeWindow = this.getOwnerWindow(node);
		if (nodeWindow) {
			return nodeWindow.frameElement;
		}
		return null;
	}

	getBoundingClientRectWithBorderOffset(node) {
		const dimensions = this.getElementDimensions(node);
		return this.mergeRectOffsets([
			node.getBoundingClientRect(),
			{
				top: dimensions.borderTop,
				left: dimensions.borderLeft,
				bottom: dimensions.borderBottom,
				right: dimensions.borderRight,
				width: 0,
				height: 0
			}
		]);
	}

	mergeRectOffsets(rects) {
		return rects.reduce((previousRect, rect) => {
			if (previousRect === null) {
				return rect;
			}
			return {
				top: previousRect.top + rect.top,
				left: previousRect.left + rect.left,
				width: previousRect.width,
				height: previousRect.height,
				bottom: previousRect.bottom + rect.bottom,
				right: previousRect.right + rect.right
			};
		});
	}

	getNestedBoundingClientRect(node, boundaryWindow) {
		const ownerIframe = this.getOwnerIframe(node);
		if (ownerIframe && ownerIframe !== boundaryWindow) {
			const rects = [node.getBoundingClientRect()];
			let currentIframe = ownerIframe;
			let onlyOneMore = false;
			while (currentIframe) {
				const rect = this.getBoundingClientRectWithBorderOffset(currentIframe);
				rects.push(rect);
				currentIframe = this.getOwnerIframe(currentIframe);
				if (onlyOneMore) {
					break;
				}
				if (currentIframe && this.getOwnerWindow(currentIframe) === boundaryWindow) {
					onlyOneMore = true;
				}
			}
			return this.mergeRectOffsets(rects);
		}
		return node.getBoundingClientRect();
	}

	boxWrap(dimensions, parameter, node) {
		Object.assign(node.style, {
			borderTopWidth: dimensions[parameter + 'Top'] + 'px',
			borderLeftWidth: dimensions[parameter + 'Left'] + 'px',
			borderRightWidth: dimensions[parameter + 'Right'] + 'px',
			borderBottomWidth: dimensions[parameter + 'Bottom'] + 'px',
			borderStyle: 'solid'
		});
	}
}

const inspect = new Inspector();
browserAppData.runtime.onMessage.addListener(request => {
	if (request.action === 'activate') {
		return inspect.getOptions();
	}
	return inspect.deactivate();
});