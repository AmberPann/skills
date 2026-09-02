---
name: test-reporting-standards
description: >-
  Use this skill only for code functional testing: designing a test plan, executing
  automated or manual tests, validating software behavior against code or interface
  contracts, and maintaining a current-state test report. Do not use it for AI Agent
  effectiveness evaluation, including output-quality or capability assessment,
  evaluation-set or benchmark design, grader or judge design, stochastic multi-run
  evaluation, or model and Agent comparison.
---

# Code Functional Test Workflow Standards

Use this skill for the full code functional testing workflow in this repository: define success, produce a test plan, execute the plan case by case, update the current-state report after each case, and close only when every planned item has a current result.

This skill is not only for writing reports. Report writing is one step inside a larger test workflow.

## Scope Boundary

Apply this skill when the assertion is about whether software behaves according to a code, API, interface, state, persistence, or runtime contract.

Do not apply this skill when the subject is an AI Agent's effectiveness, such as:

- whether Agent output is high quality, correct, useful, or preferred
- whether an Agent can complete a task or demonstrate a capability
- how Agent performance varies across repeated runs
- how to design evaluation datasets, benchmarks, metrics, graders, or LLM judges
- how to compare prompts, models, Agents, or workflows by evaluation results

An Agent-related service may still need code functional testing. In that case, use this skill only for contract-level claims such as API behavior, authentication, routing, tool invocation, state transitions, persistence, and readback. Keep semantic output quality, task success, capability coverage, and statistical evaluation outside this skill's plan, report, and templates.

If a request combines code functional testing with Agent effectiveness evaluation, apply this skill only to the code functional testing scope and handle the evaluation scope separately.

## When To Use

Use this skill when the user asks to test code functionality by:

- design a test plan
- execute tests end to end against a known scope
- add or revise unit, integration, or E2E tests
- validate real runtime behavior with logs, persisted state, or readback
- write or update a current-state test report
- audit current coverage, remaining gaps, and blocking failures
- turn an ad hoc testing effort into a tracked execution loop

If the task is only “fix one failing test”, keep the scope narrow, but still use this skill's standards for success criteria, evidence, and current-state reporting.

## Default Workflow

Unless the user explicitly narrows scope, follow this sequence.

1. Align on the success target.
   Confirm what exact outcome counts as success, what does not count, and which evidence source is authoritative. Do not silently replace the user's target with a narrower engineering proxy such as “接口返回 200”, “pytest 通过”, or “日志里出现一次请求”.

2. Produce or update the test plan first.
   Before running broad testing work, create or refresh a plan that defines:
   - goal
   - scope
   - environment and prerequisites
   - execution order
   - plan-point IDs
   - success criteria
   - evidence requirements
   - escalation policy for failed cases

3. Execute strictly against the plan.
   Work plan point by plan point. Do not free-run through random commands and reconstruct scope afterwards. If scope changes during execution, update the plan first, then continue.

4. Update the current-state test report after each completed plan point.
   A plan point is “completed” when it has one current status:
   - passed
   - failed
   - blocked
   Never leave completed execution evidence only in terminal history.

5. If a plan point fails, separate validation from remediation.
   First record the failure with direct evidence and current RCA status: verified RCA, root-cause lead, or open question. Then decide whether the task requires debugging/fixing before continuing.

6. Keep reports human-reviewable.
   Agent-generated testing can produce large amounts of output. The report must make it cheap for a human reviewer to see:
   - what is verified fact
   - which evidence supports it
   - what is an inferred root-cause lead
   - what still requires human or follow-up verification
   Never present an Agent inference as a verified conclusion without evidence.

