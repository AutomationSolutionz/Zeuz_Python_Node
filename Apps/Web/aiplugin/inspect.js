const browserAppData = chrome || browser;
setInterval(() => {
	// Only run this periodic extraction on the main page, not inside iframes 
	// (this prevents tracking pixels from overwriting the main page DOM)
	if (window.top !== window.self) return;

	var html = document.createElement('html');
	html.setAttribute('zeuz', 'aiplugin');
	var myString = document.documentElement.outerHTML;
	html.innerHTML = myString;

	var elements = html.getElementsByTagName('head');
	while (elements[0])
		elements[0].parentNode.removeChild(elements[0])

	var elements = html.getElementsByTagName('link');
	while (elements[0])
		elements[0].parentNode.removeChild(elements[0])

	var elements = html.getElementsByTagName('script');
	while (elements[0])
		elements[0].parentNode.removeChild(elements[0])

	var elements = html.getElementsByTagName('style');
	while (elements[0])
		elements[0].parentNode.removeChild(elements[0])

	// AI model works better on indented dom, so not removing indentation.
	// var result = html.outerHTML.replace(/\s+/g, ' ').replace(/>\s+</g, '><');

	//The following code removes non-unicode characters except newline and tab
	var result = html.outerHTML.replace(/[\x00-\x08\x0B-\x1F\x7F]/g, '');

	let mapData = { page_map_json: null, page_map: "" };
	if (typeof extractPageMapData === 'function') {
		try {
			mapData = extractPageMapData();
		} catch (e) {
			console.error("Error extracting page map:", e);
		}
	}

	browserAppData.runtime.sendMessage({
		apiName: 'node_ai_contents',
		dom: result,
		page_map: mapData.page_map,
		page_map_json: mapData.page_map_json
	})

}, 5000);

// Attribute panel limits: pages can carry huge attribute payloads (inline styles,
// data-* blobs), showing all of it makes the panel cover the page.
const MAX_ATTR_VALUE_CHARS = 60;
const MAX_ATTR_TOTAL_CHARS = 200;

// How long the pointer must stay inside an iframe before we spotlight it.
const IFRAME_DWELL_MS = 1500;
const FRAME_MESSAGE_TAG = 'zeuz-iframe-spotlight';

class Inspector {
	constructor() {
		this.win = window;
		this.doc = window.document;

		this.draw = this.draw.bind(this);
		this.getData = this.getData.bind(this);
		this.setOptions = this.setOptions.bind(this);
		this.onFrameMessage = this.onFrameMessage.bind(this);
		this.startFrameDwell = this.startFrameDwell.bind(this);
		this.endFrameDwell = this.endFrameDwell.bind(this);
		this.onFrameMouseOut = this.onFrameMouseOut.bind(this);
		this.syncSpotlight = this.syncSpotlight.bind(this);
		this.trackPointer = this.trackPointer.bind(this);

		this.cssNode = 'xpath-css';
		this.overlayElement = 'xpath-overlay';
		this.modalNode = 'zeuzMyModal';
		this.elementNode = 'zeuzMyElement';
		this.spotlightNode = 'zeuz-iframe-spotlight-host';

		this.isTopFrame = window.top === window.self;
		this.dwellTimer = null;
		this.dwellActive = false;
		this.spotlightHost = null;
	}


