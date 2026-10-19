/* Pure packaging helpers; no original page code executes in exported artifacts. */
(() => {
  'use strict';
  const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
  const policy = "default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; frame-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'";
  globalThis.TabShotterExport = ({snapshot, metadata}) => `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${escape(policy)}"><meta name="referrer" content="no-referrer"><title>TabShotterUwU capture</title><style>body{font:16px system-ui;margin:2rem;line-height:1.5}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f4f4;padding:1rem}iframe{width:100%;height:65vh;border:1px solid #999}</style></head><body>
<h1>TabShotterUwU</h1><p>Sanitized live DOM capture. Original scripts, styling, links and remote resources are removed. Page text may still be sensitive.</p>
<p>SHA-256 checks only the embedded sanitized DOM. It does not authenticate the website, timestamp or metadata. Use the included verify.py tool for verification.</p>
<h2>Capture metadata</h2><pre id="capture-metadata">${escape(JSON.stringify(metadata, null, 2))}</pre>
<h2>Inert preview</h2><iframe title="Sanitized captured page" sandbox="" referrerpolicy="no-referrer" srcdoc="${escape(snapshot)}"></iframe>
<details><summary>Sanitized HTML source</summary><pre id="snapshot-source">${escape(snapshot)}</pre></details>
</body></html>`;
})();
