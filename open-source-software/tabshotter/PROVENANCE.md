# Capture engine provenance

This implementation is a security-focused derivative of the author's recovered `snapshot-tab.js` browser script, supplied as the authoritative original.

Original SHA-256: `14607dde9337a58d9cd33a326c06de9c20de967589b607591f54c4379a32fa3e`

The original was inspected without modification. Its central pipeline is retained: read the current tab's live DOM, serialize HTML, record capture metadata, compute SHA-256, and package a standalone HTML capture. The new format deliberately hashes only the minimized, sanitized DOM. It does not retain an unsanitized snapshot, raw page URL, referrer, user agent, form values, original scripts, or network resources.

The original's sandbox-only claim of network isolation was incorrect. This derivative uses a strict HTML/attribute allowlist, explicit restrictive CSP, and an empty iframe sandbox in combination. Original source is not shipped as an executable alternative.

The staged package carries the MIT License selected for this release candidate. Publication remains gated on confirming rights to release the derivative and completing the browser/security review. This directory must not be advertised as a validated release until those gates are complete.
