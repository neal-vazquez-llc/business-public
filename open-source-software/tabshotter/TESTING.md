# Verification record

Staging checks on 2026-10-02:

- PASS: 10 Node built-in unit tests, including live text/table serialization, Unicode hash, excluded controls/hidden data/attributes, retained visible-secret warning, size/depth/protocol rejection, escaped static export, Python verifier match/tamper/duplicate rejection, minimal manifest permissions, review gate, discard, repeated capture reset, failure cleanup and unsupported-page feedback.
- PASS: JavaScript syntax checks for capture, export, popup and tests; Python syntax checks; manifest JSON parse; packaging smoke check.
- PASS: authoritative original source SHA-256 remains `14607dde9337a58d9cd33a326c06de9c20de967589b607591f54c4379a32fa3e`.
- NOT RUN TO COMPLETION: eight real-browser Playwright tests. Test setup could not launch Chromium. The environment rejected Chromium's local `socket()` startup with `Operation not permitted`, including a permitted escalation retry. Zero browser tests executed; this is not a browser test pass.
- NOT RUN: extension installation, actual toolbar/keyboard flow, downloads, restrictive-site behavior, popup rendering/accessibility in a real extension profile, Firefox compatibility and browser-store validation.

Unit tests use a deliberately small fake DOM and fake extension APIs. They exercise production sanitizer/export/popup code, but cannot establish browser parsing, CSP enforcement, srcdoc loading, extension API compatibility, or network isolation. The browser suite uses synthetic hostile fixtures, never private page captures. It is intended to verify live DOM updates, sanitization examples, hashing, offline replay with no HTTP(S) requests, CSP defense in depth, capture size limits and permission scope.

Do not call this security-validated, broadly browser-compatible, or ready for general release until the blocked integration and manual checks pass on the exact final source.
