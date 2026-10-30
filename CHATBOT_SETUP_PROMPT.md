# Copy-paste project setup prompt

Copy everything below the line into a coding assistant after cloning this
repository into the new project directory.

---

You are setting up this local research project from the **Research LaTeX + CDP
+ Overleaf + Zotero** template. Work only inside the current project folder.

First, read `README.md`, `TEMPLATE.md`, and `AGENTS.md`. Then inspect the
repository without changing any files until you understand its current state.

Set up the project as follows:

1. Create `.codex/config.toml` from `.codex/config.toml.example` only if it
   does not already exist. Preserve an existing local configuration instead of
   replacing it.
2. Check whether `uv` and `zotero-cli` are available. The supported client is
   `zotero-mcp-server[pdf]==0.13.2`, installed as a user-level uv tool; its
   `zotero-cli` command is the direct Zotero interface. If either is absent,
   report the exact missing prerequisite and the command
   `uv tool install "zotero-mcp-server[pdf]==0.13.2"`. Do not download or
   install `uv` or the tool unless I explicitly authorize package installation.
   If I do authorize it, install uv with its official installer for the current
   operating system, ensure the newly installed uv directory is on `PATH` in
   this command environment, then run that `uv tool install` command. Verify
   only `zotero-cli --help` and command availability; do not configure a Zotero
   MCP server or create credentials.
   If `zotero-cli` is present, run `zotero-cli config` only to determine whether
   it is usable. Summarize only that result; never print, copy, save, or expose
   any API key, token, cookie, library data, or absolute personal file path.
3. Treat `zotero-cli` as the direct Zotero integration. Do not add a Zotero
   MCP server to configuration. For a requested write/export, first check that
   the same command environment can reach Zotero's Local API; do not install
   software, alter account settings, or request authorization unless I
   explicitly request that.
4. Check whether Google Chrome is installed and whether port 9222 is free. Do
   not launch Chrome, log into Overleaf, connect to a browser, or create an
   Overleaf project unless I explicitly ask. If I later ask to use Overleaf,
   use `.agents/scripts/start-research-chrome.sh` on macOS,
   `.agents/scripts/start-research-chrome-linux.sh` on Linux, or
   `.agents/scripts/start-research-chrome.ps1` on Windows so the normal Chrome profile
   is never modified. If automatic browser detection or the chosen launcher
   fails because its install location is unknown, tell me clearly that the
   browser was not found and ask me for the full executable path. Rerun with
   `--chrome-path` on Linux or `-ChromePath` on Windows. Do not guess a
   nonstandard path or ask for a browser profile, login, or password.
5. Check that the Overleaf CDP skill exists at
   `.agents/skills/overleaf-cdp/SKILL.md` and that the repository excludes
   local configuration, credentials, browser profiles, and TeX build output.
   Also verify `.agents/skills/zotero-cli/scripts/sync_zotero_bibliography.py`,
   `.agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py`, and
   `.agents/skills/zotero-cli/reference.md` are present. If Python is
   available, run `python3 .agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py`; this test
   uses a temporary localhost-only fake API and never accesses the user's
   Zotero library or manuscript files.
6. Report a short readiness checklist: ready items, missing prerequisites, and
   any local action I must take. Do not make external changes (including GitHub
   repository creation, package installation, browser login, Zotero writes, or
   Overleaf edits) without my explicit approval.

For future work in this project, follow `AGENTS.md`. Prefer `zotero-cli` for
normal Zotero tasks, and use visible Chrome/CDP only for web research and
authorized Overleaf work. For every Overleaf source edit, read the target,
make a bounded change, read it back, compile, and inspect both the PDF and the
compile log.

