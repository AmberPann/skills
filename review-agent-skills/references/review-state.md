# Agent Skill 审查状态

状态保存一次完整分析，供地图、四个维度详评、只看问题和完整审查复用。它不保存第二份 Skill 原文，只保存范围、文件指纹、结论、证据锚点和导航所需摘要。

## 目录

- [生命周期](#生命周期)
- [草稿关键字段](#草稿关键字段)
- [固定维度与关联规则](#固定维度与关联规则)
- [状态命令](#状态命令)

## 生命周期

1. Agent 完成全量分析并准备草稿 JSON。
2. `review_state.py save` 校验草稿、计算源文件 SHA-256，并在系统临时目录创建权限为 `0700` 的 `skill-review-*` 目录。
3. 脚本生成随机 state id，将它同时写入状态和权限为 `0600` 的目录 marker，再以原子写入方式保存权限为 `0600` 的 `review-state.json`。
4. 所有用户视图先通过 `review_state.py load` 重新校验结构和源文件指纹。
5. 源文件变化时状态失效，停止展示旧结论。
6. 审查完成、提前停止或状态失效后运行 `cleanup`。脚本只有在目录前缀、状态版本、state id 和 marker 全部匹配时才删除该状态目录。

## 草稿关键字段

以下内容只展开一个维度，用来说明字段关系，不能直接作为完整草稿提交。实际草稿必须包含后文列出的四个维度，并让 `readingUnits`、覆盖记录、问题和证据引用全部可解析。

```json
{
  "analysisStatus": "complete",
  "language": "zh-CN",
  "title": "generation-skill",
  "scope": {
    "target": "prod generation-skill v4",
    "agent": {
      "name": "Pexo Agent",
      "boundary": "prod Release 6 的 Skill 加载、工具和权限配置",
      "evidenceRefs": ["E0"]
    },
    "environment": "prod",
    "files": [
      {"path": "/absolute/path/SKILL.md", "kind": "main", "role": "入口与主流程"},
      {"path": "/absolute/path/references/route.md", "kind": "reference", "role": "模型路由"}
    ]
  },
  "context": {
    "problem": "这份说明解决什么问题及缺失时的具体失败",
    "readBoundary": "何时启用、继续、跳过和转交",
    "mechanism": "Agent 如何识别、判断、调用、记录和转交",
    "organization": "主文与 references 的阅读目的和顺序",
    "evidenceBoundary": "已查证内容及未确认范围"
  },
  "evidence": [
    {"id": "E0", "kind": "runtime", "source": "prod Agent runtime", "summary": "目标 Agent 及当前运行边界"},
    {"id": "E1", "kind": "document", "source": "SKILL.md:25", "summary": "Activation Gate"}
  ],
  "readingUnits": [
    {
      "path": "/absolute/path/SKILL.md",
      "purpose": "判断是否进入 Generation 并完成生产交接",
      "readWhen": "Script 要求生成素材",
      "skipWhen": "仅编辑现有媒体",
      "inputs": "Script Handoff 和条件性 Subject Manifest",
      "consumer": "Assembly、Motion 或直接交付",
      "lifecycle": {"status": "applicable", "detail": "包含工具调用、handoff 和失败恢复"},
      "placement": "保留为 SKILL.md 主流程",
      "coverageRowIds": ["F1", "N1", "C1", "T1"]
    }
  ],
  "dimensions": [
    {
      "key": "feasibility",
      "title": "可行性",
      "purpose": "判断说明要求的行为能否在目标 Agent 中执行",
      "overallConclusion": "关键工具可用，但音乐和 AFC contract 不匹配",
      "coverage": [
        {
          "id": "F1",
          "question": "music_generate 是否接受 Skill 规定的参数？",
          "status": "有问题",
          "conclusion": "prod 工具不接受 scene/music_prompt 协议",
          "evidenceRefs": ["E1"],
          "problemIds": ["P1"]
        }
      ]
    }
  ],
  "problems": [
    {
      "id": "P1",
      "dimensionKey": "feasibility",
      "coverageRowIds": ["F1"],
      "severity": "P1",
      "title": "完整歌曲调用使用了失效协议",
      "location": "generation-skill/references/music-audio-production-strategy.md:21",
      "file": "/absolute/path/references/music-audio-production-strategy.md",
      "line": 21,
      "problem": "Skill 要求传 scene、duration_ms 和 music_prompt",
      "introducedBy": "当前 tool schema 已改为统一 provider_param，旧字段无法绑定",
      "trigger": "Agent 生产作为画面时钟的完整歌曲",
      "impact": "调用在生成前失败，重要路径无法闭环",
      "fix": "改用当前 composition_plan contract，或恢复旧协议适配",
      "evidenceRefs": ["E1"]
    }
  ],
  "finalAssessment": {
    "overall": "存在阻断重要路径的问题",
    "unresolved": ["未执行付费生成调用"]
  }
}
```

## 固定维度与关联规则

完整草稿必须包含四个 `dimensions`，顺序和 key 固定：

- `feasibility`：可行性；
- `necessity`：内容必要性、增量和信息密度；
- `clarity`：内容清晰度；
- `terminology`：术语与指代。

`status` 只使用 `通过`、`有问题`、`未覆盖`、`不适用`。每个 `有问题` 覆盖项必须关联至少一个 `problemIds`；其他状态不得关联问题。`severity` 可以是 `P1`、`P2`、`P3` 或 `null`，其中 `null` 表示已确认问题尚未达到 Finding 门槛。

`scope.target` 记录被审查的 Skill 或 package。`scope.agent` 记录运行它的 Agent、已核对的运行边界和对应证据；缺少任一项时不能保存完整状态。

每个 main/reference 文件必须有一条 `readingUnits` 记录，并通过 `coverageRowIds` 连接到覆盖记录。问题必须连接到状态为 `有问题` 的覆盖项。证据引用必须解析到 `evidence[].id`。

## 状态命令

保存草稿：

```bash
python3 <skill-dir>/scripts/review_state.py save --input <draft-json>
```

加载状态：

```bash
python3 <skill-dir>/scripts/review_state.py load --state <statePath>
```

清理状态：

```bash
python3 <skill-dir>/scripts/review_state.py cleanup --state <statePath>
```
