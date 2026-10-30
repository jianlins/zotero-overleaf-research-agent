# zotero-overleaf-research-agent

A credential-free research-manuscript workflow for projects that use LaTeX, an
Overleaf project in visible Chrome, and a local Zotero library.

It intentionally versions the workflow, not private state: no API keys,
browser cookies, Zotero library data, or machine-specific Chrome ports belong
in this repository.

## What it provides

- `.agents/agents/zotero-overleaf-research-agent/AGENT.md`: the shared
  research-manuscript Agent definition, with Codex, Claude, Gemini, and
  OpenCode entry points.
- `AGENTS.md`: project instructions for research, Overleaf, and Zotero work.
- `.agents/skills/visible-research-cdp`: visible Chrome/CDP workflow for
  public literature searches and user-completed site verification.
- `.agents/skills/zotero-cli`: saves each confirmed relevant paper to Zotero
  before citation or bibliography work.
- `.agents/skills/zotero-cli/scripts/sync_zotero_bibliography.py`: merges Local API BibLaTeX exports
  without changing established citation keys; its self-contained test ships
  alongside it.
- `.agents/skills/overleaf-cdp`: a bounded, compile-verified Overleaf editing
  workflow.
- `.codex/config.toml.example`: Chrome DevTools MCP configuration, with no
  credentials.
- Direct Zotero CLI guidance: the Zotero workflow does not require an MCP
  server configuration.
- `.agents/scripts/start-research-chrome.sh`, `-linux.sh`, `.ps1`, and `.cmd`:
  separate Chrome profiles for macOS, Linux, and Windows CDP work.
- `.agents/requirements-pdf-extraction.txt`: the optional, project-scoped
  Docling dependency declaration used by the PDF converter.
- `CHATBOT_SETUP_PROMPT.md`: a platform-neutral bootstrap prompt to paste into
  Codex or OpenCode from a new, empty folder.

## Use it

```bash
git clone https://github.com/jianlins/zotero-overleaf-research-agent.git
cd zotero-overleaf-research-agent
```

For a new, empty folder, paste the contents of
[`CHATBOT_SETUP_PROMPT.md`](CHATBOT_SETUP_PROMPT.md) into Codex or OpenCode.
It will safely clone this template, perform the local setup, and explain any
machine-specific prerequisite that still needs you.

### Where your work belongs

Treat `.agents/` as internal, versioned automation: do not move or edit it
unless you are maintaining the template. Put your manuscript and bibliography
at the project root, research PDFs and extracted Markdown in `references/`,
and personal working notes in `notes/` (create it when needed). This keeps
your research material separate from the template's tooling.

[`WORKSPACE_LAYOUT.md`](WORKSPACE_LAYOUT.md) defines the full directory
contract, including plans, handoffs, the research log, and which artifacts stay
local rather than entering Git.

### Extracting PDF text

The template includes a controlled PDF-to-Markdown command based on Docling.
It preserves reading order and tables where possible, and never delegates text
reconstruction to an LLM:

```bash
uv run --python 3.12 \
  --with-requirements .agents/requirements-pdf-extraction.txt \
  python .agents/scripts/extract_pdf_to_markdown.py \
  --input references/pdf/ZOTEROITEMKEY.pdf
```

It writes `references/markdown/ZOTEROITEMKEY.md` by default, refuses to
overwrite it without `--force`, and reports when a scanned PDF must be OCRed
first. OCR is opt-in through `--ocr` after local Docling OCR setup. Docling
requires Python 3.10+; `uv` supplies Python 3.12 in the command above. Its
dependency is declared in
`.agents/requirements-pdf-extraction.txt`; see
[`WORKSPACE_LAYOUT.md`](WORKSPACE_LAYOUT.md) for the full contract and model
license review requirement.

### Updating the manuscript bibliography

The canonical BibLaTeX file is `references.bib` at the project root. The
Zotero guard reads the local Zotero API, dry-runs a merge, and writes only the
local bibliography and its ignored key lock after `--apply`; it does not modify
Zotero or manage PDF files. The exact command and review gate are in
[`WORKSPACE_LAYOUT.md`](WORKSPACE_LAYOUT.md).

