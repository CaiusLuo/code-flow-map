# Code Flow Map

**English** · [简体中文](README.zh-CN.md)

Trace a repository workflow in an offline HTML page with source code on the left and the execution flow on the right. Click a node to jump to its source lines, or click a marked line number to find its node.

![Code Flow Map cover showing source code linked to execution nodes](docs/images/cover.png)

## Demo

https://github.com/user-attachments/assets/fa17df5e-d21b-488a-b96a-a99b4205e0a4

*36-second walkthrough with Chinese captions, from source navigation to replaying a retry path.*

[Download the offline example](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/task-queue.html)

## Quick start

Invoke `code-flow-map` in the project you want to understand. In your prompt, name the workflow and any branch you want to trace.

> Trace a job from claim to completion. Show what happens when processing fails and the job is retried. Give me an HTML map I can open offline.

Use playback or single-step controls to follow the main path and its branches. For Git projects, Code Flow Map reads local HEAD by default and records the source commit in the HTML. The file includes the full text of each referenced source file.

## Install

Rendering requires Python 3.9 or newer. Reading source from a commit requires Git. [Read the skill on GitHub](skills/code-flow-map/SKILL.md) or download the [v0.1.0 skill ZIP](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/code-flow-map-skill-v0.1.0.zip) for manual installation.

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

The sample job queue demonstrates a successful run and a retry after failure. Run the renderer from the repository root.

```sh
python3 skills/code-flow-map/scripts/render.py \
  --repo examples/task-queue \
  --manifest examples/task-queue/flow.json \
  --out task-queue.html
```

Open `task-queue.html` in a browser. To change a node or add a path, edit the [example manifest](examples/task-queue/flow.json) and render it again. [Manifest fields](skills/code-flow-map/references/manifest.md)

## License

[MIT](LICENSE)
