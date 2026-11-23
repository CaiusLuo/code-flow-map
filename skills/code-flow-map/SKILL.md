---
name: code-flow-map
description: Create an offline HTML walkthrough of a specific repository workflow, with source code on the left and a clickable execution diagram on the right. Use when the user asks to understand a code path, trace branches through files, or link a flowchart and source in both directions.
license: MIT

---

# Code Flow Map

Turn one workflow into a source-linked walkthrough. Use the user's requested entry point or outcome. When the request only says “core code,” pick the central execution path and state the scope in the handoff.

1. Read the repository instructions and trace the workflow from its actual entry point. For Git, resolve the requested ref to a commit before reading. Default to local HEAD. Use working files when the user requests them or the project lacks Git.
2. Write a small flow manifest using [the manifest reference](references/manifest.md). Follow about 5–9 meaningful steps and add a branch or loop when it explains a real decision. Give every node a primary source range. Add secondary ranges when they explain a cross-file handoff. Verify the execution order and each range against the same source snapshot.
3. Generate a standalone HTML file using [the renderer](scripts/render.py). Resolve bundled paths from the directory containing this SKILL.md. Keep generated files outside the inspected repository unless the user names a destination inside it.
4. Open the file and check flow → source, source → flow, and one complete route, including any loop. Hand off the HTML path, the workflow covered, and the source revision when available. Describe playback as a source-based walkthrough.

The HTML embeds the full text of the mapped files. Select only the source files needed for the walkthrough and keep the result local by default. Fetching, committing, publishing, and installing the skill require their own task authorization.
