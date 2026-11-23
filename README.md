# Code Flow Map

**English** · [简体中文](README.zh-CN.md)

![Code Flow Map cover showing source code linked to execution nodes](docs/images/cover.png)

Turn one repository workflow into an interactive, offline HTML walkthrough. Read the source on the left and follow the execution flow on the right. Select a node to jump to its source, or select a marked line number to jump back to the node.

## Demo

https://github.com/user-attachments/assets/fa17df5e-d21b-488a-b96a-a99b4205e0a4

*36-second walkthrough with Chinese captions, from source navigation to replaying a retry path.*

[Download the offline example](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/task-queue.html)

## Quick start

Open the project you want to understand, invoke `code-flow-map` in your agent, and describe the workflow. For example, ask:

> Trace how a job goes from claim to completion, including retry after failure. Give me an offline HTML page where I can jump between the flow and the source.

The agent reads the entry point, follows the main path and its relevant branches, then checks the file and line range for each node. The renderer turns that map into one HTML file. For Git projects, the skill reads local HEAD by default and includes the commit in the output. Playback follows the paths mapped from the source.

## Install

Every agent uses the same [skill directory](skills/code-flow-map). For a manual install, download the [v0.1.0 skill ZIP](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/code-flow-map-skill-v0.1.0.zip). Rendering requires Python 3.9 or newer. Reading a commit also requires Git.

### Codex and Claude Code

Run this in the target project:

```sh
npx skills add CaiusLuo/code-flow-map --skill code-flow-map --agent codex claude-code
```

Invoke `$code-flow-map` in Codex or `/code-flow-map` in Claude Code. For a manual install, put the full `code-flow-map` directory under the project's `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. [Codex skills](https://learn.chatgpt.com/docs/build-skills) · [Claude Code skills](https://code.claude.com/docs/en/skills)

### DeepSeek Harness

Put the full `code-flow-map` directory under `.agents/skills/` or `.dsh/skills/` at the project root, then invoke `/code-flow-map`. Harness can reuse the same project-level `.agents/skills/` installation as Codex. [Harness skills](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)

### Pi

Install the Git package at the release tag, then invoke `/skill:code-flow-map`.

```sh
pi install git:github.com/CaiusLuo/code-flow-map@v0.1.0
```

[Pi packages](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/packages.md)

### Magpie

1. In **Library → Skills**, add `CaiusLuo/code-flow-map` from GitHub. Pick `code-flow-map` and the agents that should receive it.
2. If the Skill Router is enabled, use the command below to list it in `magpie-skills`. With direct installation, use the receiving agent's own invocation.

```sh
magpie library skill router code-flow-map routed
```

Run `magpie library skill router on` to enable the router for the whole Library. Each receiving agent decides when to invoke a skill. [Magpie Library](https://usemagpie.ai/docs/library#skills)

## Run the example locally

Run this from the repository root. The example uses a small job queue with a success path and a retry path.

```sh
python3 skills/code-flow-map/scripts/render.py \
  --repo examples/task-queue \
  --manifest examples/task-queue/flow.json \
  --out task-queue.html
```

Open `task-queue.html` in a browser. To adjust the nodes or branches, edit the [example manifest](examples/task-queue/flow.json) and render it again. The [manifest reference](skills/code-flow-map/references/manifest.md) describes its fields.

The HTML embeds the full text of the referenced source files. Check those files before sharing a generated page.

## License

[MIT](LICENSE)
