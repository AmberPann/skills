---
name: query-agent-context
description: Trace a Git commit to the exact local agent conversation that produced it. Use when resuming historical investigation, explaining why a commit changed, reviewing agent-authored code, tracing regressions, or locating the full Codex, Claude, or Cursor conversation behind a commit.
---

# Query Agent Context

Use the local `agent-context` CLI as the evidence source. The index links a
commit to one or more exact provider sessions; it does not infer links from
repository or timestamp proximity.

## Workflow

1. Query the relevant commit first:

   ```bash
   agent-context context HEAD --repo . --json
   ```

2. Preserve each `session_ref`, transcript path, and `anchor.tool_use_id` in
   the result. Multiple sessions may be valid for one commit.

3. Read only the transcript records around the anchor before expanding to the
   full conversation. Raw transcripts can include bootstrap instructions and
   unrelated tool events.

4. Resolve a session reference when the path is absent or stale:

   ```bash
   agent-context session codex:SESSION_ID --json
   ```

5. State the commit SHA and `session_ref` when using this evidence in an
   explanation. Report an unavailable transcript as unavailable; do not infer
   its content from other sessions.