7. Confirm the external-worker policy during planning if failures may need parallel investigation or fixing.
   During the test-plan stage, ask the user whether failed cases may be escalated to an external worker or assistant session. If yes, record in the plan:
   - whether external workers are allowed
   - which command pattern is approved
   - whether approval is one-time for the whole plan or required case by case
   - any required worker/session identity constraints
   Example:
   - `claude --dangerously-skip-permissions --resume {session_id}`
   - `claude --dangerously-skip-permissions "请排查 RECALL-07 的 backend 路由问题"`
   Do not launch external workers, resume external sessions, or run user-specific assistant commands unless the user has approved that policy.

8. After a fix, re-run the affected plan points and refresh the report again.
   A stale failure entry is not acceptable once the code changed.

9. Finish only when every plan point has a current status in the report.
   The final report must show no hidden “pending mental checklist”.

## Core Rules

### 1. Plan before execution

The default deliverables are:

- a test plan
- a current-state test report

The plan is the execution contract. The report is the evolving current-state snapshot.

Start from the plan template in [`references/test-plan-template.md`](./references/test-plan-template.md).
Write reports with [`references/report-template.md`](./references/report-template.md).

When the repository already has an active plan/report pair, update them instead of creating parallel artifacts.

### 2. Every plan point needs an ID

Use stable IDs such as:

- `PATH-01`
- `UPD-03`
- `RECALL-07`

IDs let the plan, execution notes, code changes, and report stay aligned. The report must reference plan-point IDs directly rather than inventing a second naming system.

### 3. Execute by layer, not by convenience

Choose the layer that can actually prove the behavior:

- unit tests for pure logic, parsing, classification, mapping, state transitions
- runtime tests for initialization, wiring, config loading, lifecycle
- integration/E2E for cross-process or cross-service claims
- manual/live validation when the value is in observing a real running flow

Do not use unit tests alone to claim an end-to-end behavior.

### 4. “Passed” means the evidence matches the claim

For each plan point, define:

1. what condition must be true
2. how it is observed
3. which artifact proves it
4. whether that artifact is direct evidence or only supporting evidence

Prefer evidence across layers:

- execution evidence: pytest output, request result, SSE response, manual trigger result
- service evidence: caller log, callee log, worker log
- persistence evidence: DB row, object storage object, file content, lock state
- readback evidence: query API, read interface, follow-up session recall, backend readback

If a claim needs persistence or readback, do not mark it passed from first-hop success alone.

### 4.1 Keep facts, evidence, and inferences separate

This is especially important when an Agent helps test, inspect logs, read code, or draft the report.

Use these categories consistently:

- verified fact: directly observed behavior, command output, log line, DB row, readback result, source definition
- evidence: artifact that lets a reviewer verify the fact
- inference: an interpretation drawn from facts, such as suspected cause or impact
- root-cause lead: a plausible RCA candidate that still needs confirmation
- verified RCA: root cause confirmed by source inspection, reproduction, or targeted verification
- open question: what remains unknown and how to verify it

Do not collapse these into a single “current conclusion” when the reviewer needs to know which parts are proven.

### 5. Reports are current-state only

The report should describe only the latest valid state:

- latest command or trigger
- latest result
- current status per plan point
- current failures and blockers
- current uncovered items

Do not turn the report into a repair diary unless the user explicitly asks for chronology.

The report should include a short human-review summary when the scope is non-trivial:

- current release/merge/readiness judgment if applicable
- highest-risk failures or blockers
- findings that need human review
- assumptions not yet backed by evidence

### 6. Update the report continuously, not at the end

After each plan point:

1. record the actual command or live trigger
2. record the observed result
3. set the plan-point status
4. attach direct evidence
5. refresh the summary counts if they changed

This is mandatory for long-running test efforts.

### 7. Manual testing is valid only with durable evidence

When manual/live validation is required, use [`references/manual-testing-checklist.md`](./references/manual-testing-checklist.md).

Record:

- exact trigger
- stable input identifier
- expected result
- actual result
- service evidence
- persistence/readback evidence
- final judgment

If a manual case becomes repeatable, propose converting it into automation.

## Execution Loop

Use this loop for broad testing tasks.

