function extractPageMapData() {
    // ── Helpers ──────────────────────────────────────────────────────────────
    const vw = window.innerWidth, vh = window.innerHeight;

    function isVisible(el) {
        const s = window.getComputedStyle(el);
        return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) >= 0.1;
    }

    function inViewport(el) {
        const r = el.getBoundingClientRect();
        return r.bottom > 0 && r.right > 0 && r.top < vh && r.left < vw;
    }

    function norm(s, max = 120) {
        return (s || '').replace(/\s+/g, ' ').trim().slice(0, max);
    }

    // ── XPath generator ──────────────────────────────────────────────────────
    function getXPath(el) {
        if (el.id) return `//*[@id="${el.id}"]`;
        const stableAttrs = ['name', 'data-testid', 'aria-label', 'placeholder'];
        for (const attr of stableAttrs) {
            const val = el.getAttribute(attr);
            if (val) {
                const tag = el.tagName.toLowerCase();
                try {
                    if (document.querySelectorAll(`${tag}[${attr}="${CSS.escape(val)}"]`).length === 1)
                        return `//${tag}[@${attr}="${val}"]`;
                } catch (e) {
                    // Ignore escaping errors
                }
            }
        }
        if (['BUTTON', 'A'].includes(el.tagName)) {
            const txt = el.innerText.trim().slice(0, 60);
            if (txt) {
                const tag = el.tagName.toLowerCase();
                const hits = [...document.querySelectorAll(tag)].filter(e => e.innerText.trim().startsWith(txt));
                if (hits.length === 1) return `//${tag}[normalize-space()="${txt}"]`;
            }
        }
        function pos(e) {
            const tag = e.tagName.toLowerCase();
            const sibs = [...e.parentNode.children].filter(c => c.tagName === e.tagName);
            return `${tag}${sibs.length > 1 ? `[${sibs.indexOf(e) + 1}]` : ''}`;
        }
        const parts = [];
        let cur = el;
        while (cur && cur.nodeType === 1) { parts.unshift(pos(cur)); cur = cur.parentElement; }
        return '/' + parts.join('/');
    }

    // ── Label resolver ────────────────────────────────────────────────────────
    function getLabel(el) {
        if (el.id) {
            const lbl = document.querySelector(`label[for="${el.id}"]`);
            if (lbl) return lbl.innerText.trim();
        }
        const wrap = el.closest('label');
        if (wrap) return wrap.innerText.replace(el.value || '', '').trim();
        const al = el.getAttribute('aria-label');
        if (al) return al.trim();
        const alby = el.getAttribute('aria-labelledby');
        if (alby) { const ref = document.getElementById(alby); if (ref) return ref.innerText.trim(); }
        return null;
    }

    function getNearestHeading(el) {
        let cur = el.parentElement;
        while (cur && cur !== document.body) {
            const h = cur.querySelector('h1,h2,h3,h4,h5,h6');
            if (h) return norm(h.innerText, 80);
            cur = cur.parentElement;
        }
        return null;
    }

    // ── Interactive element selector ─────────────────────────────────────────
    const ACTION_SELECTOR = [
        'input:not([type=hidden])', 'textarea', 'select',
        'button', 'a[href]',
        '[role=button]', '[role=link]', '[role=textbox]',
        '[role=checkbox]', '[role=radio]', '[role=combobox]', '[role=option]'
    ].join(',');

    const actionEls = new Set(document.querySelectorAll(ACTION_SELECTOR));

    // ── Text node selector ───────────────────────────────────────────────────
    const TEXT_SELECTOR = 'h1,h2,h3,h4,h5,h6,p,li,td,th,label,span,div,[role=heading],[role=status],[role=alert],[aria-live]';

    function getDirectText(el) {
        let text = '';
        for (const node of el.childNodes) {
            if (node.nodeType === Node.TEXT_NODE) text += node.textContent;
        }
        return text.replace(/\s+/g, ' ').trim();
    }

    function hasOwnText(el) {
        const full = norm(el.innerText, 200);
        if (!full || full.length < 3) return false;
        if (actionEls.has(el)) return false;
        const nested = [...el.querySelectorAll(ACTION_SELECTOR)];
        if (nested.length === 1 && norm(nested[0].innerText, 200) === full) return false;
        return true;
    }

    // ── Collect everything in DOM order ──────────────────────────────────────
    const allNodes = [];

    // Pre-compute DOM order Map to avoid O(N^2) slowdown on large pages (eBay/Amazon)
    const domOrderMap = new Map();
    document.querySelectorAll('*').forEach((el, idx) => domOrderMap.set(el, idx));

    // Pass 1 — action elements
    document.querySelectorAll(ACTION_SELECTOR).forEach(el => {
        if (!isVisible(el)) return;
        const form = el.closest('form');
        allNodes.push({
            _type: 'action',
            _el: el,
            _order: domOrderMap.get(el) || 0,
            tag: el.tagName.toLowerCase(),
            type: el.getAttribute('type') || null,
            role: el.getAttribute('role') || el.tagName.toLowerCase(),
            id: el.id || null,
            name: el.getAttribute('name') || null,
            placeholder: el.getAttribute('placeholder') || null,
            label: getLabel(el) || null,
            text: norm(el.innerText || el.value || '', 80) || null,
            required: el.required || false,
            disabled: el.disabled || false,
            in_viewport: inViewport(el),
            form_id: form && form.id ? form.id : null,
            heading: getNearestHeading(el),
            xpath: getXPath(el),
        });
    });

    // Pass 2 — text context nodes
    const seenTexts = new Set();
    document.querySelectorAll(TEXT_SELECTOR).forEach(el => {
        if (!isVisible(el) || !inViewport(el)) return;
        if (!hasOwnText(el)) return;
        const text = norm(el.innerText, 150);
        if (!text || text.length < 5) return;
        if (seenTexts.has(text)) return;

        let dominated = false;
        for (const seen of seenTexts) { if (seen.includes(text) || text.includes(seen)) { dominated = true; break; } }
        if (dominated) return;
        seenTexts.add(text);

        const tag = el.tagName.toLowerCase();
        const isHeading = /^h[1-6]$/.test(tag) || el.getAttribute('role') === 'heading';
        allNodes.push({
            _type: 'text',
            _el: el,
            _order: domOrderMap.get(el) || 0,
            kind: isHeading ? 'heading' : (el.getAttribute('role') || tag),
            text,
            in_viewport: true,
        });
    });

    // Sort by DOM order
    allNodes.sort((a, b) => a._order - b._order);

    // Strip internal fields and assign idx
    const page_map_json = allNodes.map((n, i) => {
        const { _type, _el, _order, ...rest } = n;
        return { idx: i, node_type: _type, ...rest };
    });

    // Build compact text map
    const lines = ["# Page Map (text context + interactive elements, in document order)\n"];
    for (const node of page_map_json) {
        if (node.node_type === "text") {
            const kind = (node.kind || "text").toUpperCase();
            const vp = node.in_viewport ? "👁" : "↕";
            lines.push(`  ${vp} [${kind}] "${node.text}"`);
        } else {
            const parts = [`[${node.idx}]`, (node.role || '').toUpperCase()];
            if (node.label) parts.push(`label='${node.label}'`);
            if (node.placeholder) parts.push(`placeholder='${node.placeholder}'`);
            if (node.text) parts.push(`text='${node.text}'`);
            if (node.type) parts.push(`type=${node.type}`);
            if (node.name) parts.push(`name=${node.name}`);
            if (node.required) parts.push("required");
            if (node.disabled) parts.push("disabled");
            if (node.heading) parts.push(`section='${node.heading}'`);
            const vp = node.in_viewport ? "👁" : "↕";
            parts.push(vp);
            lines.push("  " + parts.join("  "));
        }
    }
    const page_map = lines.join("\n");

    return { page_map_json, page_map };
}
