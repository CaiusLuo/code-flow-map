# Code Flow Map

[English](README.md) · **简体中文**

在一个离线 HTML 页面里读懂仓库的一条执行流程。左侧看源码，右侧看流程。点击节点跳到对应的代码行，点击带圆点的行号回到节点。

![Code Flow Map 封面，左侧源码与右侧流程节点双向对应](docs/images/cover.png)

## 演示

https://github.com/user-attachments/assets/fa17df5e-d21b-488a-b96a-a99b4205e0a4

*36 秒使用演示，从源码定位到重试路径播放。*

[下载离线示例](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/task-queue.html)

## 最小用法

在要阅读的项目里调用 `code-flow-map`，指定要追踪的流程，带上你关心的分支。

> 梳理任务从领取到完成的流程，展示处理失败后的重试过程。生成一个能离线打开的 HTML 流程图。

用播放或单步按钮按顺序跟读主线和分支。对于 Git 项目，Code Flow Map 默认读取本地 HEAD，并在 HTML 里标明提交号。HTML 包含被引用的源码文件全文。

## 安装

生成 HTML 需要 Python 3.9 或更新版本。从提交读取源码需要 Git。可以[直接在 GitHub 阅读 Skill](skills/code-flow-map/SKILL.md)，也可以下载 [v0.1.0 Skill ZIP](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/code-flow-map-skill-v0.1.0.zip) 手动安装。

### Codex 和 Claude Code

在目标项目目录执行：

```sh
npx skills add CaiusLuo/code-flow-map --skill code-flow-map --agent codex claude-code
```

在 Codex 输入 `$code-flow-map`，在 Claude Code 输入 `/code-flow-map`。如需手动安装，把完整的 `code-flow-map` 技能目录分别放到项目的 `.agents/skills/` 或 `.claude/skills/`。 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills) · [Claude Code 技能文档](https://code.claude.com/docs/en/skills)

### DeepSeek Harness

把完整的 `code-flow-map` 技能目录放到项目根目录的 `.agents/skills/` 或 `.dsh/skills/`，然后输入 `/code-flow-map`。如果已在同一项目为 Codex 安装到 `.agents/skills/`，可以直接复用。 [Harness 技能文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)

### Pi

用 Pi 的 Git 包安装，固定到首版。安装后在 Pi 输入 `/skill:code-flow-map`。

```sh
pi install git:github.com/CaiusLuo/code-flow-map@v0.1.0
```

[Pi 包与安装文档](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/packages.md)

### Magpie

1. 打开 **Library → Skills**，从 GitHub 添加 `CaiusLuo/code-flow-map`，选择 `code-flow-map` 和要接收它的 Agent。
2. 如果已启用 Skill Router，运行下面的命令让这一项进入 `magpie-skills` 目录。采用直装时，可用接收方 Agent 自己的技能调用方式。

```sh
magpie library skill router code-flow-map routed
```

如果需要开启库级 Skill Router，可以运行 `magpie library skill router on`。这个开关作用于整个 Library，具体是否调用某项技能仍由接收技能的 Agent 决定。 [Magpie Library 文档](https://usemagpie.ai/docs/library#skills)

## 本地跑一个示例

示例任务队列演示首次成功和失败重试两条路径。在仓库根目录运行渲染命令。

```sh
python3 skills/code-flow-map/scripts/render.py \
  --repo examples/task-queue \
  --manifest examples/task-queue/flow.json \
  --out task-queue.html
```

在浏览器打开 `task-queue.html`。要调整节点或新增路径，修改 [示例清单](examples/task-queue/flow.json) 后重新生成。 [清单字段说明](skills/code-flow-map/references/manifest.md)

## 许可证

[MIT](LICENSE)
