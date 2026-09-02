# Manual Testing Checklist

Use this checklist when the task requires live verification against a running service, UI, tool flow, or external dependency and the result needs to be reported as valid evidence.

This checklist is part of a larger plan-driven workflow:

1. the manual case should map to a test-plan point ID
2. the result should be written back to the current-state test report immediately after execution
3. if the failed case may trigger an external worker, follow the escalation policy already recorded in the test plan

## When to use

Use this checklist when:

- the user explicitly asks for manual testing or point-and-check validation
- the flow depends on live services, real accounts, or real side effects
- automation is not yet worth the setup cost
- the goal is to validate a user-visible or operator-visible behavior before scripting it

Do not treat manual testing as “informal”. If it will be cited in a report, record it with the same rigor as automated evidence.

## Required record for each manual case

For every manual case, record all of the following:

| Field | What to record |
|---|---|
| Plan point ID | The exact test-plan ID such as `RECALL-07` or `UPD-01` |
| Case name | Short stable name for the scenario |
| Purpose | What exact behavior is being validated |
| Success definition | What counts as pass, and what does not |
| Trigger action | Exact command, request, UI path, or user action |
| Input identifier | Thread ID, task ID, request ID, account ID, file path, or other stable identifier |
| Preconditions | Required env, account state, service state, seeded data, running process |
| Expected result | Observable outcome expected before execution |
| Actual result | What actually happened |
| Execution evidence | Response payload, SSE chunk, UI output, command output, screenshot |
| Service evidence | Caller log and downstream service log if applicable |
| Persistence evidence | Database row, JSONL record, message, object metadata, or file output |
| Readback evidence | Query API result, admin panel query, read endpoint result, or DB query output |
| Final judgment | Pass / Fail / Blocked |
| Gap or next action | What is still missing if not fully passed |

If the case involves Agent / LLM / tool calling, also record:

| Field | What to record |
|---|---|
| Prompt or user input | Exact prompt, request body, or user-visible instruction |
| Model / Agent version | Model name, agent build, prompt version, or workflow version |
| Tool trace | Tool calls, request/session id, trace id, or log location |
| Runtime configuration | Env, feature flags, temperature, seed, retry policy, permissions |
| Code or config path | Relevant source/config paths inspected during root-cause tracing |
| Determinism note | Whether the behavior is deterministic or needs repeated sampling |

## Evidence expectations by scenario

### 1. Live API or service flow

Prefer this stack of evidence:

- request payload or command
- immediate response or streamed event
- caller-side log
- callee/service log
- DB or persisted record
- readback query result

### 2. UI or frontend flow

Prefer this stack of evidence:

- exact UI path and input
- visible result or screenshot
- browser/network evidence if needed
- backend log
- persistence or readback evidence if the claim includes saved state

### 3. Background job or worker flow

Prefer this stack of evidence:

- initial queued or retrying state
- worker log proving pickup
- downstream effect log
- final persisted state
- absence of retry residue if that matters

## Pass / fail rules

- `Pass`: all success-definition conditions are satisfied with evidence.
- `Fail`: a success-definition condition is disproven by evidence.
- `Blocked`: the case could not be executed because a prerequisite was missing or invalid.

Do not mark a case as `Pass` when only the first hop succeeded. If the success definition includes persistence or readback, those must also be proven.

When Agent analysis is used, separate:

- verified facts: direct observations from output, logs, persisted state, readback, or source
- root-cause leads: plausible explanations that still need confirmation
- verified RCA: root cause confirmed by source inspection, reproduction, or targeted validation
- open questions: checks still needed before a reviewer can trust the conclusion

## Turning manual tests into automation

After a manual case is stable, consider converting it into automation if:

- the case will be repeated
- the inputs can be controlled
- the evidence can be collected automatically
- the same judgment can be made deterministically

When converting, preserve the same identifiers and evidence chain used in the manual case.

After a manual case is executed, immediately update the current-state test report with:

- the plan-point status
- the exact trigger or command
- the observed result
- the direct evidence source
