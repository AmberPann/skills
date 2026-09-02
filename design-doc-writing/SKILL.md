---
name: design-doc-writing
description: Write and revise architecture, design, ADR, RFC, or other persistent technical documentation so it is self-contained for future readers. Use when Codex creates or edits long-lived docs, especially design documents, interface definitions, architecture proposals, decision records, or implementation plans.
---

# Design Doc Writing

Use this skill when writing persistent technical documentation, not transient chat answers.

## Reader Model

Write for a future reader who did not participate in the conversation.

- Make the document self-contained.
- Introduce concepts before relying on them.
- Avoid references to the discussion process unless the process itself is part of the artifact.
- Do not add explanations whose only purpose is to answer a local conversational objection.

## Writing Rules

Prefer positive, direct definitions.

- Good: `NodeAttr` is the attribute structure returned by `Stat`.
- Avoid: `NodeAttr` is used so we do not confuse it with `Stat`.

Avoid exclusion-style phrasing unless the contrast is necessary and fully explained.

- Good: gRPC is the internal service interface. HTTP is the external and debugging interface.
- Avoid: The interface is gRPC/HTTP, not FUSE/NFS.

Avoid sudden comparison targets.

- If a concept appears only because it was discussed earlier, either remove it or introduce why it matters.
- If a rejected alternative matters, move it into a "Alternatives Considered" or ADR-style section with context.

Turn local naming debates into general conventions.

- Good: Operation names use verbs. Result structures use nouns.
- Avoid: We call the operation `Stat` and the result `NodeAttr` to avoid mixing names.

Define before explaining tradeoffs.

- First state what the design is.
- Then describe why it works.
- Then list tradeoffs, risks, and alternatives if they help the reader.

## Structure Guidance

For architecture/design docs, prefer this order:

1. Context and problem
2. Goals and non-goals
3. Proposed design
4. Interface or data model
5. Operational behavior
6. Tradeoffs and alternatives
7. Open questions and phased plan

Use "non-goals" only when it prevents real scope confusion. Do not use it as a dumping ground for conversational rejections.

## Review Checklist

Before finishing a persistent document, check:

- A reader can understand the document without reading the chat.
- Terms are defined before use.
- Headings describe stable concepts, not the order of conversation.
- Explanations are not defensive or patch-like.
- Comparisons include enough context to be meaningful.
- Business-specific concepts are separated from reusable/interface-level concepts.
- Naming choices are expressed as conventions, not as responses to one-off objections.

