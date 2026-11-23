# Code Flow Map

![Code Flow Map 封面，左侧源码与右侧流程节点双向对应](docs/images/cover.png)

给定一个仓库和一个想弄懂的流程，生成一页可交互的离线 HTML。左侧读源码，右侧看执行流程。点击流程节点跳到对应行，点击带圆点的行号可以回到节点。

[36 秒使用视频](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/code-flow-map-demo.mp4) · [下载离线示例](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/task-queue.html)

## 最小用法

在要阅读的项目里启动 Agent，调用 `code-flow-map` 并说明想看的流程。例如：

> 梳理当前仓库里任务从领取到完成的流程，带上失败重试。交付一个代码和流程图可以双向定位的离线 HTML。

Agent 从真实入口读一条执行主线，补上能解释关键判断的分支，再核对每个节点对应的文件和行号。渲染器根据清单生成页面。Git 项目默认读取本地 HEAD，页面带有提交号。播放按源码中整理出的路径逐步定位。

## 安装

下面几种安装方式共用同一个 [Skill 目录](skills/code-flow-map)。手动安装可以下载 [首版 Skill ZIP](https://github.com/CaiusLuo/code-flow-map/releases/download/v0.1.0/code-flow-map-skill-v0.1.0.zip)。生成 HTML 需要 Python 3.9 或更新版本。读取 Git 提交时需要 Git。

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

从仓库根目录执行。示例是一个自建任务队列，包含首次成功和失败后重试两条路径。

```sh
python3 skills/code-flow-map/scripts/render.py \
  --repo examples/task-queue \
  --manifest examples/task-queue/flow.json \
  --out task-queue.html
```

在浏览器打开 `task-queue.html`。需要手工调整节点或分支时，可以先改 [示例清单](examples/task-queue/flow.json)，再重新生成。字段见 [清单格式](skills/code-flow-map/references/manifest.md)。

HTML 会嵌入被引用文件的全文。分享生成的页面前，检查这些文件是否适合公开。

## 许可证

[MIT](LICENSE)
