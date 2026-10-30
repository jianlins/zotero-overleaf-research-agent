# Copy-paste bootstrap prompt

Open Codex or OpenCode in a new, empty project folder and paste the complete
prompt below. The assistant will ask whether to start from the template ZIP or
from a repository created with **Use this template**.

---

Set up the current folder as a local research-manuscript project based on the
public `zotero-overleaf-research-agent` template.

Before you change anything, ask me exactly this question: “Do you have a
GitHub account and are you signed in? If yes, you can create a repository with
**Use this template**; otherwise, choose the template ZIP. Which would you
like to use?” Do not download, clone, or otherwise bootstrap until I answer.

Use the GitHub repository option only if I confirm that I have a GitHub account
and am signed in. If I choose that option, ask for its clone URL before doing
anything else. The URL must be for my newly created repository, not this
template repository. If I do not have an account, am not signed in, or choose
ZIP, use the public template archive at
`https://github.com/jianlins/zotero-overleaf-research-agent/archive/refs/heads/main.zip`.

This prompt authorizes you to download the public ZIP or clone that supplied
public repository, create and edit files inside this project, install the
user-level `uv` tool and the user-level Zotero CLI and Docling dependencies
specified below, and run the supplied local verification test. Do not make
other external changes without asking first. In particular, do not create or
publish a GitHub repository, push commits, create an Overleaf project, sign in
to any service, open or modify a normal browser profile, authorize a Zotero
write, access a Zotero library, or ask for credentials, cookies, passwords,
API keys, or a browser profile.

Work through this procedure and report the final checklist.

1. **Protect the target folder.** Before downloading or cloning, confirm that
   the current directory is empty apart from harmless editor or OS placeholders
   (for example `.DS_Store`), the downloaded ZIP itself, and temporary files
   you created for this bootstrap. If it contains a real project, source files,
   a Git repository, or anything whose ownership is unclear, stop and ask me
   to choose a different empty folder. Never merge, delete, or overwrite such
   files.

2. **Fetch the selected starting point.**

   - If I chose the GitHub repository option, confirm that the clone URL is for
     my newly created GitHub repository, then run
     `git clone --depth 1 REPOSITORY_URL .` so its files land at the current
     project root. Do not clone the public template repository instead, and do
     not use credentials or a personal access token.
   - If I chose ZIP, download the public ZIP into a temporary location, extract
     it there, and confirm it contains exactly one extracted top-level template
     directory. Move that directory's contents, including
     dotfiles, into the current folder without overwriting anything. Only after
     confirming the files are present at the project root, remove the temporary
     ZIP and the now-empty extracted wrapper directory. Do not leave the
     project nested under `zotero-overleaf-research-agent-*`.

   If `git` is unavailable for the GitHub repository route, report that Git must
   be installed by me (or ask whether I want help installing it) and stop. If
   public network access is unavailable, report the exact failed command and
   the next local action needed; do not substitute an unverified mirror or
   fabricate files.

3. **Confirm the result and read policy.** Confirm `README.md`, `AGENTS.md`,
   `WORKSPACE_LAYOUT.md`, and `.agents/` are now present. If any are missing,
   stop and report the failed bootstrap check. Then read `README.md`,
   `AGENTS.md`, `WORKSPACE_LAYOUT.md`, and
   `.agents/agents/zotero-overleaf-research-agent/AGENT.md`. Treat their
   instructions as project policy for all later work. Preserve the cloned Git
   configuration when using the GitHub repository route; do not initialize a new
   repository for the ZIP route, alter the template workflow, or configure a
   Zotero MCP server.

4. **Create local Codex configuration safely.** If `.codex/config.toml` does
   not exist, copy it from `.codex/config.toml.example`. If it already exists,
   preserve it and only report that fact. This configuration is useful to
   Codex; OpenCode may retain it as project-local documentation and should not
   invent an OpenCode configuration format. Do not run `npx`, start a browser,
   or connect to a Chrome DevTools endpoint as part of this setup.

5. **Install and verify local research tools.** Install the supported
   user-level Zotero CLI and the project-declared Docling dependency together:

   ```sh
   uv tool install "zotero-mcp-server[pdf]==0.13.2" \
     --with-requirements .agents/requirements-pdf-extraction.txt
   ```

   Install `uv` with its official installer if needed, then run the command
   above. Verify with `zotero-cli --help` and `zotero-cli config`. Keep all
   returned secrets and library data private. Do not authorize or access
   Zotero, or configure a Zotero MCP server.

6. **Verify the bibliography guard.** Confirm that
   `.agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py` and
   `.agents/scripts/extract_pdf_to_markdown.py` exist.

   If `python3` is available, run:

   ```sh
   python3 .agents/skills/zotero-cli/scripts/test_sync_zotero_bibliography.py
   ```

   If Python is absent, report it as a missing prerequisite; do not install it.

7. **Leave live services disconnected.** You may check Chrome and port 9222,
   but do not launch Chrome or log in. For a later Overleaf request, use the
   OS-specific launcher in `.agents/scripts/`; if it cannot find Chrome, ask
   for its executable path only.

8. **Report readiness.** Report the selected bootstrap method; the Git
   revision and remote (or that the ZIP route intentionally has no Git
   checkout); whether configuration was created or preserved; the status of
   Git, uv, `zotero-cli`, Python, the test, Chrome, and port 9222; and each
   missing prerequisite. State that Zotero and Overleaf remain unconnected.