	getData(e) {

		e.stopImmediatePropagation();
		e.preventDefault && e.preventDefault();
		e.stopPropagation && e.stopPropagation();

		if ((e.target.id !== this.modalNode) && (e.target.id !== this.elementNode)) {


			// message element
			const modalNode = document.getElementById(this.modalNode);

			const insert_modal_text = (response, modal_id) => {
				console.log("insert_modal_text ..................")
				if (response["info"] == "success") {
					const modalText = 'Element data was recorded. Please Click "Add by AI"';
					console.log(modalText);

					if (this.successContainer) {
						this.successContainer.textContent = modalText;
						this.successContainer.classList.add('show');
						setTimeout(() => {
							this.successContainer.classList.remove('show');
						}, 3000);
					}
					return true;
				}
				console.error(response["info"]);
				return false;
			}

			async function send_data(server_url, api_key, data, modal_id, refinedHtml) {
				browserAppData.runtime.sendMessage({
					apiName: 'ai_record_single_action',
					data: data,
					html: refinedHtml,
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

					// get all <link> elements from div
					var elements = html.getElementsByTagName('link');
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

								//The following code removes non-unicode characters (except \x09 and \x0A that are \t and \n), that causes issue in lxml tree
								// Optionally remove control characters (0-31 and 127 in ASCII) except 9,10 \t and \n
								refinedHtml = refinedHtml.replace(/[\x00-\x08\x0B-\x1F\x7F]/g, '');
								var data = JSON.stringify({
									"page_src": refinedHtml,
									"action_type": "selenium"
								});

								send_data(server_url, api_key, data, this.modalNode, refinedHtml);

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

						refinedHtml = refinedHtml.replace(/[^\x00-\x7F]/g, '');
						refinedHtml = refinedHtml.replace(/[\x00-\x1F\x7F]/g, '');
						refinedHtml = refinedHtml.replace(/\s+/g, ' ').replace(/>\s+</g, '><');
						var data = JSON.stringify({
							"page_src": refinedHtml,
							"action_type": "selenium"
						});

						send_data(server_url, api_key, data, this.modalNode, refinedHtml);

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

	createAttributeDisplay() {
		const host = document.createElement('div');
		host.id = 'zeuz-attributes-host';
		Object.assign(host.style, {
			position: 'fixed',
			top: '12px',
			left: '12px',
			// just under the floating button, so the panel can never bury it
			zIndex: '2147483640',
			pointerEvents: 'none'
		});
		document.body.appendChild(host);

		const shadow = host.attachShadow({ mode: 'open' });
		const style = document.createElement('style');
		style.textContent = `
			.attributes-container {
				background: rgba(0, 0, 0, 0.82);
				color: white;
				padding: 6px 10px;
				border-radius: 6px;
				font-family: monospace;
				font-size: 11px;
				line-height: 1.45;
				max-width: 320px;
				word-break: break-all;
				backdrop-filter: blur(4px);
				border: 1px solid rgba(255, 255, 255, 0.2);
			}
			.tag {
				color: #c4b5fd;
				font-weight: bold;
			}
			.attrs:empty, .more:empty {
				display: none;
			}
			.more {
				color: rgba(255, 255, 255, 0.55);
				font-style: italic;
			}
		`;
		shadow.appendChild(style);

		const container = document.createElement('div');
		container.className = 'attributes-container';

		const tag = document.createElement('div');
		tag.className = 'tag';
		const attrs = document.createElement('div');
		attrs.className = 'attrs';
		const more = document.createElement('div');
		more.className = 'more';
		container.append(tag, attrs, more);
		shadow.appendChild(container);

		this.attributesHost = host;
		this.attributesTag = tag;
		this.attributesText = attrs;
		this.attributesMore = more;
	}

	renderAttributes(node) {
		const names = node.getAttributeNames();
		const parts = [];
		let total = 0;

		for (const name of names) {
			if (total >= MAX_ATTR_TOTAL_CHARS) break;
			let value = node.getAttribute(name) || '';
			if (value.length > MAX_ATTR_VALUE_CHARS) {
				// escaped, not literal: keeps this file pure ASCII so a page
				// charset other than UTF-8 cannot mangle the glyph
				value = value.slice(0, MAX_ATTR_VALUE_CHARS) + '\u2026';
			}
			const part = `${name}="${value}"`;
			parts.push(part);
			total += part.length;
		}

		const hidden = names.length - parts.length;
		this.attributesTag.textContent = `<${node.localName}>`;
		this.attributesText.textContent = parts.join(' ');
		this.attributesMore.textContent = hidden > 0 ? `+${hidden} more attribute${hidden > 1 ? 's' : ''}` : '';
	}

	createSuccessMessage() {
		const host = document.createElement('div');
		host.id = 'zeuz-success-host';
		Object.assign(host.style, {
			position: 'fixed',
			top: '20px',
			left: '50%',
			transform: 'translateX(-50%)',
			zIndex: '2147483647',
			pointerEvents: 'none'
		});
		document.body.appendChild(host);

		const shadow = host.attachShadow({ mode: 'open' });
		const style = document.createElement('style');
		style.textContent = `
			.success-message {
				background: linear-gradient(135deg, #4ade80, #22c55e);
				color: white;
				padding: 12px 20px;
				border-radius: 8px;
				font-family: sans-serif;
				font-size: 14px;
				font-weight: 500;
				box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
				border: 1px solid rgba(255, 255, 255, 0.2);
				opacity: 0;
				transform: translateY(-10px);
				transition: all 0.3s ease;
			}
			.success-message.show {
				opacity: 1;
				transform: translateY(0);
			}
		`;
		shadow.appendChild(style);

		const container = document.createElement('div');
		container.className = 'success-message';
		shadow.appendChild(container);

		this.successHost = host;
		this.successContainer = container;
	}

	// mouseover alone is not enough: moving across one large element never
	// re-fires it, so the panel would stay in a stale corner.
	trackPointer(e) {
		if (this.positionFrame) return;
		const x = e.clientX;
		const y = e.clientY;
		this.positionFrame = requestAnimationFrame(() => {
			this.positionFrame = null;
			this.updateAttributePosition(x, y);
		});
	}

	// Park the panel in whichever of the 4 corners is opposite the cursor,
	// so it never sits under the element being inspected.
	updateAttributePosition(mouseX, mouseY) {
		if (!this.attributesHost) return;

		const margin = '12px';
		const toRight = mouseX < window.innerWidth / 2;
		const toBottom = mouseY < window.innerHeight / 2;

		Object.assign(this.attributesHost.style, {
			left: toRight ? 'auto' : margin,
			right: toRight ? margin : 'auto',
			top: toBottom ? 'auto' : margin,
			bottom: toBottom ? margin : 'auto'
		});
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

		// attributes display if not exists
		if (!this.attributesHost) {
			this.createAttributeDisplay();
		}

		// position based on mouse location
		this.updateAttributePosition(e.clientX, e.clientY);
		this.renderAttributes(node);

		// pointer is back on the host page, so any iframe spotlight is stale
		if (this.spotlightHost && node !== this.spotlightFrame) {
			this.hideSpotlight();
		}
	}

	activate() {
		this.createOverlayElements();
		this.createSuccessMessage();

		const style = document.createElement('style');
		style.id = this.cssNode;
		style.textContent = '*{cursor:crosshair!important;}';
		document.head.appendChild(style);

		// add listeners
		document.addEventListener('click', this.getData, true);
		this.options.inspector && (document.addEventListener('mouseover', this.draw));
		this.options.inspector && (document.addEventListener('mousemove', this.trackPointer, { passive: true }));

		// iframe spotlight: children report dwell, every frame relays it upwards
		window.addEventListener('message', this.onFrameMessage);
		if (!this.isTopFrame) {
			document.addEventListener('mouseover', this.startFrameDwell);
			document.addEventListener('mouseout', this.onFrameMouseOut);
		}
	}

	deactivate() {
		// remove overlay
		this.removeOverlay();
		this.endFrameDwell();
		this.hideSpotlight();

		let Remove = [
			this.cssNode,
			this.overlayElement,
			'zeuz-attributes-host',
			'zeuz-success-host'
		]

		for (let elemId of Remove) {
			const elem = document.getElementById(elemId);
			elem && elem.remove();
		}

		// remove listeners
		document.removeEventListener('click', this.getData, true);
		this.options && this.options.inspector && (document.removeEventListener('mouseover', this.draw));
		document.removeEventListener('mousemove', this.trackPointer);
		cancelAnimationFrame(this.positionFrame);
		this.positionFrame = null;
		window.removeEventListener('message', this.onFrameMessage);
		document.removeEventListener('mouseover', this.startFrameDwell);
		document.removeEventListener('mouseout', this.onFrameMouseOut);

		// reset
		this.attributesHost = null;
		this.attributesTag = null;
		this.attributesText = null;
		this.attributesMore = null;
		this.successHost = null;
		this.successContainer = null;
	}

	/* ---------------- iframe spotlight ---------------- */

	// Inside a frame: once the pointer has stayed here long enough, ask the top
	// frame to dim everything but us.
	startFrameDwell() {
		if (this.dwellTimer || this.dwellActive) return;
		this.dwellTimer = setTimeout(() => {
			this.dwellTimer = null;
			this.dwellActive = true;
			window.parent.postMessage({
				tag: FRAME_MESSAGE_TAG,
				type: 'focus',
				rect: null,
				label: (document.title || location.hostname || '').slice(0, 60)
			}, '*');
		}, IFRAME_DWELL_MS);
	}

	// relatedTarget is null only when the pointer crosses out of this document
	onFrameMouseOut(e) {
		if (!e.relatedTarget) this.endFrameDwell();
	}

	endFrameDwell() {
		clearTimeout(this.dwellTimer);
		this.dwellTimer = null;
		if (!this.dwellActive) return;
		this.dwellActive = false;
		window.parent.postMessage({ tag: FRAME_MESSAGE_TAG, type: 'blur' }, '*');
	}

	onFrameMessage(e) {
		const data = e.data;
		if (!data || data.tag !== FRAME_MESSAGE_TAG) return;

		if (data.type === 'blur') {
			if (this.attributesHost) this.attributesHost.style.visibility = 'visible';
			this.isTopFrame ? this.hideSpotlight() : window.parent.postMessage(data, '*');
			return;
		}

		const frame = this.findFrameElement(e.source);
		if (!frame) return;

		// The pointer is inside the frame now and the frame highlights its own
		// element. Our highlight is still sitting on the <iframe> tag, which
		// would tint the whole frame, and our panel still shows that tag.
		this.removeOverlay();
		if (this.attributesHost) this.attributesHost.style.visibility = 'hidden';

		// translate the child's rect into this frame's viewport coordinates
		const frameRect = frame.getBoundingClientRect();
		const style = window.getComputedStyle(frame);
		const originX = frameRect.left + parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft);
		const originY = frameRect.top + parseFloat(style.borderTopWidth) + parseFloat(style.paddingTop);
		const rect = data.rect
			? { left: originX + data.rect.left, top: originY + data.rect.top, width: data.rect.width, height: data.rect.height }
			: { left: frameRect.left, top: frameRect.top, width: frameRect.width, height: frameRect.height };

		if (this.isTopFrame) {
			this.showSpotlight(frame, rect, data.label);
		} else {
			window.parent.postMessage({ tag: FRAME_MESSAGE_TAG, type: 'focus', rect, label: data.label }, '*');
		}
	}

	findFrameElement(sourceWindow) {
		return Array.from(document.querySelectorAll('iframe, frame'))
			.find(frame => frame.contentWindow === sourceWindow);
	}

	showSpotlight(frame, rect, label) {
		if (!this.spotlightHost) {
			const host = document.createElement('div');
			host.id = this.spotlightNode;
			Object.assign(host.style, {
				position: 'fixed',
				inset: '0',
				overflow: 'hidden',
				pointerEvents: 'none',
				zIndex: '2147483000',
				opacity: '0',
				transition: 'opacity 0.25s ease'
			});
			document.body.appendChild(host);

			const shadow = host.attachShadow({ mode: 'open' });
			const style = document.createElement('style');
			style.textContent = `
				.hole {
					position: fixed;
					border-radius: 6px;
					box-shadow: 0 0 0 100vmax rgba(15, 23, 42, 0.55), 0 0 26px rgba(167, 139, 250, 0.55);
					outline: 2px solid rgba(167, 139, 250, 0.95);
				}
				.label {
					position: fixed;
					padding: 3px 8px;
					background: rgba(167, 139, 250, 0.95);
					color: #1f1147;
					font-family: sans-serif;
					font-size: 11px;
					font-weight: 600;
					border-radius: 4px;
					white-space: nowrap;
					max-width: 60vw;
					overflow: hidden;
					text-overflow: ellipsis;
				}
			`;
			const hole = document.createElement('div');
			hole.className = 'hole';
			const badge = document.createElement('div');
			badge.className = 'label';
			shadow.append(style, hole, badge);

			this.spotlightHost = host;
			this.spotlightHole = hole;
			this.spotlightLabel = badge;

			window.addEventListener('scroll', this.syncSpotlight, true);
			window.addEventListener('resize', this.syncSpotlight);
			requestAnimationFrame(() => host && (host.style.opacity = '1'));
		}

		this.spotlightFrame = frame;
		// keep the offset of nested frames so scrolling can re-derive the rect
		const frameRect = frame.getBoundingClientRect();
		this.spotlightOffset = { x: rect.left - frameRect.left, y: rect.top - frameRect.top };
		this.spotlightLabel.textContent = label ? `\u29C9 iframe \u2014 ${label}` : '\u29C9 iframe';
		this.placeSpotlight(rect);
	}

	placeSpotlight(rect) {
		this.spotlightSize = { width: rect.width, height: rect.height };
		Object.assign(this.spotlightHole.style, {
			left: rect.left + 'px',
			top: rect.top + 'px',
			width: rect.width + 'px',
			height: rect.height + 'px'
		});
		const above = rect.top > 28;
		Object.assign(this.spotlightLabel.style, {
			left: rect.left + 'px',
			top: (above ? rect.top - 24 : rect.top + 8) + 'px'
		});
	}

	syncSpotlight() {
		if (!this.spotlightHost || !this.spotlightFrame) return;
		const frameRect = this.spotlightFrame.getBoundingClientRect();
		this.placeSpotlight({
			left: frameRect.left + this.spotlightOffset.x,
			top: frameRect.top + this.spotlightOffset.y,
			width: this.spotlightSize.width,
			height: this.spotlightSize.height
		});
	}

	hideSpotlight() {
		if (!this.spotlightHost) return;
		if (this.attributesHost) this.attributesHost.style.visibility = 'visible';
		window.removeEventListener('scroll', this.syncSpotlight, true);
		window.removeEventListener('resize', this.syncSpotlight);

		const host = this.spotlightHost;
		host.style.opacity = '0';
		setTimeout(() => host.remove(), 250);

		this.spotlightHost = null;
		this.spotlightHole = null;
		this.spotlightLabel = null;
		this.spotlightFrame = null;
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