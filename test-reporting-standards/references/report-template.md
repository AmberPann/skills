# Current-State Test Report Template

Use this template when the user asks for a test report or when a planned testing task is in progress. The report should stay aligned to the test plan and be updated after each completed plan point.

Write the report in Chinese by default. Keep commands, file paths, code ids, and test function names in their original form.

Prefer relative links between the report, the plan, evidence, and referenced repository files unless the repository explicitly requires absolute links.

## Report skeleton

````md
# [模块名] 当前测试报告

日期：YYYY-MM-DD

计划引用：[测试计划](./[YYYYMMDD]_[module]-test-plan.md)

## 1. 当前态说明

本报告只反映当前工作区内已经实际执行的自动化测试、integration/E2E 验证与 live 验证结果，不包含推测、未执行结论或修复过程说明。

本轮最新自动化基线命令：

```bash
...
```

执行结果：

```text
...
```

如本轮还有补充聚焦命令，继续追加：

```bash
...
```

执行结果：

```text
...
```

如包含 live / 手工测试，补充：

| 手工测试项 | 输入或标识 | 当前结果 | 证据 |
|---|---|---|---|
| `...` | `thread_id / request_id / task_id / file marker` | `通过 / 失败 / 阻塞` | `日志 / 读回 / 返回值` |

执行环境：

- 工作区：`...`
- 测试根目录：`...`
- 运行时版本：`...`
- 命令执行器：`...`

失败升级策略：

- 是否允许外部 worker：`是 / 否`
- 审批方式：`整轮预授权 / 逐案确认`
- 已批准命令模式：`...`

## 2. 人工审查摘要

用于降低 reviewer 的验证成本。只写当前态，不写修复流水账。

- 当前总体判断：`可接受 / 不可接受 / 需要人工复核后判断`
- 最高风险项：`计划点 ID + 一句话原因`
- 需要人工重点复核：
  1. `...`
  2. `...`
- 尚未被证据覆盖的关键假设：
  1. `...`
  2. `...`
- Agent 生成或辅助判断的内容：`无 / 有，见下方失败项或样例中的“初步根因线索”`

## 3. 与测试计划的对应结果总览

- `已通过`：N 个计划点
- `失败`：N 个计划点
- `阻塞`：N 个计划点
- `未执行`：N 个计划点

说明：

- `已通过`：当前执行结果已经覆盖该计划点的核心通过条件。
- `失败`：当前已实际执行，并拿到了直接失败证据。
- `阻塞`：当前未能有效执行，阻塞原因已确认且已记录。
- `未执行`：本轮没有针对该计划点形成有效执行证据。

## 4. 计划点逐条结果

### 4.1 [分块名称]

| 计划点 | 当前状态 | 当前结果 | 事实层 | 证据层 |
|---|---|---|---|---|
| PATH-01 | 已通过 | `...` | `实际观察到的行为` | `[test_xxx.py](../../tests/...)` `test_name`；`日志/读回/脚本结果` |
| PATH-02 | 失败 | `...` | `失败现象或缺失行为` | `[agent.log](../../../infra/.dev-logs/...)`；`readback` |

### 4.2 [分块名称]

| 计划点 | 当前状态 | 当前结果 | 事实层 | 证据层 |
|---|---|---|---|---|
| UPD-01 | 已通过 | `...` | `...` | `...` |

## 5. 当前失败项

按严重程度或计划点顺序列出当前失败项：

1. `RECALL-07`
   - 直接现象：`...`
   - 已验证事实：`...`
   - 直接证据：`...`
   - 初步根因线索：`...`
   - 已验证 RCA：`无 / ...`
   - 待确认项：`...`
   - 下一步验证方式：`...`

## 6. 当前阻塞项

如果没有，可写“当前无阻塞项”。

## 7. 当前未执行项

| 计划点 | 原因 | 下一步 |
|---|---|---|
| `...` | `...` | `...` |

## 8. 本轮新增或重点使用的测试与证据

- [test_xxx.py](../../tests/...)：`验证点`
- [test_yyy.py](../../tests/integration/...)：`验证点`
- [agent.log](../../../infra/.dev-logs/...)：`关键 live 证据`

## 9. Agent / LLM 场景上下文

仅在测试对象或测试执行涉及 Agent / LLM / tool calling 时填写；否则写“本轮不涉及”。

| 项 | 当前值或证据 |
|---|---|
| Prompt / 输入 | `...` |
| 模型 / Agent 版本 | `...` |
| 工具调用记录 | `trace_id / session_id / log link` |
| 运行配置 | `temperature / seed / env / feature flag` |
| 相关代码路径 | `...` |
| 可复现性说明 | `确定性 / 非确定性 / 需多次采样` |

## 10. 关键执行样例

仅保留当前仍有价值的代表性样例。每条样例都要能对应到计划点。

1. `UPD-01` 显式记忆写入
   - 标识：`...`
   - 结果：`...`
   - 当前判定：`...`

2. `RECALL-07` 历史项目 recall
   - 标识：`...`
   - 结果：`...`
   - 当前判定：`...`
````

## Writing rules

- 报告必须和测试计划逐条对齐。
- 每完成一个计划点，就更新一次报告。
- 只写当前最新状态，不写修复过程流水账。
- 所有结果必须来自实际执行，不要把 `collect-only`、旧报告、旧日志当成当前结论。
- 若同一计划点在修复后重跑，必须用最新结果覆盖旧结论。
- 手工测试结果必须带可回查的输入标识和证据来源。
- 如果引用“成功”或“通过”，必须给对应观察依据。
- 区分事实、证据、推断和待确认项；不要把 Agent 的推断写成已验证结论。
- “初步根因线索”只能说明排查方向；只有被源码、日志、复现或针对性验证证明后，才能写入“已验证 RCA”。
- 如果失败项已经按计划唤起外部 worker 处理，报告里只保留当前有效策略和最新结果，不展开写 worker 对话过程。

## Status rules

- `已通过`：当前结果满足该计划点的核心通过条件。
- `失败`：当前结果已形成明确反证。
- `阻塞`：当前因为缺失环境、账号、依赖、权限等原因无法形成有效执行结果。
- `未执行`：当前还没跑到，或没有形成可采信的执行证据。

Avoid “部分覆盖” unless the user explicitly wants an interim state. In a plan-driven workflow, the default expectation is to keep going until the point can be marked passed, failed, or blocked.

## Evidence checklist

When the report claims a real integration or end-to-end outcome, check whether it should cite one or more of:

- test command output
- caller log
- downstream service log
- database query result
- persisted file or object-storage readback
- query or readback API response
- live SSE / HTTP response

If one critical link in the chain is missing, do not overclaim the result.