### Starting the research browser

Use the launcher for your operating system; each creates an isolated profile
and uses CDP port 9222 by default.

```bash
# macOS
zsh .agents/scripts/start-research-chrome.sh
```

```bash
# Linux
bash .agents/scripts/start-research-chrome-linux.sh
```

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\.agents\scripts\start-research-chrome.ps1

# Or from Command Prompt
.\.agents\scripts\start-research-chrome.cmd
```

The Linux and Windows launchers accept `--port PORT` and `-Port PORT`,
respectively. The macOS launcher accepts `--port PORT`. When using a port
other than 9222, make the same change to the browser URL in the local,
untracked `.codex/config.toml`. Codex starts the CDP bridge from that
configuration with `npx`, so Node.js/npm must be available when that bridge is
used; it downloads `chrome-devtools-mcp` on first use.

The Windows launcher looks for `chrome.exe` on `PATH` and in Chrome's standard
per-machine and per-user install locations. The Linux launcher looks for
`google-chrome`, `google-chrome-stable`, `chromium`, or `chromium-browser` on
`PATH`. If either launcher cannot find a browser, give the chatbot its full
executable path; it can pass it safely with Windows `-ChromePath` or Linux
`--chrome-path`. Do not give it browser-profile, login, or password details.

## Publishing this folder

Publish the contents of this directory as the root of a dedicated GitHub
repository. Before publishing, select a license deliberately; none is included
because licensing is a project-owner decision. Keep `.codex/config.toml` out
of Git even when it currently contains no secret, so local port or command
customizations do not become repository policy.

## Zotero design

This template uses `zotero-cli` directly rather than registering a Zotero MCP
server. The CLI and its project skill originate from the third-party
`zotero-mcp-server` project, but normal use is a direct local command path:

```text
assistant → zotero-cli → Zotero Desktop Local API → Zotero library
```

### Install the local client

The repository includes the project-owned bibliography guard, but it does not
vendor a machine-specific Python environment or the `zotero-cli` launcher.
Install the supported client once with uv after installing uv itself:

```bash
uv tool install "zotero-mcp-server[pdf]==0.13.2"
zotero-cli config
python3 .agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py
```

The test opens only a temporary localhost fake API and does not inspect the
user's Zotero data. A setup assistant should report a missing `uv` or client
and wait for explicit permission before installing either package.

That is more portable across local coding assistants and avoids loading MCP
tools when they are unnecessary. A local write/export requires the same command
environment to reach Zotero's localhost API. If a sandbox blocks localhost,
the CLI can read local index data yet fail writes or bibliography rendering;
run the command in a permitted local context instead. `zotero-mcp authorize-local`
may be used solely to grant the package local write access—it
does not require adding an MCP server to project configuration.

### User confirmation for Zotero writes

The first direct CLI write may require local authorization. After an assistant
or user runs:

```bash
zotero-mcp authorize-local
```

Zotero Desktop displays its own authorization dialog. The user must personally
review and select the option; an assistant must not assume, simulate, or bypass
that confirmation.

- **Allow** grants a single-use key. It expires with the authorization command,
  so it normally cannot authorize a later, separate `zotero-cli` command.
- **Always Allow** grants the package a reusable local write key for future CLI
  commands. Select it only after deciding that this installed package should be
  allowed to modify the local Zotero library.
- **Deny** leaves the library read-only to this tool.

This is a local Zotero API permission, not a request to configure or start a
Zotero MCP server. Until the user has completed the appropriate authorization,
use read-only CLI operations or update `references.bib` manually.

## Bibliography guard

Use `.agents/skills/zotero-cli/scripts/sync_zotero_bibliography.py` for a dry-run before applying a
Zotero collection update to an established BibLaTeX bibliography. Store its
machine-local lock in `.zotero/citation-key-lock.json`; do not commit it, as it
contains a Zotero database identifier and item-key mapping.

