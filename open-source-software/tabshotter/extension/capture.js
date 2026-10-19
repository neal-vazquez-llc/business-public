/* TabShotterUwU: live DOM -> inert, minimized DOM. Runs in the isolated world. */
(() => {
  'use strict';
  const ALLOWED = new Set('a abbr article aside b bdi bdo blockquote br caption code col colgroup dd del details dfn div dl dt em figcaption figure footer h1 h2 h3 h4 h5 h6 header hr i ins kbd li main mark nav ol p pre q rp rt ruby s samp section small span strong sub summary sup table tbody td tfoot th thead time tr u ul var wbr'.split(' '));
  const DROP = new Set('script style link meta base iframe frame frameset object embed applet svg math template noscript canvas audio video source track picture img portal fencedframe'.split(' '));
  const CONTROLS = new Set('input textarea select option optgroup button output meter progress datalist'.split(' '));
  const MAX_NODES = 100000;
  const MAX_TEXT = 4000000;
  const POLICY = "default-src 'none'; script-src 'none'; style-src 'none'; img-src 'none'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";

  globalThis.TabShotterCapture = async function capture() {
    if (!/^https?:$/.test(location.protocol)) throw new Error('Capture is limited to ordinary HTTP(S) pages.');
    const capturedAt = new Date().toISOString();
    const output = document.implementation.createHTMLDocument('Sanitized live DOM');
    const meta = output.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = POLICY;
    output.head.prepend(meta);
    const charset = output.createElement('meta');
    charset.setAttribute('charset', 'utf-8');
    output.head.prepend(charset);
    let nodes = 0, characters = 0, removed = 0;
    function visit(node, parent, depth) {
      if (++nodes > MAX_NODES || depth > 250) throw new Error('Page is too large or deeply nested for safe capture. Nothing was saved.');
      if (node.nodeType === Node.TEXT_NODE) {
        characters += node.data.length;
        if (characters > MAX_TEXT) throw new Error('Page text exceeds the capture limit. Nothing was saved.');
        parent.appendChild(output.createTextNode(node.data));
        return;
      }
      if (node.nodeType !== Node.ELEMENT_NODE) return;
      const tag = node.localName.toLowerCase();
      if (node.namespaceURI !== 'http://www.w3.org/1999/xhtml' || DROP.has(tag) || node.hidden || node.getAttribute('aria-hidden') === 'true') { removed++; return; }
      const computed = getComputedStyle(node);
      if (computed.display === 'none' || computed.visibility === 'hidden' || computed.visibility === 'collapse' || computed.contentVisibility === 'hidden') { removed++; return; }
      if (CONTROLS.has(tag) || node.isContentEditable || node.hasAttribute('contenteditable')) {
        parent.appendChild(output.createTextNode('[editable/control content removed]'));
        removed++; return;
      }
      // Never copy attributes wholesale. This excludes handlers, URLs, data-* secrets,
      // inline styles, custom-element state, IDs, and browser autofill values.
      let target = parent;
      if (ALLOWED.has(tag)) {
        target = output.createElement(tag);
        if (tag === 'details') target.setAttribute('open', '');
        for (const attr of ['colspan', 'rowspan']) {
          if (['td', 'th'].includes(tag) && /^[1-9]\d{0,2}$/.test(node.getAttribute(attr) || '')) target.setAttribute(attr, node.getAttribute(attr));
        }
        parent.appendChild(target);
      }
      for (const child of node.childNodes) visit(child, target, depth + 1);
    }
    for (const child of (document.body || document.documentElement).childNodes) visit(child, output.body, 0);
    const snapshot = '<!DOCTYPE html>\n' + output.documentElement.outerHTML;
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(snapshot));
    const hash = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    return {
      snapshot,
      metadata: {
        format: 'tabshotter-sanitized-dom-v1',
        captured_at_utc: capturedAt,
        // Origin only: paths can contain credentials or sensitive identifiers too.
        page_origin: location.origin,
        viewport: { width: innerWidth, height: innerHeight, device_pixel_ratio: devicePixelRatio },
        scroll: { x: scrollX, y: scrollY },
        snapshot_sha256: hash,
        sanitization: 'strict-inert-html-v1',
        removed_subtrees: removed,
        warning: 'Visible text may contain secrets. Manual review is required. Hash integrity does not prove source authenticity or capture time.'
      }
    };
  };
})();
