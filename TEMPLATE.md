# Research-LaTeX + CDP + Overleaf + Zotero starter

Copy this directory into a new project, then complete the following once.

For a guided local setup, paste the contents of `CHATBOT_SETUP_PROMPT.md` into
Codex, Copilot, or another coding assistant after copying the directory.

1. Copy `.codex/config.toml.example` to `.codex/config.toml`.
2. Install the Zotero CLI once, as a user-level uv tool, then confirm
   `zotero-cli config` succeeds:

   ```bash
   uv tool install "zotero-mcp-server[pdf]==0.13.2"
   zotero-cli config
   ```

   Install `uv` first if it is not already available. Zotero work uses direct
   CLI calls; the template does not register a Zotero MCP server. The template
   deliberately contains no API key, login data, or copied local virtual
   environment.
3. Start a dedicated research browser, then sign in to Overleaf in that
   isolated browser if live editing is required:
   - macOS: `zsh .agents/scripts/start-research-chrome.sh`
   - Linux: `bash .agents/scripts/start-research-chrome-linux.sh`
   - Windows PowerShell:
     `powershell -ExecutionPolicy Bypass -File .\.agents\scripts\start-research-chrome.ps1`
   - Windows Command Prompt: `.agents\scripts\start-research-chrome.cmd`

   The CDP configuration expects port 9222. If the port is busy, choose
   another port in both places. If the Windows or Linux launcher cannot find a
   browser, provide the chatbot its full executable path; it will rerun with
   Windows `-ChromePath '<path-to-chrome.exe>'` or Linux
   `--chrome-path '<path-to-browser>'`.
4. Verify the included bibliography guard before using it:

   ```bash
   python3 .agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py
   ```

   The test uses a temporary localhost-only fake Zotero API; it does not read
   or modify your Zotero library. Add your manuscript, `references.bib`, and a
   `references/RESEARCH_LOG.md`.

## Design choices

This is a project scaffold, not an Artifact Template. Artifact Templates are
for a document, spreadsheet, presentation, image, email, Slack message, or
Site reference; they are not designed to carry runtime integrations. Keeping
the scaffold in version control makes its behavior inspectable and lets each
new project inherit it with a normal directory copy or a repository-template
action.

The browser connection, Overleaf session, and Zotero authorization remain
machine-local. They cannot safely be copied: CDP ports are temporary, while
cookies and API credentials are private and commonly expire. Only the stable
workflow policy and credential-free setup are templated here.

