# AmberPann Skills

这个仓库存放个人日常开发工作编写的 Agent Skills。

| Skill | 用途 |
| --- | --- |
| [`code-review-principles`](code-review-principles/) | 按代码、契约、测试和运行证据审查实现，重点关注正确性、安全性、可维护性和生产风险。 |
| [`design-doc-writing`](design-doc-writing/) | 编写和修订架构设计、ADR、RFC 等长期技术文档，使其脱离原始对话后仍能独立阅读。 |
| [`query-agent-context`](query-agent-context/) | 根据 Git commit 定位产生该变更的 Codex、Claude 或 Cursor 对话。 |
| [`review-agent-skills`](review-agent-skills/) | 审查 Agent Skill 的内容组织、职责边界和实际运行可行性。 |
| [`shape-development-task`](shape-development-task/) | 在复杂开发开始前澄清目标、范围、架构、风险和验收标准，形成可执行的任务契约。 |
| [`test-reporting-standards`](test-reporting-standards/) | 规划和执行代码功能测试，并持续维护反映当前结果的测试报告。 |

## 安装

仓库推送到 GitHub 后，可直接安装并按提示选择需要的 Skill：

```bash
npx skills add AmberPann/skills
```

也可以先下载仓库，再从本地目录安装：

```bash
git clone https://github.com/AmberPann/skills.git
cd skills
npx skills add .
```