1. Read the relevant code, design doc, interface contract, or prior report.
2. Build or refresh the test plan.
3. Create or refresh the current-state report with all plan points listed.
4. Execute the highest-priority pending plan point.
5. Update the report immediately.
6. If the point failed, decide whether to:
   - continue collecting other independent evidence
   - debug locally
   - ask the user whether to wake an external worker
7. If code changes were made, re-run the affected point and update the report again.
8. Repeat until every plan point is passed, failed, or blocked.

## Failure Handling

When a case fails:

1. Record the failure first.
   Include the direct failing evidence, not just an interpretation.

2. Trace to root cause before claiming a conclusion.
   For static facts such as code definition, routing, prompt content, backend mount rules, or permission rules, inspect the source directly.

3. Separate root-cause leads from verified RCA.
   Agent-assisted testing can make code and logs easier to inspect, so reports may include deeper root-cause clues than traditional black-box testing. Mark them explicitly:
   - `已验证 RCA`: confirmed by direct source/log/runtime evidence
   - `初步根因线索`: plausible but not fully verified
   - `待确认`: specific check needed before treating the lead as fact

4. Keep business interpretation out of generic framework layers unless the repository already does so.
   If the fix appears to require domain-specific parsing in an infrastructure layer, challenge that design before implementing it.

5. If the user expects remediation and a local fix is feasible, do it.
   If the remediation would rely on an external worker, a resumed external session, or a user-specific assistant command, ask the user first.

## External Worker Escalation

This skill allows recommending a worker or companion assistant when a failed case needs deeper debugging or a parallel fix.

Prefer settling the policy in the test plan before execution starts.

1. During planning, ask whether worker escalation is allowed for failed cases.
2. If allowed, record the approved command pattern and approval mode in the plan.
3. When a failure occurs, follow that recorded policy.
4. If the plan requires case-by-case approval, ask again before invoking the worker.
5. After the worker returns, re-run the affected plan point and update the report.

Example wording:

- Planning-stage confirmation:
  “本轮测试若遇到失败项，是否允许我唤起外部 worker 并行排查或修复？如果允许，请确认命令形式，例如 `claude --dangerously-skip-permissions --resume {session_id}`，以及这是整轮预授权还是逐案确认。”
- Execution-stage confirmation when policy is case-by-case:
  “`RECALL-07` 已有失败证据，需要并行排查 asset/conversation_history backend 路由。按当前计划，这类场景需逐案确认。若你同意，我会用 `claude --dangerously-skip-permissions --resume {session_id}` 唤起对应 worker。”

Do not hide the worker step inside the skill as an automatic side effect.

## Repository-Specific Rules

For this repository:

- write test plans and test reports in Chinese unless the user explicitly requests another language
- in markdown test artifacts, prefer relative links between plan, report, evidence, and referenced files unless the repository requires otherwise
- keep commands, code identifiers, test function names, and file paths in their original form
- do not claim integration/E2E execution from `--collect-only`
- functional integration tests for code under `agent/` should use injected env when needed, for example:

```bash
infra/scripts/load-dev-env.sh bash -lc 'cd agent && uv run pytest ...'
```

- if a live Agent API is required for code functional testing, start it with the same env source actually used by the service

## What Good Output Looks Like

At the end of a testing task, the repository should have:

1. a plan that names all intended test points
2. a report that maps one-by-one to those plan points
3. direct evidence for each passed/failed/blocked point
4. a human-review summary for non-trivial scopes
5. failure entries that separate verified facts, evidence, root-cause leads, and open questions
6. no “未执行” or “部分覆盖” entries unless they are still truly current

## References

- Use [`references/test-plan-template.md`](./references/test-plan-template.md) to create or refresh the execution plan.
- Use [`references/report-template.md`](./references/report-template.md) to keep the current-state report aligned to the plan.
- Use [`references/manual-testing-checklist.md`](./references/manual-testing-checklist.md) when the task requires live/manual validation.
