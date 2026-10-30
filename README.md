# zotero-overleaf-research-agent

A credential-free research-manuscript workflow for projects that use LaTeX, an
Overleaf project in visible Chrome, and a local Zotero library.

It intentionally versions the workflow, not private state: no API keys,
browser cookies, Zotero library data, or machine-specific Chrome ports belong
in this repository.

## Why use this alongside Deep Research?

General-purpose Deep Research is useful for quickly discovering and
synthesizing public material. This workflow is designed for the next stage:
building a reviewable manuscript from sources that a researcher has actually
examined. It keeps a person in control at the points where access,
provenance, and manuscript correctness matter.

- **Access through your own visible browser.** A signed-in local browser can
  reach material available through an institutional VPN, library proxy, or
  other access that a hosted research service cannot use. You can see which
  sites and documents are opened, complete a CAPTCHA or other human
  verification yourself, and decide what the assistant may read. Credentials
  and browser profiles remain local.
- **A durable, searchable source record.** Confirmed papers, metadata, PDFs,
  notes, and tags can be organized in Zotero rather than living only in a
  chat transcript. That library remains useful for later manual or automated
  analysis, and gives each manuscript reference an inspectable source record.
- **Citation handling that survives revision.** Zotero is the bibliographic
  source of truth, while the bibliography guard preserves citation keys
  already used by the manuscript and dry-runs merges before writing them.
  LaTeX/BibLaTeX regenerates citation order and formatting when the document
  changes, avoiding the fragile manual renumbering common in Word-based
  workflows. This improves traceability and reduces avoidable reference
  errors; it does not replace checking every cited claim.
- **Live, collaborative manuscript production.** Overleaf makes the LaTeX
  source available for direct collaboration and discussion with coauthors.
  The editing workflow reads changes back, compiles the project, and checks
  the resulting PDF and log, so a citation or formatting change is verified
  in the document people will actually review.
- **An auditable handoff.** Versioned source, notes, plans, and a concise
  research log make it possible for a coauthor or another agent to retrace
  searches, decisions, and evidence instead of relying on a one-off generated
  answer.

The goal is not to replace Deep Research, but to pair broad discovery with a
transparent, researcher-controlled path from source access to a collaborative,
compile-verified manuscript.

This template does not bundle a Deep Research skill. You may add an
open-source Deep Research skill set for discovery, search planning, or
literature synthesis, then use this workflow to inspect the selected sources
in the visible browser, save confirmed records to Zotero, and incorporate
citations into Overleaf. Treat externally generated references as leads to
verify, rather than importing them into a manuscript unchecked.

### Limits and required human checks

This workflow makes a *fabricated* reference much less likely when every
manuscript item is selected from a Zotero record that you have inspected: the
bibliography is generated from those records, rather than invented by a model
while drafting. It is not a guarantee that every reference or claim is
correct. Before relying on a citation, check the source landing page, DOI or
other persistent identifier, authorship, publication version, and (where it
matters) the full text. Also check that the cited source actually supports the
nearby claim.

Possible failures still include an incorrect or incomplete metadata import, a
confusion between similarly titled papers or preprint and final versions, a
real paper cited for a claim it does not support, or a manually edited `.bib`
file that bypasses the guard. The model and its instructions still matter:
stronger models and explicit source-checking prompts can reduce these errors,
but neither removes the need for human judgment. Keep the visible-browser,
Zotero-confirmation, and compile-review checkpoints in the workflow, and
report or correct any uncertain source before sharing the manuscript.

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
- `.agents/requirements-pdf-extraction.txt`: the Docling dependency declaration
  used by the PDF converter.
- `CHATBOT_SETUP_PROMPT.md`: a platform-neutral setup prompt to paste into
  Codex or OpenCode after creating a project from this template.

## Use it

Choose the starting path that fits your project:

1. **Creating a GitHub-backed project (recommended):** on this repository's
   GitHub page, select **Use this template** and create your new repository.
   This copies the template files into your repository without making this
   template's development history your project history. Clone *your new
   repository* afterward if you want a local checkout.
2. **Starting without Git history:** use GitHub's **Download ZIP** option,
   extract it, and open the extracted folder in your coding assistant. This is
   the cleanest option when you do not need a repository yet.
3. **Using Git directly:** only when a local checkout of this template itself
   is useful, make it shallow so you do not fetch its full history:

```bash
git clone --depth 1 https://github.com/jianlins/zotero-overleaf-research-agent.git
cd zotero-overleaf-research-agent
```

For an automated local bootstrap, open a new empty folder in Codex or OpenCode
and paste [`CHATBOT_SETUP_PROMPT.md`](CHATBOT_SETUP_PROMPT.md). It first asks
whether the user has a signed-in GitHub account: use **Use this template** only
when they do; otherwise use the ZIP. The ZIP route downloads and safely
flattens the template archive; the repository route shallow-clones the new
repository after collecting its clone URL. It performs the local setup and
explains any machine-specific prerequisite that still needs you; it never
creates or publishes a GitHub repository.

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
It preserves reading order and tables where possible. The configured converter
runs locally; it does not call an LLM or a paid model API.

```bash
uv run --python 3.12 \
  --with-requirements .agents/requirements-pdf-extraction.txt \
  python .agents/scripts/extract_pdf_to_markdown.py \
  --input references/pdf/ZOTEROITEMKEY.pdf
```

It writes `references/markdown/ZOTEROITEMKEY.md` by default, refuses to
overwrite it without `--force`, and reports when a scanned PDF must be OCRed
first. OCR is opt-in through `--ocr` after local Docling OCR setup. Docling
requires Python 3.10+; `uv` supplies Python 3.12 in the command above. See
[`WORKSPACE_LAYOUT.md`](WORKSPACE_LAYOUT.md) for the full contract and OCR
model-license review requirement.

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

### Install local tools

After installing [uv](https://docs.astral.sh/uv/), install the Zotero CLI and
the converter dependency together with one command:

```bash
uv tool install "zotero-mcp-server[pdf]==0.13.2" \
  --with-requirements .agents/requirements-pdf-extraction.txt
zotero-cli config
python3 .agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py
```

This installs the free, open-source Docling package alongside the CLI. PDF
conversion remains local and does not incur LLM or model-API charges. The test
uses only a temporary localhost fake API and does not inspect Zotero data. A
setup assistant should report a missing `uv` and request permission before
installing it or these packages.

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

