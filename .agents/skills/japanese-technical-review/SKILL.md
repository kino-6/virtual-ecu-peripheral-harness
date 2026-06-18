---
name: japanese-technical-review
description: Project-local workflow for writing strict, low-noise Japanese technical review comments. Use when reviewing MBD artifacts, specifications, generated code, reports, documentation, or when the user asks to review in Japanese. Emphasizes evidence-first findings, clear reject reasons, limited uncertainty, reader load control, and no LLM-like filler.
---

# Japanese Technical Review

Use this skill when writing Japanese review comments for engineering artifacts.
It is inspired by the linked Japanese technical-writing gist, but adapted for
this repository's MBD review workflow.

Reference gist:
https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d

## Review Comment Shape

Write findings in this order:

1. 判定: `Reject`, `Needs work`, `Accept with notes`, or `OK`.
2. 根拠: file, line/section, requirement ID, scenario, report, or generated
   artifact.
3. 影響: why this blocks review, traceability, MBD handoff, harness evidence, or
   generated-code confidence.
4. 修正条件: what must change before the artifact can pass.

Prefer concrete nouns over broad labels. For example, write "SYS-008の復帰条件"
instead of "安全性まわり".

## Japanese Style

- Keep one topic per paragraph.
- Put the paragraph's point in the first sentence.
- Do not hide the finding behind praise or cushioning.
- Avoid vague summaries such as "全体的に良いが" or "改善の余地がある".
- Keep uncertainty only when evidence is incomplete. Say what evidence is
  missing.
- Use bullet lists for independent findings.
- Use code blocks for snippets, generated text, commands, and logs.
- Do not use dramatic wording, motivational phrasing, or empty LLM filler.

## MBD Review Use

When reviewing MBD artifacts, combine this skill with
`mbd-review-quality-gate`.

Each Japanese finding should identify at least one of:

- requirement/spec mismatch
- broad or decorative trace
- unclear state/control behavior
- unclear interface or data flow
- missing scenario evidence
- preview-only assumption presented as accepted behavior
- generated artifact edited or reviewed as source

## Output Gate

Before finalizing, remove any sentence that does not change the reviewer's next
action. If the review would still leave the developer asking "何を直せばいいの",
rewrite it.
