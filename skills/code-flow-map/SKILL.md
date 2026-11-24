---
name: code-flow-map
description: Learn a repository's core code paths with a browser-ready HTML walkthrough that links flow nodes and source lines in both directions. Use to trace a specific code behavior or to list or delete saved Code Flow Map walkthroughs.
license: MIT
---

# Code Flow Map

Use the user's request to choose one action.

- **Create a walkthrough.** Trace one learning question using the steps below. Save the HTML in `~/code-flow-map` and return a link the user can open in a browser.
- **List walkthroughs.** Run `python3 scripts/library.py list` and turn its JSON into a compact table in the conversation. Include the title, source revision when available, and a link to each HTML file.
- **Delete a walkthrough.** List the saved files and match the user's selection to one exact filename. Ask which file they mean if several match. Run `python3 scripts/library.py delete -- "filename.html"` for the selected file. Report where it moved under `~/code-flow-map/.trash`.

Run bundled scripts from the skill directory or use their absolute paths. Keep all generated walkthroughs and cleanup inside `~/code-flow-map`. The scripts enforce this folder. Source code can be read from the requested repository.

## Create a walkthrough

1. Start with one learning question and identify the entry point, key decision or state change, and outcome. Use the requested local directory, the current project when clear, or a public GitHub repository URL. For GitHub, resolve the requested ref or remote HEAD and inspect the needed files at that commit. For local Git, default to HEAD and read working files when requested or when Git is unavailable.
2. Write a flow manifest using [the manifest reference](references/manifest.md). Show the steps needed to answer the question. Give every node a source range at the inspected revision. Add secondary ranges for cross-file handoffs. Use the `focus` field to open at the node that best explains the question.
3. Run [render.py](scripts/render.py) with `--repo`, `--ref` when pinned, and `--manifest -` to pass the JSON on stdin. It saves one self-contained HTML file.
4. Open the generated page. Verify that selecting the focus node reveals the relevant code, that a marked source line selects its flow node, and that the path reaches the stated outcome. Return the HTML link, scope, and source revision when available.

Each HTML contains the full text of its referenced source files. Include only the files needed to explain the workflow. Keep the project's sources and the generated page local unless the user requests publication.
