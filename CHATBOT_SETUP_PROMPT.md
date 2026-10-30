# Copy-paste bootstrap prompt

Use this prompt when Codex or OpenCode has been opened in a **new, empty
folder**. Copy everything below the line into that assistant's chat. It is a
bootstrap prompt: the repository has not yet been cloned, no local tools are
assumed to be installed, and nobody is assumed to be signed in to Zotero or
Overleaf.

---

Set up this empty folder as a local research-manuscript project using the
public `zotero-overleaf-research-agent` template.

This prompt authorizes you to clone the public template repository into the
current folder; create and edit files inside this project; download and install
the user-level `uv` tool and the user-level Zotero CLI dependency specified
below; and run the supplied local verification test. Do not make other external
changes without asking first. In particular, do not create or publish a GitHub
repository, push commits, create an Overleaf project, sign in to any service,
open or modify a normal browser profile, authorize a Zotero write, access a
Zotero library, or ask for credentials, cookies, passwords, API keys, or a
browser profile.

Work through this procedure and report the final checklist.

1. **Protect the target folder before cloning.** Confirm the current directory
   is empty, apart from harmless editor or OS placeholders such as `.DS_Store`,
   `.gitkeep`, or workspace metadata created by the coding tool. If it contains
   a real project, source files, a Git repository, or anything whose ownership
   is unclear, stop and ask me to choose a different empty folder; never merge,
   delete, overwrite, or clone into it. Check that `git` is available. If it is
   not, explain that Git must be installed by me (or ask whether I want help
   installing it) and stop without attempting a clone.

2. **Fetch the template.** Clone
   `https://github.com/jianlins/zotero-overleaf-research-agent.git` into the
   current directory, so the template files are at the project root rather than
   nested inside a second folder. Do not use a personal access token or any
   credential. If public network access is unavailable, report the exact failed
   command and the next local action needed; do not substitute an unverified
   mirror or fabricate files.

3. **Read the project policy before configuring it.** After a successful
   clone, read `README.md`, `AGENTS.md`, `WORKSPACE_LAYOUT.md`, and
   `.agents/agents/zotero-overleaf-research-agent/AGENT.md`. Treat their
   instructions as project policy for all later work. Inspect the worktree and
   preserve the cloned files; do not change the template's workflow or install
   an MCP server for Zotero. Do not install the optional Docling PDF-to-Markdown
   dependency during bootstrap: it requires Python 3.10+ and may download local
   model artifacts on first use. Install it only when I explicitly request PDF
   conversion, using the command documented in `WORKSPACE_LAYOUT.md`.

4. **Create the local Codex configuration safely.** If
   `.codex/config.toml` does not exist, copy it from
   `.codex/config.toml.example`. If it already exists, preserve it and only
   report that fact. This configuration is useful to Codex; OpenCode may simply
   retain it as project-local documentation and should not invent an OpenCode
   configuration format. Do not run `npx`, start a browser, or connect to a
   Chrome DevTools endpoint as part of this setup.

5. **Install and verify the direct Zotero client.** The supported client is a
   user-level uv tool:

   ```sh
   uv tool install "zotero-mcp-server[pdf]==0.13.2"
   ```

   First check whether `uv` and `zotero-cli` are already available. If `uv` is
   missing, install it only using uv's official installer for the detected
   operating system, then ensure its install directory is available in the
   current command environment. Install the supported tool if `zotero-cli` is
   missing; if it is present, do not replace or upgrade it unless needed to
   meet the pinned version. Verify command availability with `zotero-cli --help`.
   You may run `zotero-cli config` only to determine whether the client is
   usable. Summarize its status without printing, storing, copying, or exposing
   API keys, tokens, cookies, library contents, or absolute personal paths.
   Do not run `zotero-mcp authorize-local`, do not configure a Zotero MCP
   server, and do not make a read or write request to the Zotero library.

6. **Verify the repository-owned bibliography guard.** Confirm that these
   files exist:

   - `.agents/skills/overleaf-cdp/SKILL.md`
   - `.agents/skills/zotero-cli/SKILL.md`
   - `.agents/skills/zotero-cli/reference.md`
   - `.agents/skills/zotero-cli/scripts/sync_zotero_bibliography.py`
   - `.agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py`
   - `.agents/requirements-pdf-extraction.txt`
   - `.agents/scripts/extract_pdf_to_markdown.py`

   If `python3` is available, run:

   ```sh
   python3 .agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py
   ```

   This test must use only its temporary localhost fake API and must not access
   Zotero data or manuscript files. Do not install Docling or run the PDF
   converter during bootstrap: its optional dependency may download local model
   artifacts on first use. If Python is absent, report it as a missing
   prerequisite rather than installing it automatically.

7. **Leave accounts and live browser work for an explicit later request.** You
   may check whether Google Chrome is installed and whether port 9222 is free,
   but do not launch Chrome or log in. If I later request Overleaf work, use
   the supplied OS-specific launcher in `.agents/scripts/`, which creates an
   isolated task-only profile. If its browser detection fails, ask me for the
   full browser executable path; never ask for a profile, login, or password.
   A separate explicit request is required before creating an Overleaf project,
   signing in, or editing a remote project.

8. **Finish with a concise readiness report.** State: the template revision
   cloned; whether `.codex/config.toml` was created or preserved; the status of
   Git, uv, `zotero-cli`, Python, the bibliography-guard test, Chrome, and port
   9222; and the exact user action still required for any missing prerequisite.
   Also state that Zotero and Overleaf remain unconnected until I explicitly
   request and personally complete their respective authorization or login.

For all future work in this project, follow `AGENTS.md`. Prefer `zotero-cli`
for normal Zotero tasks, use visible Chrome/CDP only for public web research
and authorized Overleaf work, and keep every externally visible claim
traceable to a source. For an Overleaf source edit, read the target, make a
bounded change, read it back, compile, and inspect both the PDF and compile
log.

