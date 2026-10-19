# Quiet release checklist

- [ ] Confirm the staged MIT License and rights to release the derivative source.
- [ ] Run all Node tests and JavaScript/Python syntax checks on final files.
- [ ] Run Playwright browser suite with zero failures; review resource-request log and srcdoc rendering.
- [ ] Load unpacked in desktop Chromium; test toolbar, shortcut, initial capture, repeat capture, review gate, save, discard, popup close/reopen and errors on restricted pages.
- [ ] Open downloaded HTML offline. Confirm expected inert text/structure and no HTTP(S) requests in DevTools. Recheck hostile fixtures, Unicode, long pages and tamper verification.
- [ ] Check narrow popup view, keyboard-only focus flow, source review and screen-reader status announcements.
- [ ] Confirm original/private documents, real captures, identities, credentials and browser profiles are absent from the release package.
- [ ] Confirm README candidly describes fidelity losses, remaining sensitive text and unsigned integrity limitations.
- [ ] If promising Firefox support, validate a separate Firefox MV3 package and all corresponding manual/security checks first.
- [ ] Owner approves public repository placement and exact publication action. No launch campaign or paid service is implied.
- [ ] Choose a private security-report contact. Add store-required policies/identity only if an actual store submission is planned.

Local staging does not satisfy these release gates by itself.
