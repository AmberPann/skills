# Codex UI 适配器

仅在 Codex 且当前环境提供 `visualize` 时使用。先读取当前 `visualize` Skill，其契约优先于本文件。UI 负责理解、定位和导航；文件链接、覆盖表、原文证据和完整问题说明仍使用原生 Markdown。

## 审查地图

首次地图和“回到地图”使用一个紧凑的行内交互总览，替代本次响应中的 Markdown 地图。总览从已校验的 `review-state.json` 读取，不能重新分析。

总览按以下顺序呈现：

- 标题上方显示弱化的 `Agent Skill Review` 标识；
- 使用 Skill 或 package 名称作为简洁主标题；
- 标题下用一行 `.text-muted` 文本显示目标 Agent、环境、版本、主文和 reference 数量，不把这些元数据做成 badge；
- 用“解决的问题”“阅读边界”“解决机制”“文章组织”“证据边界”五行说明 Skill 脉络；
- 显示“审查地图”标题，再按固定顺序显示四个审查维度；
- 推荐理由放在维度列表之后、全局操作之前；没有证据时省略；
- 最后显示“只看问题”和“完整审查”按钮。

Skill 脉络使用对齐的“标签列 + 内容列”。标签保持简短、使用 `500` 字重，内容使用正常正文；各行之间用细分隔线区分。内容较长或宽度不足时，整组切成单列，不保留空白标签列。

每个维度使用一条全宽语义行，不做卡片：左侧依次显示编号和维度名称、一句话目的、覆盖状态与发现数量；右侧显示“查看第 N 章”按钮。统计信息使用一行 `.text-muted` 文本，以间隔点分隔，不把每个数量做成 badge。最高严重程度可在标题旁使用一个 `.viz-badge`；没有 finding 时不显示空 badge。

顶层透明、无外框。语义行之间使用细分隔线，保持充足纵向留白；操作使用 `<button type="button" class="btn">`，有明确推荐时仅推荐入口使用 `.btn-primary`。不显示路径、源码、长段问题说明、装饰面板或重复标签。颜色只使用 Codex token，并同时显示文字。

宽屏下，Skill 脉络使用 `minmax(112px, 160px) 1fr`，维度行使用 `1fr auto`；窄于约 560px 时都改为单列，按钮放在内容下方并左对齐。不得通过缩小字号、压缩行高或截断文字维持分栏。

## 维度详评

维度详评采用混合呈现：先用一个紧凑可视化摘要显示维度名称、作用、覆盖状态数量、发现数量、最高严重程度和未确认数量；随后用 Markdown 展示完整覆盖记录、问题说明、证据、未确认项和文本导航。

摘要沿用地图的视觉层级：顶部显示弱化的 `Agent Skill Review`，主标题使用 `N/4 <维度名称>`，作用放在标题下一行。覆盖状态、发现和未确认数量合并为一行 `.text-muted` 文本；最高严重程度可单独使用一个 `.viz-badge`。不创建状态卡片或重复指标网格。

可视化摘要不复制覆盖表和问题正文，不显示文件路径。问题位置使用 Markdown 绝对路径链接：

```md
[SKILL.md](/absolute/path/to/SKILL.md:42)
```

## 交互操作

章节、回到地图、相邻维度、只看问题和完整审查使用：

```js
await window.openai.sendFollowUpMessage({
  prompt,
  title,
})
```

`prompt` 必须包含：

- `statePath`；
- 目标视图：`map`、`dimension`、`problems` 或 `full`；
- 进入维度时的固定 key 和中文标题；
- 明确要求先运行 `review_state.py load`，读取同一状态，不重新分析；
- 明确要求状态失效时停止展示旧结论。

示例：

```js
const prompt = [
  "继续 Agent Skill Review。",
  "statePath: /tmp/skill-review-.../review-state.json",
  "view: dimension",
  "dimension: feasibility",
  "先加载并校验状态；不要重新分析。",
].join("\n");

await window.openai.sendFollowUpMessage({
  prompt,
  title: "查看可行性详评",
});
```

`title` 使用当前输出语言，简短说明将打开的视图。不要传入当前 `visualize` 契约没有记录的参数。

## 可视化文件

按当前 `visualize` 契约，将 HTML fragment 写入 Codex 提供的 thread-scoped visualization 目录或其他明确可写、任务专属的位置。fragment 只包含必要标签、状态和按钮。用绝对路径通过 `visualize` 内容引用展示，不向用户暴露临时 HTML 或 `statePath`。

普通审查只在当前 `visualize` 契约要求的一次 fragment 回读中检查必要字段、原生 tab 顺序、交互失败处理、布局规则和 Codex token。回读后直接展示，不再调用其他命令或查看媒体，也不把 UI 验证加入审查证据或完整性条件。

审查过程中不得为地图或摘要启动浏览器、HTTP server、Playwright、截图、图片回看、canvas 检查、多视口或主题测试，也不得反复渲染并调整样式。返回地图、切换维度或读取同一状态时沿用固定布局，不重新验证适配器。

只有用户明确要求设计、修改或调试这个 UI 适配器时，才执行视觉 QA。普通审查中 `visualize` 不可用或首次渲染失败后，立即回退到 `references/interaction-contract.md` 的 Markdown 约定，不调试、不重试，也不同时展示两套地图。
