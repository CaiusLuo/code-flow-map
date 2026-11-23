# Flow manifest

Use UTF-8 JSON. `project` identifies the repository, `title` names the workflow, and `language` selects English (`en`, default) or Chinese (`zh`) controls.

```json
{
  "project": "Example worker",
  "title": "Complete one job",
  "language": "en",
  "nodes": [
    {
      "id": "run",
      "title": "Run the job",
      "symbol": "runJob()",
      "description": "Invoke the registered handler with the claimed job.",
      "refs": [{"file": "src/worker.ts", "lines": [12, 16], "label": "Invoke handler"}]
    },
    {
      "id": "finish",
      "title": "Save result",
      "symbol": "store.save()",
      "description": "Write the result before acknowledging the job.",
      "refs": [{"file": "src/worker.ts", "lines": [20, 24], "label": "Save result"}]
    }
  ],
  "paths": [{"name": "Success", "steps": ["run", "finish"]}]
}
```

- List references in display order, with the primary jump first. Use repository-relative paths and inclusive, one-based line ranges. References in the same file must be disjoint so a click has one destination.
- The first path establishes the main vertical lane and lists each of its nodes once. An additional path can revisit nodes. A side node sits beside its preceding main-lane node, with one side node per row. Model a longer branch as its own walkthrough if the diagram gets crowded.
- Path steps describe the order the user sees during playback. Include each declared node in at least one path. Use `symbol` for the real function, event, or type behind the step.

Run with Python 3.9 or newer from any directory, using absolute paths where helpful.

```sh
python3 /path/to/code-flow-map/scripts/render.py \
  --repo /path/to/repo --ref COMMIT \
  --manifest /path/to/flow.json --out /path/to/flow.html
```

Omit `--ref` to read files from the given directory. In Git mode, pass the same commit used for source inspection. Regenerate after updating the manifest or ranges. Open the resulting HTML directly in a browser.
