---
name: visible-research-cdp
description: Search public literature, source pages, abstracts, or papers through visible Chrome DevTools Protocol. Use when research may encounter a site verification the user must complete.
---

# Visible Research CDP

Use visible Chrome/CDP for public literature searches. Reuse the dedicated
research-browser tab or start the isolated research browser; preserve the
user's normal Chrome profile and tabs.

When a browser must be started, use
`.agents/scripts/start-research-chrome.sh` on macOS,
`.agents/scripts/start-research-chrome-linux.sh` on Linux, or
`.agents/scripts/start-research-chrome.ps1` on Windows. If browser discovery
fails, ask the user for the executable path and pass it with `--chrome-path`
on Linux or `-ChromePath` on Windows.

1. Search and inspect sources in the visible browser, including abstracts and
   publicly available papers.
2. When a paper is relevant, read `.agents/skills/zotero-cli/SKILL.md` and
   save it to Zotero after its write authorization is in place.
3. Capture the source details needed to support the requested claim.
4. If a site requires human verification, leave its visible tab open and ask
   the user to complete it. Continue after the user confirms access.
5. Close only tabs created for this task when the research is complete.
