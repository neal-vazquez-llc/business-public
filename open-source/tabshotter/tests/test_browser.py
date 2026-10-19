"""Synthetic fixtures only. Requires Python Playwright and system Chromium."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify', ROOT / 'tools/verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)

FIXTURE = '''<!doctype html><html><head><title>TITLE_SECRET</title><style>.hidden{display:none}</style></head><body>
<h1>Live page</h1><p id="state">before</p><p>Unicode: café 日本語 🐱 &amp; &lt;hello&gt;</p>
<table><tr><td colspan="2" data-secret="ATTR_SECRET">cell</td></tr></table>
<input type="password" value="PASSWORD_SECRET"><input type="hidden" value="HIDDEN_SECRET">
<textarea>TEXTAREA_SECRET</textarea><select><option>SELECT_SECRET</option></select>
<div contenteditable>EDITABLE_SECRET</div><div hidden>HIDDEN_TEXT_SECRET</div><div class="hidden">CSS_HIDDEN_SECRET</div>
<div aria-hidden="true">ARIA_SECRET</div><div style="visibility:hidden">VISIBILITY_SECRET</div>
<a href="https://USER:PASS@leak.test/private?token=URL_SECRET#HASH_SECRET" ping="https://leak.test/ping" onclick="alert(1)">link text</a>
<iframe src="https://leak.test/frame"></iframe><img src="https://leak.test/image" onerror="alert(2)">
<script type="application/json">{"secret":"SCRIPT_SECRET"}</script>
<style>body{background:url(https://leak.test/css)}</style>
<svg><foreignObject><p>SVG_SECRET</p></foreignObject></svg><math><mtext>MATH_SECRET</mtext></math>
<template><p>TEMPLATE_SECRET</p></template><object data="https://leak.test/object"></object>
<form action="https://leak.test/submit"><p>Form label</p><button>BUTTON_SECRET</button></form>
<div data-token="DATA_SECRET" style="background:url(https://leak.test/inline)">Visible text remains</div>
<p>VISIBLE_SECRET_REQUIRES_REVIEW</p><div id="shadow"></div>
</body></html>'''

class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.route('**/*', lambda route: route.fulfill(status=200, content_type='text/html', body=FIXTURE) if route.request.url.startswith('https://fixture.test/') else route.abort())
        self.page.goto('https://fixture.test/private/path?token=LOCATION_SECRET#FRAGMENT_SECRET')
        self.page.evaluate("document.getElementById('state').textContent = 'after live mutation'; document.getElementById('shadow').attachShadow({mode:'open'}).innerHTML='<p>SHADOW_TEXT</p>'")
        self.page.add_script_tag(path=str(ROOT / 'extension/capture.js'))
        self.capture = self.page.evaluate('TabShotterCapture()')
    def tearDown(self):
        self.context.close()
    def export(self):
        self.page.add_script_tag(path=str(ROOT / 'extension/export.js'))
        return self.page.evaluate('capture => TabShotterExport(capture)', self.capture)
    def test_live_dom_and_unicode_preserved(self):
        source = self.capture['snapshot']
        self.assertIn('after live mutation', source)
        self.assertIn('café 日本語 🐱', source)
        self.assertIn('colspan="2"', source)
        self.assertNotIn('SHADOW_TEXT', source)
    def test_controls_hidden_and_attributes_removed(self):
        serialized = json.dumps(self.capture)
        for secret in ['TITLE_SECRET','ATTR_SECRET','PASSWORD_SECRET','HIDDEN_SECRET','TEXTAREA_SECRET','SELECT_SECRET','EDITABLE_SECRET','HIDDEN_TEXT_SECRET','CSS_HIDDEN_SECRET','ARIA_SECRET','VISIBILITY_SECRET','URL_SECRET','HASH_SECRET','SCRIPT_SECRET','SVG_SECRET','MATH_SECRET','TEMPLATE_SECRET','BUTTON_SECRET','DATA_SECRET','LOCATION_SECRET','FRAGMENT_SECRET']:
            self.assertNotIn(secret, serialized)
        self.assertIn('VISIBLE_SECRET_REQUIRES_REVIEW', serialized)
        self.assertNotIn('leak.test', serialized)
        self.assertEqual(self.capture['metadata']['page_origin'], 'https://fixture.test')
    def test_no_active_original_markup(self):
        source = self.capture['snapshot']
        for token in ['<script', '<style', '<img', '<iframe', '<form', '<svg', '<math', '<input', 'onclick=', 'href=', 'src=', 'data-token=']:
            self.assertNotIn(token, source)
        self.assertIn("default-src 'none'", source)
        self.assertIn("form-action 'none'", source)
    def test_hash_matches(self):
        expected = hashlib.sha256(self.capture['snapshot'].encode()).hexdigest()
        self.assertEqual(expected, self.capture['metadata']['snapshot_sha256'])
    def test_export_opens_offline_without_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'capture.html'
            path.write_text(self.export())
            replay = self.context.new_page()
            requests = []
            replay.on('request', lambda r: requests.append(r.url))
            replay.goto(path.as_uri())
            replay.wait_for_timeout(400)
            frame = replay.frames[1]
            self.assertIn('after live mutation', frame.locator('body').inner_text())
            self.assertEqual([r for r in requests if r.startswith(('http:', 'https:'))], [])
            self.assertEqual(replay.locator('script').count(), 0)
            self.assertEqual(replay.locator('iframe').get_attribute('sandbox'), '')
            self.assertTrue(verifier.verify(path)[0])
            path.write_text(path.read_text().replace('after live mutation', 'tampered mutation'))
            self.assertFalse(verifier.verify(path)[0])
    def test_csp_blocks_resources_if_inserted_in_preview(self):
        # Defense in depth: a future sanitizer regression must still meet CSP.
        self.page.set_content('<iframe sandbox="" id="preview"></iframe>')
        requests = []
        self.page.on('request', lambda r: requests.append(r.url))
        self.page.locator('#preview').evaluate('(el, html) => el.srcdoc=html', self.capture['snapshot'].replace('</body>', '<img src="https://leak.test/regression"><script>fetch("https://leak.test/js")</script><form action="https://leak.test/post"></form></body>'))
        self.page.wait_for_timeout(300)
        self.assertFalse(any('regression' in r or '/js' in r for r in requests))
    def test_limit_fails_without_partial_capture(self):
        self.page.evaluate("document.body.textContent='x'.repeat(4000001)")
        with self.assertRaisesRegex(Exception, 'exceeds the capture limit'):
            self.page.evaluate('TabShotterCapture()')
    def test_manifest_minimal_permissions(self):
        manifest = json.loads((ROOT / 'extension/manifest.json').read_text())
        self.assertEqual(manifest['permissions'], ['activeTab', 'scripting'])
        self.assertNotIn('host_permissions', manifest)
        self.assertNotIn('background', manifest)

if __name__ == '__main__':
    unittest.main(verbosity=2)
