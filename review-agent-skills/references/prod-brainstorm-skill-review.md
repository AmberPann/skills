# prod Brainstorm Skill 审查记录

本文保存对 prod 当前有效 Brainstorm Skill 的已确认审查结论。它是个案 checkpoint，不替代 `../SKILL.md` 中的通用审查方法。

## 目录

- [审查范围](#审查范围)
- [Skill 的原始职责](#skill-的原始职责)
- [URL2Video 与 Brainstorm 的职责关系](#url2video-与-brainstorm-的职责关系)
- [已确认的内容放置原则](#已确认的内容放置原则)
- [三份 URL 路线记录](#三份-url-路线记录)
- [已确认 findings](#已确认-findings)
- [独立问题：当前 artifact revision 的确定](#独立问题当前-artifact-revision-的确定)
- [未确认项](#未确认项)

## 审查范围

- 环境：prod。
- Skill：`brainstorm-skill@v4`。
- 运行内容：`SKILL.md` 与 8 个 references，共 1,164 行。
- 主文：227 行，声明 7 个兼容工具，引用 6 个其他 Skills。
- 运行核对：三台 prod Agent 挂载内容一致。
- 平台检查：包级 `required=0`、`suggested=0`。
- 尚未执行：真实 URL-to-video E2E。

## Skill 的原始职责

通用 Brainstorm 处理同一个创意决策过程：

- 判断用户的目标、受众、约束和创意方向是否已经足够明确；
- 在未决选项会明显改变结果时，与用户逐项收敛；
- 必要时用最轻量的预览帮助用户判断；
- 将确认后的需求和创意方向记录为 Creative Brief；
- 在方向已经完整的非 URL 请求中跳过该阶段。

需求分析和创意方案共同修改 Creative Brief，也共享同一个完成条件，因此可以作为一个高内聚阅读目的。

## URL2Video 与 Brainstorm 的职责关系

URL2Video 包含独立的判断和行为边界：

- 任意 URL 会覆盖 Brainstorm 的正常 skip；
- 使用专属 Capture、query、download 和分析工具；
- 处理 blocked、thin、empty、ambiguous 等来源状态；
- 记录 URL 事实、素材索引、下载路径和 provenance；
- 形成 Capture Context 与 Website Asset Brief；
- 将确认素材继续传给 Script、Subject、Generation、Assembly 和 Motion。

这些内容可以在创意方向已经完整时独立发生，也会因 Capture 协议和来源结构变化而独立修改。它与创意设计共享的是 Script 前置位置和用户确认，不是同一个核心判断。

历史证据：

- `r1785306931328062809` 中的 Brainstorm 主文只有 31 行，是创意方向入口。
- `r1785313519826291285` 的提交信息是 `sync url2video skill runtime content from test`。
- 该提交将 URL Capture、Website Asset Brief 和确认流程并入原有 Brainstorm，同时删除多份旧 references。

已确认方向：将 URL2Video 从 Brainstorm 拆出，规划为新的 Skill。新 Skill 的名称、接口和详细状态机尚未确定。

## 已确认的内容放置原则

- Skill 主文保留跨工具的编排不变量、选择依据、结果消费方式、停止和转交条件。
- 参数名、枚举、数量限制和返回结构由 live tool schema 表达。
- 只在局部分支需要的详细判断放入 reference。
- 可独立适用、拥有独立 use/skip 和失败边界的内容拆成 Skill。
- 跨阶段稳定字段放入 contract。
- parser、schema validation、权限、幂等、持久化和当前版本选择由代码、validator 或 action 保证。

## 三份 URL 路线记录

当前说明定义三类记录：

- Creative Brief：用户确认的目标、受众、创意方向、beats、format 和约束。
- Capture Context：URL 返回的事实、overview、素材索引、下载记录和来源证据。
- Website Asset Brief：连接创意方案和 URL 来源，记录拟使用的素材、用途和用户确认。

三类信息具有不同的变化原因，可以分别保留。Website Asset Brief 不应写入内部 `proposed_owner` 和 `proposed_lane`；生产 owner 由 Script 根据已确认用途派生。

## 已确认 findings

### [P2] Brainstorm 内聚不足

位置：`brainstorm-skill/SKILL.md:17`。

非 URL 路线只在创意不完整时进入，URL 路线却在创意完整时仍强制执行。URL 子流程拥有专属工具、失败状态、三份记录和 provenance contract，构成可独立适用的另一类工作。

### [P2] 用户确认记录耦合内部生产路由

位置：`brainstorm-skill/references/website-asset-brief-contract.md:61`。

同一 contract 说明 Script 负责编译 production ownership，却要求 Brainstorm 在用户确认记录中写入 `proposed_owner` 和 `proposed_lane`。内部路由变化因此可能触发不必要的用户重新确认。

### [P2] 确定性 artifact 校验没有系统机制

位置：`brainstorm-skill/SKILL.md:144`。

说明要求 parse YAML、reject duplicate keys 并执行 contract validation。prod 向 Agent 提供读写文件能力，但没有三种 Brainstorm artifact 的 parser 或 validator action。重新阅读文本不能证明确定性校验成功。

### [P2] publishing-skill 是无效转交目标

位置：`brainstorm-skill/SKILL.md:224`。

prod 当前有效 Skills、Skill 元数据和 repo head 都没有 `publishing-skill`，但 Brainstorm、Script 和 Capability Discovery 仍引用它。

### [P3] 主文重复并混入低频内容

位置：`brainstorm-skill/SKILL.md:202`。

Preview 判断在主文多处和 reference 中重复；Creative Principles 重述 `creative-ideation-principles.md`；Multi-Direction、Combine Both 和 Format Preferences 混入每次必读主文。主文出现 27 处负向表达。

### [P3] 行动主体、术语和指代不清

位置：`brainstorm-skill/SKILL.md:36`。

- Skill、Brainstorm、Script 等阶段名被写成调用工具、读写文件或维护状态的主体；
- `See -> Think -> Execute -> Land` 不是领域通用状态名，`Land` 实际表示 persist/handoff；
- `Format Gate` 没有可定位章节；
- `Ground Rules` 没有包内路径或注入契约；
- `internal video production knowledge` 没有说明来源。

说明应直接要求 Agent 在什么条件下识别、判断、调用、记录或停止。阶段名只标识当前职责范围。

## 独立问题：当前 artifact revision 的确定

该问题独立于 Brainstorm 和 URL2Video 的拆分，暂不讨论解决方案。

问题描述：

- 同一类型的不可变 handoff 可以存在多个 revision；
- 后续阶段必须确定当前有效 revision；
- 历史 revision 需要保留，但不能继续被误用；
- 长任务经过 summarization 或用户跨轮修改后，不能依赖模型记忆、目录顺序或最大 RNN 猜测当前版本。

当前可验证事实：

- Skill 文本使用 `artifact_context` 表示当前 artifact path；
- Agent 可观察面没有读取或更新 current artifact 的明确 action/contract；
- `PexoAgentState` 是 LangGraph 内部实现，不是 Skill 读者可以直接访问的对象；
- summarization 只向 Agent 保留摘要和最近消息，摘要不保证保留完整 artifact identity。

影响：

- 后续阶段可能无法唯一选择有效 revision；
- 如果自行猜测，则不可证明所读 artifact 是当前版本；
- 如果停止并退回上游，则长任务可能重复执行已完成阶段。

状态：已记录，解决方案待独立讨论。

## 未确认项

- URL2Video 新 Skill 的正式名称、两次读取时机和产物 contract。
- URL 素材选择是否继续使用独立 Website Asset Brief。
- 用户确认引用和确认时间由哪个可观察接口提供。
- 真实 URL-to-video E2E 下，当前 artifact 路径、Capture failure 和用户改选能否按文档闭环。
