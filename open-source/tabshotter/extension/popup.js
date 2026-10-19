'use strict';
const api = globalThis.browser || globalThis.chrome;
const $ = id => document.getElementById(id);
let capture = null;
function discard() {
  capture = null;
  $('review').hidden = true;
  $('approved').checked = false;
  $('save').disabled = true;
  $('preview').removeAttribute('srcdoc');
  $('metadata').textContent = '';
  $('source').value = '';
}
$('capture').addEventListener('click', async () => {
  discard();
  $('capture').disabled = true;
  $('status').textContent = 'Capturing sanitized live DOM…';
  try {
    const [tab] = await api.tabs.query({active: true, currentWindow: true});
    if (!tab?.id || !/^https?:\/\//.test(tab.url || '')) throw new Error('Open an ordinary HTTP(S) webpage first. Browser-internal pages and local files are not supported.');
    await api.scripting.executeScript({target: {tabId: tab.id}, files: ['capture.js']});
    const result = await api.scripting.executeScript({target: {tabId: tab.id}, func: () => globalThis.TabShotterCapture()});
    if (!result[0]?.result) throw new Error('The page changed or capture was blocked. Try again.');
    capture = result[0].result;
    $('metadata').textContent = JSON.stringify(capture.metadata, null, 2);
    $('source').value = capture.snapshot;
    $('preview').srcdoc = capture.snapshot;
    $('review').hidden = false;
    $('status').textContent = 'Review required. Nothing has been saved.';
  } catch (error) {
    discard();
    $('status').textContent = `Capture failed: ${error.message}`;
  } finally { $('capture').disabled = false; }
});
$('approved').addEventListener('change', () => { $('save').disabled = !capture || !$('approved').checked; });
$('discard').addEventListener('click', () => {discard(); $('status').textContent = 'Capture discarded.';});
$('save').addEventListener('click', () => {
  if (!capture || !$('approved').checked) return;
  const url = URL.createObjectURL(new Blob([TabShotterExport(capture)], {type: 'text/html;charset=utf-8'}));
  const a = document.createElement('a');
  a.href = url;
  a.download = `tabshotter-${capture.metadata.captured_at_utc.replace(/[:.]/g, '-')}.html`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
  $('status').textContent = 'Download requested. Check your browser downloads.';
});
