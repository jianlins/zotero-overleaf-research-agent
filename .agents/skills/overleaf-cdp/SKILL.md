---
name: overleaf-cdp
description: Edit and compile a logged-in Overleaf project through visible Chrome DevTools Protocol. Use for bounded LaTeX or BibLaTeX edits, citation insertion, and compile-log checks; not for account, sharing, or token management.
---

# Overleaf CDP

Use the visible Chrome/CDP session to make small, reviewable changes to one
Overleaf project and verify them through Overleaf's compiler.

## Scope

- Confirm the exact project and target file before writing.
- Browser login, project creation, file creation, edits, and recompilation
  change external state. Perform only actions authorized by the user.
- Account settings, sharing, integrations, token creation, and project
  deletion are outside this skill.
- Reuse an existing Chrome/CDP connection and tab whenever possible. Start
  the isolated research browser only when no usable session exists.
- When starting it, use `.agents/scripts/start-research-chrome.sh` on macOS,
  `.agents/scripts/start-research-chrome-linux.sh` on Linux, or
  `.agents/scripts/start-research-chrome.ps1` on Windows. If browser discovery
  fails, request the browser executable path and use the launcher's path option
  (`--chrome-path` on Linux; `-ChromePath` on Windows).

## Edit and verification loop

1. Inspect Chrome pages and select the intended Overleaf project.
2. Read the complete target file and retain its original content in the task
   context.
3. Make one bounded edit. For a small file, replacing its whole content is
   preferable to multi-step cursor edits.
4. Read the editor again and confirm the intended source is present.
5. Select **Recompile** and wait until compilation completes.
6. Inspect both the PDF and **View logs**. Completion requires zero errors;
   report relevant warnings.
7. If the edit caused a failure, correct or restore that bounded edit and
   compile again. Stop if the failure is unrelated or cannot be safely fixed.

## Bibliography verification

For standalone BibLaTeX projects, the default compatible setup is:

```latex
\usepackage[backend=biber,style=authoryear]{biblatex}
\addbibresource{references.bib}

% In the document body:
\parencite{citationKey}
\printbibliography
```

Keep bibliographic metadata valid BibTeX/BibLaTeX syntax. Treat a citation as
verified only when its in-text form and bibliography entry are both visible in
the rendered PDF.

## Evidence to report

Report the project name, changed files, whether each expected citation appears
in the PDF, and final error/warning counts. State separately anything not
verified in the live project.

