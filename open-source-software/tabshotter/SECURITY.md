# Security model

Treat the source page as hostile and the resulting captured text as potentially private. The source page is never copied wholesale into a replay document. An allowlist reconstructs a new HTML document from supported text/structure. Unknown ordinary HTML containers are unwrapped; active and foreign-namespace subtrees are dropped. Original attributes are not copied except bounded numeric `colspan`/`rowspan`; details are deliberately opened for review. Editable/control subtrees and hidden subtrees are dropped.

Replay has three independent protections: removal of network/executable markup, an early deny-by-default CSP in the captured document, and an empty sandbox on the wrapper's iframe. The wrapper contains no scripts. The wrapper permits only its inline presentation CSS and its own srcdoc frame. No source CSS, remote URL, link navigation, form action or script should survive reconstruction. Sandbox alone is insufficient for network isolation.

The preview/metadata/source must be reviewed before a download is requested. This is a user acknowledgment, not automated certification. Captures remain in popup memory until discarded or the popup closes. Downloaded artifacts become ordinary local files under the user's control. Operating-system/browser crash dumps, swap and download history are outside this tool's retention model.

Origin, timestamps and ordinary visible text may identify a person or reveal secrets. This implementation intentionally makes no comprehensive secret detection or legal-evidence claim. The SHA-256 covers sanitized source only and is not signed or independently timestamped. It does not authenticate the preview, metadata, origin or creator.

The extension requests only `activeTab` and `scripting`. It has no persistent background script, host grants, storage permission, remote service, analytics, update fetcher, external dependencies, or upload path. The browser itself can have independent network activity.

Before release, run the browser security suite and manual extension acceptance checks. Report security issues privately to the project owner using an owner-approved contact once selected; do not post captured private pages in public issues. No contact address is invented here.
